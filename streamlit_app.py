"""Streamlit UI for HR Bot."""

import streamlit as st
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from aye_finance_hr_bot_v2.flows.hr_bot_flow import HRBotFlow

# Page config
st.set_page_config(
    page_title="Aye Finance HR Bot",
    page_icon="🤖",
    layout="centered"
)

# Header
st.title("🤖 Aye Finance HR Bot v2.0")
st.caption("Your AI-powered HR Assistant - Ask in English or Hinglish!")

# Initialize session state
if 'flow' not in st.session_state:
    st.session_state.flow = HRBotFlow()

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'employee_id' not in st.session_state:
    st.session_state.employee_id = None

if 'employee_email' not in st.session_state:
    st.session_state.employee_email = None

# Sidebar
with st.sidebar:
    st.header("👤 Employee Information")
    
    emp_id = st.text_input(
        "Employee ID", 
        value=st.session_state.employee_id or "",
        placeholder="e.g., EMP12345",
        help="Your unique employee identifier"
    )
    
    emp_email = st.text_input(
        "Official Email", 
        value=st.session_state.employee_email or "",
        placeholder="e.g., john@ayefinance.com",
        help="Your registered email for detailed information"
    )
    
    if st.button("💾 Save Information", use_container_width=True):
        st.session_state.employee_id = emp_id
        st.session_state.employee_email = emp_email
        
        # Update Flow state
        st.session_state.flow.state.employee_id = emp_id
        st.session_state.flow.state.employee_email = emp_email
        
        st.success("✅ Information saved!")
    
    st.markdown("---")
    
    # Show if credentials are saved
    if st.session_state.flow.state.employee_id:
        st.success(f"✅ Logged in as: {st.session_state.flow.state.employee_id}")
    
    st.markdown("---")
    
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.flow = HRBotFlow()
        st.rerun()
    
    st.markdown("---")
    st.caption("Powered by CrewAI Flows & LightRAG")

# Instructions
with st.expander("ℹ️ How to use"):
    st.markdown("""
    **What I can help with:**
    - 💰 Salary & Payslip information
    - 🏥 Medical Insurance & ESIC
    - 🌴 Leave Balance & Policies
    
    **Tips:**
    - Ask in English or Hinglish
    - You can ask multiple questions at once
    - Say "send me complete details" for email with attachments
    - Your Employee ID is saved for the conversation
    
    **Examples:**
    - "What is my current salary?"
    - "Mera leave balance kitna hai?"
    - "Send me my complete payslip"
    - "Medical card kaha se milega?"
    """)

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask your HR question..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get bot response
    with st.chat_message("assistant"):
        with st.spinner("🤔 Thinking..."):
            try:
                # Set current query in Flow state
                # Employee ID/Email will persist automatically via @persist decorator
                st.session_state.flow.state.employee_query = prompt
                
                # Run Flow (state persists automatically)
                result = st.session_state.flow.kickoff()
                
                response = str(result)
                
                # Check if Flow is asking for employee info
                if "please provide" in response.lower() and "employee id" in response.lower():
                    response += "\n\n💡 **Tip**: You can save your Employee ID in the sidebar to avoid entering it every time!"
                
                st.markdown(response)
                
            except Exception as e:
                response = f"""
❌ **Oops! Something went wrong.**

I encountered an error while processing your request. 

**What you can do:**
- Try rephrasing your question
- Contact HR directly at hr@ayefinance.com
- Check the employee portal

**Error details**: {str(e)}
"""
                st.error(response)
    
    # Add bot response to history
    st.session_state.messages.append({"role": "assistant", "content": response})
