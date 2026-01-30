"""Session state model for HR Bot Flow."""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
import uuid



class SessionState(BaseModel):
    """Structured state for Flow persistence with conversation history."""
    
    # Conversation tracking
    flow_id: str = Field(
        default="",
        description="Unique conversation identifier for flow resumption"
    )
    user_id: str = Field(
        default="123",
        description="Unique user identifier for external memory storage"
    )
    current_message: str = Field(
        default="",
        description="Current user message"
    )
    conversation_history: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Full conversation history for context"
    )
    
    # Core fields for persistence
    employee_id: Optional[str] = Field(
        default=None,
        description="Employee ID (e.g., EMP12345, AYE12345)"
    )
    employee_email: Optional[str] = Field(
        default=None,
        description="Employee official email"
    )

    
    # Processing fields (reset each query)
    classification: Optional[Dict] = Field(
        default=None,
        description="Latest intent classification result"
    )
    specialist_responses: Dict[str, str] = Field(
        default_factory=dict,
        description="Responses from specialist agents"
    )
    final_response: Optional[str] = Field(
        default=None,
        description="Final synthesized response"
    )
    
    # Optional fields for future features
    main_ticket_id: Optional[str] = Field(
        default=None,
        description="Main ticket ID for this conversation"
    )
    email_sent: bool = Field(
        default=False,
        description="Whether detailed email was sent"
    )
    email_topics: List[str] = Field(
        default_factory=list,
        description="Topics included in email"
    )
    escalated: bool = Field(
        default=False,
        description="Whether query was escalated to HR"
    )
    escalation_reason: Optional[str] = Field(
        default=None,
        description="Reason for escalation"
    )
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                # "employee_id": "AYE12345",
                # "employee_email": "john@ayefinance.com",
                "employee_query": "What is my salary?"
            }
        }
