"""HR Bot Flow - Main orchestration logic."""

from crewai.flow.flow import Flow, start, listen, router, or_
from crewai.flow.persistence import persist
from crewai import Agent, Task, Crew
from typing import Dict, Any
import uuid
import json
import re
import threading

from aye_finance_hr_bot_v2.models.session_state import SessionState
from aye_finance_hr_bot_v2.models.intent import IntentClassification
from aye_finance_hr_bot_v2.agents.agent_factory import (
    create_session_manager,
    create_salary_specialist,
    create_medical_specialist,
    create_leave_specialist,
    create_response_synthesizer,
    create_handoff_specialist
)
from aye_finance_hr_bot_v2.tools.salary_lightrag_tool import SalaryLightRAGTool
from aye_finance_hr_bot_v2.tools.medical_lightrag_tool import MedicalLightRAGTool
from aye_finance_hr_bot_v2.tools.leave_lightrag_tool import LeaveLightRAGTool
from aye_finance_hr_bot_v2.tools.esic_lightrag_tool import EsicLightRagTool
from aye_finance_hr_bot_v2.tools.ticket_creation_tool import TicketCreationTool
from aye_finance_hr_bot_v2.tools.email_sending_tool import EmailSendingTool


@persist()  
class HRBotFlow(Flow[SessionState]):
    """Main HR Bot Flow with conditional routing and persistent state."""

    
    @start()
    def validate_session(self):
        """Step 1: Validate session and extract employee info."""
        # Get current query directly from state (set by Streamlit)
        employee_query = self.state.employee_query or ''
        
        print(f"🔍 Validating session for query: {employee_query}")
        print(f"📊 Current state - Employee ID: {self.state.employee_id}, Email: {self.state.employee_email}")
        
        # If missing employee info, try to extract or ask
        if not self.state.employee_id or not self.state.employee_email:
            session_agent = create_session_manager()
            session_task = Task(
                description=f"""
                Check if Employee ID and Email are available.
                Current state:
                - Employee ID: {self.state.employee_id or 'MISSING'}
                - Employee Email: {self.state.employee_email or 'MISSING'}
                
                Query: {employee_query}
                
                If missing:
                1. Try to extract from query (look for patterns like EMP12345, AYE12345, email@domain.com)
                2. If found, return them in format: "FOUND: employee_id=VALUE, employee_email=VALUE"
                3. If not found, ask user politely ONCE
                
                If found, confirm and proceed.
                """,
                expected_output="Employee ID and Email status with extraction or request",
                agent=session_agent
            )
            
            crew = Crew(agents=[session_agent], tasks=[session_task], verbose=False)
            result = crew.kickoff()
            result_str = str(result)
            
            # Try to parse extracted values
            if "FOUND:" in result_str:
                # Extract employee_id and employee_email from response
                import re
                id_match = re.search(r'employee_id=([A-Z0-9]+)', result_str)
                email_match = re.search(r'employee_email=([\w\.-]+@[\w\.-]+)', result_str)
                
                if id_match:
                    self.state.employee_id = id_match.group(1)
                    print(f"✅ Extracted Employee ID: {self.state.employee_id}")
                if email_match:
                    self.state.employee_email = email_match.group(1)
                    print(f"✅ Extracted Employee Email: {self.state.employee_email}")
            
            # Check if we still need to ask user
            if not self.state.employee_id or not self.state.employee_email:
                if "please provide" in result_str.lower() or "need" in result_str.lower():
                    return {
                        "status": "need_info",
                        "message": result_str,
                        "requires_user_input": True
                    }
        
        
        # Session validated, proceed to classification
        return {
            "status": "validated",
            "employee_query": employee_query,
            "employee_id": self.state.employee_id,
            "employee_email": self.state.employee_email
        }
    
    @router(validate_session)
    def classify_and_route(self, validation_result: Dict[str, Any]):
        """Router: Classify intent with LLM and route to appropriate handler."""
        
        # If validation failed, return message
        if validation_result.get("status") == "need_info":
            self.state.final_response = validation_result["message"]
            return "respond_to_user"
        
        employee_query = validation_result["employee_query"]
        
        print(f"🎯 Classifying and routing: {employee_query}")
        
        # Direct LLM classification
        from crewai import LLM
        
        llm = LLM(
            model="gpt-4o-mini",
            temperature=0.3,
            response_format=IntentClassification
        )
        
        prompt = f"""
            Classify this employee query and determine routing.

            **HR Queries (is_hr_query=true):**
            - salary: Payslip, CTC, deductions, salary components
            - medical: medical card, health coverage
            - leave: Leave balance, vacation policies, leave types
            - esic: ESIC card, registration, contributions
            - handoff: Complex HR issues, policy questions, complaints, benefits not covered above, general HR queries

            **General Conversation (is_hr_query=false):**
            - greeting_only: "hi", "hello", "namaste"
            - credential_only: Only Employee ID/Email provided
            - general_conversation: "thank you", "how are you", "bye"
            - out_of_scope: Weather, news, non-HR topics

            Query: "{employee_query}"

            **Conversation Responses:**
            - greeting/credential: "Hello! I have your details. How can I help you today?\n\n**I can assist you with:**\n• 💰 Salary & Payslip information\n• 🏥 Medical Insurance & ESIC\n• 🌴 Leave Balance & Policies\n\n**Please ask your question!**"
            - thank you: "You're welcome! Let me know if you need anything else."
            - bye: "Goodbye! Feel free to reach out anytime you need help."
            - out_of_scope: "I'm an HR assistant and can only help with salary, medical, leave, and ESIC queries."

            Also detect if user requests detailed email (keywords: "complete", "detailed", "full", "send me", "email me").
            Support Hinglish (mix of Hindi and English).
            """
        
        # Classify with LLM
        classification = llm.call(prompt)
        
        print(f"✅ Classification: {classification}")

        # Clear previous query data for new query
        self.state.specialist_responses = {}
        self.state.main_ticket_id = None

        # Store in state
        self.state.classification = classification.model_dump()
        self.state.employee_query = employee_query
        self.state.employee_id = validation_result["employee_id"]
        self.state.employee_email = validation_result["employee_email"]
        
        # ROUTE based on classification
        if not classification.is_hr_query:
            # General conversation - return response directly
            print(f"💬 General conversation detected")
            self.state.final_response = classification.conversation_response
            return "respond_to_user"
        
        # HR query - route to specialists
        intents = classification.intents
        print(f"🔀 Routing to specialists: {intents}")
        
        if len(intents) == 1:
            if "salary" in intents:
                return "process_salary"
            elif "medical" in intents or "esic" in intents:
                return "process_medical"
            elif "leave" in intents:
                return "process_leave"
            elif "handoff" in intents:
                return "process_handoff"
        else:
            return "process_multiple"
        
        # Default fallback to handoff for unknown
        return "process_handoff"
    
    def _compose_detailed_email(self, topics: list[str], responses: Dict[str, str], ticket_id: str = None) -> str:
        """Compose detailed email with specialist responses and ticket ID."""
        
        # Special template for handoff queries
        if "handoff" in topics:
            email_body = f"""Dear Employee,

            Thank you for reaching out to the HR Bot regarding your query.

            YOUR QUERY


            {self.state.employee_query}


            Your query has been forwarded to our HR team for personalized assistance. 
            A support specialist will review your request and respond within 24-48 business hours.

            Support Ticket ID: {ticket_id if ticket_id else 'Pending'}

            You can reference this ticket ID in any follow-up communications.

            We appreciate your patience and will get back to you soon.

            Best regards,
            HR Bot - Aye Finance
            """
            return email_body
        
        email_body = f"""Dear Employee,

            Thank you for your query. Below are the detailed responses:

            """
        
        # Include ALL responses (not filtered by topics)
        for topic, response in responses.items():
            email_body += f"""
            {topic.upper()} INFORMATION

            {response}

            """
        
        # Add ticket ID if available
        if ticket_id:
            email_body += f"""

            Ticket ID: {ticket_id}

            """
        
        email_body += f"""
            If you have any further questions, please feel free to ask.

            Best regards,
            HR Bot - Aye Finance
            """
        
        return email_body
    
    def _send_email_background(selfself, email: str, subject: str, message: str):
        """Send email in background thread to avoid blocking response."""
        
        def send_email():
            try:
                
                print(f"📧 [Background] Sending email to {email}...")
                
                email_tool = EmailSendingTool()
                result = email_tool._run(
                    email=email,
                    subject=subject,
                    message=message
                )
                
                print(f"📧 [Background] Email result: {result}")
                
            except Exception as e:
                print(f"❌ [Background] Email sending failed: {str(e)}")
        
        # Start background thread (daemon=True means it dies with main program)
        thread = threading.Thread(target=send_email, daemon=True)
        thread.start()
        
        print(f"📧 Email sending started in background for {email}")
    
    @listen("process_salary")
    def handle_salary_query(self, classification_result: Dict[str, Any]):
        """Process salary queries."""
        print("💰 Processing salary query")
        
        salary_agent = create_salary_specialist([SalaryLightRAGTool()])
        task = Task(
            description=f"""
            Answer this salary query: {classification_result['employee_query']}
            Employee ID: {classification_result['employee_id']}
            
            Use Salary LightRAG Tool to fetch accurate data.
            Provide clear, conversational response about salary, payslip, components, deductions, etc.
            """,
            expected_output="Salary information response",
            agent=salary_agent
        )
        
        crew = Crew(agents=[salary_agent], tasks=[task], verbose=True)
        result = crew.kickoff()
        
        self.state.specialist_responses["salary"] = str(result)
        
        # Create ticket via Chapter Apps API
        
        ticket_tool = TicketCreationTool()
        ticket_result = ticket_tool._run(
            title=f"Salary Query: {self.state.employee_query[:50]}",
            reporter_email=self.state.employee_email,
            reporter_employee_id=self.state.employee_id,
            reporter_user_id=self.state.employee_id,
            priority="medium"
        )
        
        # Extract ticket ID from response
        ticket_id = None
        try:
            json_match = re.search(r'\{.*\}', ticket_result, re.DOTALL)
            if json_match:
                response_json = json.loads(json_match.group(0))
                if 'response_data' in response_json and 'data' in response_json['response_data']:
                    ticket_id = response_json['response_data']['data'].get('id')
        except:
            pass
        if ticket_id:
            self.state.main_ticket_id = ticket_id
            print(f"📋 Ticket ID extracted: {ticket_id}")
        
        return str(result)
    
    @listen("process_medical")
    def handle_medical_query(self, classification_result: Dict[str, Any]):
        """Process medical/ESIC queries."""
        print("🏥 Processing medical/ESIC query")
        
        medical_agent = create_medical_specialist([MedicalLightRAGTool(), EsicLightRagTool()])
        task = Task(
            description=f"""
            Answer this medical/insurance query: {classification_result['employee_query']}
            Employee ID: {classification_result['employee_id']}
            
            Use Medical and ESIC LightRAG Tools to fetch accurate data.
            Provide clear, conversational response about medical insurance, ESIC, card status, coverage, etc.
            """,
            expected_output="Medical/ESIC information response",
            agent=medical_agent
        )
        
        crew = Crew(agents=[medical_agent], tasks=[task], verbose=True)
        result = crew.kickoff()
        
        self.state.specialist_responses["medical"] = str(result)
        
        # Create ticket via Chapter Apps API
        
        ticket_tool = TicketCreationTool()
        ticket_result = ticket_tool._run(
            title=f"Medical/ESIC Query: {self.state.employee_query[:50]}",
            reporter_email=self.state.employee_email,
            reporter_employee_id=self.state.employee_id,
            reporter_user_id=self.state.employee_id,
            priority="medium"
        )
        
        # Extract ticket ID from response
        ticket_id = None
        try:
            json_match = re.search(r'\{.*\}', ticket_result, re.DOTALL)
            if json_match:
                response_json = json.loads(json_match.group(0))
                if 'response_data' in response_json and 'data' in response_json['response_data']:
                    ticket_id = response_json['response_data']['data'].get('id')
        except:
            pass
        if ticket_id:
            self.state.main_ticket_id = ticket_id
            print(f"📋 Ticket ID extracted: {ticket_id}")
        
        return str(result)    
    @listen("process_leave")
    def handle_leave_query(self, classification_result: Dict[str, Any]):
        """Process leave queries."""
        print("🌴 Processing leave query")
        
        leave_agent = create_leave_specialist([LeaveLightRAGTool()])
        task = Task(
            description=f"""
            Answer this leave query: {classification_result['employee_query']}
            Employee ID: {classification_result['employee_id']}
            
            Use Leave LightRAG Tool to fetch accurate data.
            Provide clear, conversational response about leave balance, types, rules, etc.
            """,
            expected_output="Leave information response",
            agent=leave_agent
        )
        
        crew = Crew(agents=[leave_agent], tasks=[task], verbose=True)
        result = crew.kickoff()
        
        self.state.specialist_responses["leave"] = str(result)
        
        # Create ticket via Chapter Apps API
        
        ticket_tool = TicketCreationTool()
        ticket_result = ticket_tool._run(
            title=f"Leave Query: {self.state.employee_query[:50]}",
            reporter_email=self.state.employee_email,
            reporter_employee_id=self.state.employee_id,
            reporter_user_id=self.state.employee_id,
            priority="medium"
        )
        
        # Extract ticket ID from response
        ticket_id = None
        try:
            json_match = re.search(r'\{.*\}', ticket_result, re.DOTALL)
            if json_match:
                response_json = json.loads(json_match.group(0))
                if 'response_data' in response_json and 'data' in response_json['response_data']:
                    ticket_id = response_json['response_data']['data'].get('id')
        except:
            pass
        if ticket_id:
            self.state.main_ticket_id = ticket_id
            print(f"📋 Ticket ID extracted: {ticket_id}")
        
        return str(result)
    
    @listen("process_handoff")
    def handle_handoff_query(self, classification_result: Dict[str, Any]):
        """Handle queries requiring HR team escalation."""
        print("🤝 Processing handoff query - escalating to HR team")
        
        # Create handoff agent
        handoff_agent = create_handoff_specialist()
        task = Task(
            description=f"""
            Respond to this query that requires HR team attention:
            Query: {classification_result['employee_query']}
            Employee ID: {classification_result['employee_id']}
            
            Provide a friendly response that:
            1. Acknowledges their query
            2. Explains it's been forwarded to the HR team
            3. Mentions they'll receive email confirmation
            4. Thanks them for their patience
            
            Keep it warm, professional, and concise.
            """,
            expected_output="Friendly escalation response",
            agent=handoff_agent
        )
        
        crew = Crew(agents=[handoff_agent], tasks=[task], verbose=True)
        result = crew.kickoff()
        
        self.state.specialist_responses["handoff"] = str(result)
        
        # Create ticket via Chapter Apps API
        ticket_tool = TicketCreationTool()
        ticket_result = ticket_tool._run(
            title=f"Handoff Query: {self.state.employee_query[:50]}",
            reporter_email=self.state.employee_email,
            reporter_employee_id=self.state.employee_id,
            reporter_user_id=self.state.employee_id,
            priority="high"  # Handoff queries are higher priority
        )
        
        # Extract ticket ID
        ticket_id = None
        try:
            json_match = re.search(r'\{.*\}', ticket_result, re.DOTALL)
            if json_match:
                response_json = json.loads(json_match.group(0))
                if 'response_data' in response_json and 'data' in response_json['response_data']:
                    ticket_id = response_json['response_data']['data'].get('id')
        except:
            pass
        
        if ticket_id:
            self.state.main_ticket_id = ticket_id
            print(f"📋 Handoff Ticket ID: {ticket_id}")
        
        # Always send email for handoff queries
        self.state.classification['requires_detailed_email'] = True
        self.state.classification['email_topics'] = ['handoff']
        
        return str(result)
    
    @listen("process_multiple")
    def handle_multiple_intents(self, classification_result: Dict[str, Any]):
        """Process multiple intents in parallel."""
        print("🔄 Processing multiple intents")
        
        classification: IntentClassification = classification_result["classification"]
        responses = {}
        
        # Process each intent
        for intent in classification.intents:
            if intent == "salary":
                result = self.handle_salary_query(classification_result)
                responses["salary"] = result
            elif intent in ["medical", "esic"]:
                result = self.handle_medical_query(classification_result)
                responses["medical"] = result
            elif intent == "leave":
                result = self.handle_leave_query(classification_result)
                responses["leave"] = result
        
        self.state.specialist_responses = responses
        
        # Create ticket via Chapter Apps API for multiple intents
        
        ticket_tool = TicketCreationTool()
        ticket_result = ticket_tool._run(
            title=f"Multiple Queries: {self.state.employee_query[:50]}",
            reporter_email=self.state.employee_email,
            reporter_employee_id=self.state.employee_id,
            reporter_user_id=self.state.employee_id,
            priority="high"  # Higher priority for multiple queries
        )
        
        # Extract ticket ID from response
        ticket_id = None
        try:
            json_match = re.search(r'\{.*\}', ticket_result, re.DOTALL)
            if json_match:
                response_json = json.loads(json_match.group(0))
                if 'response_data' in response_json and 'data' in response_json['response_data']:
                    ticket_id = response_json['response_data']['data'].get('id')
        except:
            pass
        if ticket_id:
            self.state.main_ticket_id = ticket_id
            print(f"📋 Ticket ID extracted: {ticket_id}")
        
        return "Multiple queries processed"
    
    @listen(or_("process_salary", "process_medical", "process_leave", "process_handoff", "process_multiple"))
    def synthesize_response(self, specialist_result: Dict[str, Any]):
        """Step 4: Synthesize final response."""
        print("📝 Synthesizing final response")
        
        # Get specialist responses from state
        specialist_responses = self.state.specialist_responses
        
        # If single specialist
        if len(specialist_responses) == 1:
            final_response = list(specialist_responses.values())[0]
        else:
            # Multiple specialists - synthesize
            synthesizer_agent = create_response_synthesizer()
            task = Task(
                description=f"""
                Synthesize these specialist responses into a unified answer:
                {specialist_responses}
                
                Create a conversational, coherent response that addresses all aspects.
                Maintain natural flow and be helpful.
                DO NOT format as email - this is a direct chat response.
                """,
                expected_output="Unified conversational response",
                agent=synthesizer_agent
            )
            
            crew = Crew(agents=[synthesizer_agent], tasks=[task], verbose=False)
            result = crew.kickoff()
            final_response = str(result)
        
        # Check if email was requested
        classification = IntentClassification(**self.state.classification)
        print('classification :',classification)
        
        if classification.requires_detailed_email:
            print("📧 Email requested - preparing to send in background...")
            
            # Compose email content with ticket ID
            email_content = self._compose_detailed_email(
                topics=classification.email_topics,
                responses=self.state.specialist_responses,
                ticket_id=self.state.main_ticket_id
            )
            
            # Send email in BACKGROUND (non-blocking)
            self._send_email_background(
                email=self.state.employee_email,
                subject=f"Your HR Query Details - {', '.join(classification.email_topics).title()}",
                message=email_content
            )
            
            self.state.email_sent = True
            self.state.email_topics = classification.email_topics
            
            # Add confirmation to response
            final_response += f"\n\n---\n\n✅ **Detailed information is being sent to:** {self.state.employee_email}"
        
        self.state.final_response = final_response
        # Don't return dict - let respond_to_user handle final output
        return final_response
    
    @listen(validate_session)
    @listen(synthesize_response)
    def respond_to_user(self, result: Dict[str, Any]):
        """Final step: Return response to user."""
        # If validation failed, return validation message
        if result.get("status") == "need_info":
            return result["message"]
        
        # Otherwise return final response
        return self.state.final_response or "I'm sorry, I couldn't process your request."
