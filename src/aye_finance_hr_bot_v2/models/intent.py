"""Intent classification model for HR Bot."""

from pydantic import BaseModel, Field
from typing import List, Optional


class IntentClassification(BaseModel):
    """Intent classification result from query analysis."""
    
    intents: List[str] = Field(
        description="""List of detected intents:
        - salary, medical, leave, esic (HR queries)
        - greeting_only, credential_only, general_conversation, out_of_scope (non-HR)"""
    )
    is_hr_query: bool = Field(
        default=True,
        description="True if HR query needing specialist, False if conversation"
    )
    conversation_response: Optional[str] = Field(
        default=None,
        description="Direct response for non-HR queries (greeting, thank you, etc.)"
    )
    requires_detailed_email: bool = Field(
        default=True,
        description="Whether user requested detailed email"
    )
    email_topics: List[str] = Field(
        default_factory=list,
        description="Topics for email (payslip, medical_card, esic_card)"
    )
    query_language: str = Field(
        default="english",
        description="Detected language (english, hinglish, hindi)"
    )
    requires_employee_id: bool = Field(
        default=False,
        description="Whether Employee ID is required but missing"
    )
    requires_employee_email: bool = Field(
        default=False,
        description="Whether Employee Email is required but missing"
    )
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "intents": ["salary"],
                "requires_detailed_email": True,
                "email_topics": ["payslip","medical_card","esic_card"],
                "query_language": "english",
                "confidence": 0.95,
                "requires_employee_id": False,
                "requires_employee_email": False
            }
        }
