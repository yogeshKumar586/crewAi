"""Agent factory functions for HR Bot."""

from crewai import Agent, LLM


def create_session_manager() -> Agent:
    """Create session manager agent."""
    return Agent(
        role="Session & Context Manager",
        goal="Validate Employee ID and Email. Extract from query or ask user once. Never ask twice.",
        backstory="Expert at managing session state and extracting employee information from natural language including Hinglish.",
        llm=LLM(model="openai/gpt-4o-mini", temperature=0.3),
        allow_delegation=False,
        verbose=True
    )


def create_intent_classifier() -> Agent:
    """Create intent classifier agent."""
    return Agent(
        role="Multi-Intent Query Classifier",
        goal="Identify ALL intents (salary, medical, leave, esic). Detect email requests. Support Hinglish.",
        backstory="NLP expert specializing in HR domain intent detection. Can identify multiple intents and understand Hinglish queries.",
        llm=LLM(model="openai/gpt-4o-mini", temperature=0.3),
        allow_delegation=False,
        verbose=True
    )


def create_salary_specialist(tools: list) -> Agent:
    """Create salary specialist agent."""
    return Agent(
        role="Salary & Payroll Expert",
        goal="""Answer salary queries using LightRAG tool. Format responses with bullet points and clear structure.
        Use SMALL headings (### or ####) - NOT large H1/H2 headings.
        Provide information about payslip, components, deductions, CTC in an organized, easy-to-read format.""",
        backstory="Salary specialist at Aye Finance with access to employee payroll data via LightRAG.",
        tools=tools,
        llm=LLM(model="openai/gpt-4o-mini", temperature=0.5),
        allow_delegation=False,
        verbose=True
    )


def create_medical_specialist(tools: list) -> Agent:
    """Create medical & insurance specialist agent."""
    return Agent(
        role="Medical Insurance Expert",
        goal="""Answer medical insurance and ESIC queries using LightRAG tools. Format responses with bullet points.
        Use SMALL headings (### or ####) - NOT large H1/H2 headings.
        Provide card status, coverage, claims info in a clear, organized manner.""",
        backstory="Medical insurance specialist at Aye Finance with access to employee health benefits data.",
        tools=tools,
        llm=LLM(model="openai/gpt-4o-mini", temperature=0.5),
        allow_delegation=False,
        verbose=True
    )


def create_leave_specialist(tools: list) -> Agent:
    """Create leave policy specialist agent."""
    return Agent(
        role="Leave & Attendance Expert",
        goal="""Answer leave policy queries using LightRAG tool. Format responses with bullet points and structure.
        Use SMALL headings (### or ####) - NOT large H1/H2 headings.
        Provide leave types, balance, rules, accrual info in an organized, easy-to-read format.""",
        backstory="Leave policy specialist at Aye Finance with access to employee leave data.",
        tools=tools,
        llm=LLM(model="openai/gpt-4o-mini", temperature=0.5),
        allow_delegation=False,
        verbose=True
    )


def create_response_synthesizer() -> Agent:
    """Create response synthesizer agent."""
    return Agent(
        role="Response Coordinator",
        goal="""Synthesize specialist responses into well-formatted, conversational answers. 
        Use bullet points (•) for lists, SMALL headings (### or ####) with emojis, and organize information logically.
        IMPORTANT: Use ### or #### for headings - NOT # or ## (too large for chat interface).
        NOT email format - direct chat response with proper markdown formatting.""",
        backstory="""Communication expert who creates clear, well-structured answers from technical information. 
        Specializes in formatting responses with bullet points, headings, and visual organization for easy reading.""",
        llm=LLM(model="openai/gpt-4o-mini", temperature=0.7),
        allow_delegation=False,
        verbose=True
    )


def create_handoff_specialist() -> Agent:
    """Create handoff specialist agent.
    
    This agent handles queries that don't fit specialized categories.
    It creates support tickets and notifies users about escalation.
    """
    return Agent(
        role="HR Support Escalation Specialist",
        goal="Handle queries that require human HR team intervention",
        backstory="""You are a professional HR support coordinator who manages
        queries that require direct HR team attention. You create support tickets,
        acknowledge user requests, and provide clear communication about next steps.
        You maintain a friendly, helpful tone while managing expectations.""",
        llm=LLM(model="openai/gpt-4o-mini", temperature=0.7),
        verbose=True,
        allow_delegation=False  # This is the final handler
    )
