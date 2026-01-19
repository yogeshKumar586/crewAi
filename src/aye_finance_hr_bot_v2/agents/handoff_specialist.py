"""Handoff specialist agent for escalated queries."""

from crewai import Agent


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
        verbose=True,
        allow_delegation=False  # This is the final handler
    )
