"""Ticket models for HR Bot ticketing system."""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid


class SubTicket(BaseModel):
    """Sub-ticket for individual queries within a conversation."""
    
    sub_ticket_id: str = Field(
        default_factory=lambda: f"SUB-{str(uuid.uuid4())[:8]}",
        description="Unique sub-ticket identifier"
    )
    query_number: int = Field(
        description="Query number in conversation"
    )
    query_text: str = Field(
        description="The actual query text"
    )
    intents: List[str] = Field(
        default_factory=list,
        description="Detected intents for this query"
    )
    specialist_used: str = Field(
        description="Specialist(s) that handled the query"
    )
    response: str = Field(
        description="Response provided to the query"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="When the query was processed (ISO format)"
    )
    resolution_status: str = Field(
        default="resolved",
        description="Status: resolved, escalated, pending"
    )
    
    class Config:
        """Pydantic config."""
        from pydantic import ConfigDict
        model_config = ConfigDict(
            json_encoders={datetime: lambda v: v.isoformat()}
        )
        json_schema_extra = {
            "example": {
                "sub_ticket_id": "SUB-abc12345",
                "query_number": 1,
                "query_text": "What is my salary?",
                "intents": ["salary"],
                "specialist_used": "salary",
                "response": "Your salary details...",
                "resolution_status": "resolved"
            }
        }


class MainTicket(BaseModel):
    """Main ticket for entire conversation."""
    
    main_ticket_id: str = Field(
        default_factory=lambda: f"TICKET-{str(uuid.uuid4())[:8]}",
        description="Unique main ticket identifier"
    )
    conversation_id: str = Field(
        description="Associated conversation ID"
    )
    employee_id: str = Field(
        description="Employee ID"
    )
    employee_email: str = Field(
        description="Employee email"
    )
    created_at: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Ticket creation timestamp (ISO format)"
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Last update timestamp (ISO format)"
    )
    total_queries: int = Field(
        default=0,
        description="Total number of queries in conversation"
    )
    sub_tickets: List[SubTicket] = Field(
        default_factory=list,
        description="List of sub-tickets"
    )
    status: str = Field(
        default="active",
        description="Status: active, closed, escalated"
    )
    escalation_reason: Optional[str] = Field(
        default=None,
        description="Reason for escalation if escalated"
    )
    
    class Config:
        """Pydantic config."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        json_schema_extra = {
            "example": {
                "main_ticket_id": "TICKET-xyz789",
                "conversation_id": "conv-123",
                "employee_id": "EMP12345",
                "employee_email": "john@ayefinance.com",
                "total_queries": 2,
                "status": "active"
            }
        }
