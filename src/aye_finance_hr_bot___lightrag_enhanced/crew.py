import os

from crewai import LLM
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from aye_finance_hr_bot___lightrag_enhanced.tools.email_sending_tool import EmailSendingTool
from aye_finance_hr_bot___lightrag_enhanced.tools.ticket_creation_tool import TicketCreationTool
from aye_finance_hr_bot___lightrag_enhanced.tools.salary_lightrag_tool import SalaryLightRAGTool
from aye_finance_hr_bot___lightrag_enhanced.tools.medical_lightrag_tool import MedicalLightRAGTool
from aye_finance_hr_bot___lightrag_enhanced.tools.leave_lightrag_tool import LeaveLightRAGTool
from aye_finance_hr_bot___lightrag_enhanced.tools.esic_lightrag_tool import EsicLightRagTool




@CrewBase
class AyeFinanceHrBotLightragEnhancedCrew:
    """AyeFinanceHrBotLightragEnhanced crew"""

    
    @agent
    def hr_query_classifier(self) -> Agent:
        
        return Agent(
            config=self.agents_config["hr_query_classifier"],
            
            
            tools=[],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            
            max_execution_time=None,
            llm=LLM(
                model="openai/gpt-4o-mini",
                temperature=0.7,
            ),
            
        )
    
    @agent
    def salary_specialist(self) -> Agent:
        
        return Agent(
            config=self.agents_config["salary_specialist"],
            
            
            tools=[				SalaryLightRAGTool()],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            
            max_execution_time=None,
            llm=LLM(
                model="openai/gpt-4o-mini",
                temperature=0.7,
            ),
            
        )
    
    @agent
    def medical_insurance_specialist(self) -> Agent:
        
        return Agent(
            config=self.agents_config["medical_insurance_specialist"],
            
            
            tools=[				MedicalLightRAGTool()],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            
            max_execution_time=None,
            llm=LLM(
                model="openai/gpt-4o-mini",
                temperature=0.7,
            ),
            
        )
    
    @agent
    def leave_policy_specialist(self) -> Agent:
        
        return Agent(
            config=self.agents_config["leave_policy_specialist"],
            
            
            tools=[				LeaveLightRAGTool()],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            
            max_execution_time=None,
            llm=LLM(
                model="openai/gpt-4o-mini",
                temperature=0.7,
            ),
            
        )
    
    @agent
    def esic_specialist(self) -> Agent:
        
        return Agent(
            config=self.agents_config["esic_specialist"],
            
            
            tools=[				EsicLightRagTool()],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            
            max_execution_time=None,
            llm=LLM(
                model="openai/gpt-4o-mini",
                temperature=0.7,
            ),
            
        )
    
    @agent
    def conditional_email_service_agent(self) -> Agent:
        
        return Agent(
            config=self.agents_config["conditional_email_service_agent"],
            
            
            tools=[				EmailSendingTool()],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            
            max_execution_time=None,
            llm=LLM(
                model="openai/gpt-4o-mini",
                temperature=0.7,
            ),
            
        )
    
    @agent
    def ticket_manager(self) -> Agent:
        
        return Agent(
            config=self.agents_config["ticket_manager"],
            
            
            tools=[				TicketCreationTool()],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            
            max_execution_time=None,
            llm=LLM(
                model="openai/gpt-4o-mini",
                temperature=0.7,
            ),
            
        )
    
    @agent
    def hr_response_synthesizer(self) -> Agent:
        
        return Agent(
            config=self.agents_config["hr_response_synthesizer"],
            
            
            tools=[],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            
            max_execution_time=None,
            llm=LLM(
                model="openai/gpt-4o-mini",
                temperature=0.7,
            ),
            
        )
    

    
    @task
    def route_hr_query(self) -> Task:
        return Task(
            config=self.tasks_config["route_hr_query"],
            markdown=False,
            
            
        )
    
    @task
    def create_support_ticket(self) -> Task:
        return Task(
            config=self.tasks_config["create_support_ticket"],
            markdown=False,
            
            
        )
    
    @task
    def process_salary_queries(self) -> Task:
        return Task(
            config=self.tasks_config["process_salary_queries"],
            markdown=False,
            
            
        )
    
    @task
    def process_medical_insurance_queries(self) -> Task:
        return Task(
            config=self.tasks_config["process_medical_insurance_queries"],
            markdown=False,
            
            
        )
    
    @task
    def process_leave_policy_queries(self) -> Task:
        return Task(
            config=self.tasks_config["process_leave_policy_queries"],
            markdown=False,
            
            
        )
    
    @task
    def process_esic_queries(self) -> Task:
        return Task(
            config=self.tasks_config["process_esic_queries"],
            markdown=False,
            
            
        )
    
    @task
    def conditional_email_service(self) -> Task:
        return Task(
            config=self.tasks_config["conditional_email_service"],
            markdown=False,
            
            
        )
    
    @task
    def log_sub_tickets_and_handle_escalation(self) -> Task:
        return Task(
            config=self.tasks_config["log_sub_tickets_and_handle_escalation"],
            markdown=False,
            
            
        )
    
    @task
    def synthesize_final_hr_response(self) -> Task:
        return Task(
            config=self.tasks_config["synthesize_final_hr_response"],
            markdown=False,
            
            
        )
    

    @crew
    def crew(self) -> Crew:
        """Creates the AyeFinanceHrBotLightragEnhanced crew"""
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            chat_llm=LLM(model="openai/gpt-4o-mini"),
        )

    def _load_response_format(self, name):
        with open(os.path.join(self.base_directory, "config", f"{name}.json")) as f:
            json_schema = json.loads(f.read())

        return SchemaConverter.build(json_schema)
