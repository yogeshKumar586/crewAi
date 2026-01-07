from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
import requests
import json

class TicketCreationInput(BaseModel):
    """Input schema for Ticket Creation Tool."""
    title: str = Field(..., description="The ticket title")
    reporter_email: str = Field(..., description="Employee's email address")
    reporter_employee_id: str = Field(..., description="Employee's ID")
    reporter_user_id: str = Field(..., description="User ID")
    priority: str = Field(default="medium", description="Ticket priority level (default: medium)")

class TicketCreationTool(BaseTool):
    """Tool for creating support tickets via Chapter Apps API."""

    name: str = "Ticket Creation Tool"
    description: str = (
        "Creates support tickets by calling the Chapter Apps ticket API. "
        "Accepts ticket details including title, reporter information, and priority, "
        "then returns the API response with status information."
    )
    args_schema: Type[BaseModel] = TicketCreationInput

    def _run(self, title: str, reporter_email: str, reporter_employee_id: str, 
             reporter_user_id: str, priority: str = "medium") -> str:
        """
        Create a support ticket by making a POST request to the Chapter Apps API.
        
        Args:
            title: The ticket title
            reporter_email: Employee's email address
            reporter_employee_id: Employee's ID
            reporter_user_id: User ID
            priority: Ticket priority level (default: medium)
            
        Returns:
            String containing the API response with status information
        """
        try:
            # API endpoint
            url = "https://api.chapterapps.ai/chapter-agentic/ragapi/tickets/"
            
            # Headers
            headers = {
                "Content-Type": "application/json"
            }
            
            # Payload structure
            payload = {
                "title": title,
                "reporter_email": reporter_email,
                "reporter_employee_id": reporter_employee_id,
                "reporter_user_id": reporter_user_id,
                "priority": priority
            }
            
            # Make the POST request
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            # Prepare the result with status information
            result = {
                "status_code": response.status_code,
                "success": response.status_code in range(200, 300),
                "url": url,
                "payload_sent": payload
            }
            
            # Try to parse JSON response
            try:
                response_data = response.json()
                result["response_data"] = response_data
            except json.JSONDecodeError:
                result["response_text"] = response.text
            
            # Check if request was successful
            if response.status_code in range(200, 300):
                return f"✅ Ticket created successfully!\n" \
                       f"Status Code: {response.status_code}\n" \
                       f"Response: {json.dumps(result, indent=2)}"
            else:
                return f"❌ Failed to create ticket.\n" \
                       f"Status Code: {response.status_code}\n" \
                       f"Error Details: {json.dumps(result, indent=2)}"
                       
        except requests.exceptions.Timeout:
            return "❌ Error: Request timed out after 30 seconds. Please try again or check the API status."
            
        except requests.exceptions.ConnectionError:
            return "❌ Error: Failed to connect to the API. Please check your internet connection and the API endpoint."
            
        except requests.exceptions.RequestException as e:
            return f"❌ Error: Request failed - {str(e)}"
            
        except Exception as e:
            return f"❌ Unexpected error occurred: {str(e)}"