from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
import requests
import json

class EmailSendingToolInput(BaseModel):
    """Input schema for Email Sending Tool."""
    email: str = Field(..., description="Recipient's email address")
    subject: str = Field(..., description="Email subject line")
    message: str = Field(..., description="Email content/body")

class EmailSendingTool(BaseTool):
    """Tool for sending emails by calling the Triveni CRM email API."""

    name: str = "Email Sending Tool"
    description: str = (
        "Sends emails by calling the Triveni CRM email API. "
        "Requires recipient email, subject, and message content. "
        "Returns the API response including status code and any response data."
    )
    args_schema: Type[BaseModel] = EmailSendingToolInput

    def _run(self, email: str, subject: str, message: str) -> str:
        """
        Send an email using the Triveni CRM email API.
        
        Args:
            email: Recipient's email address
            subject: Email subject line
            message: Email content/body
            
        Returns:
            String containing the API response status and data
        """
        try:
            # API endpoint and headers
            url = "https://triveni-crm-backend.chapterapps.ai/api/v1/email/send"
            headers = {
                "Content-Type": "application/json"
            }
            
            # Prepare the payload
            payload = {
                "email": email,
                "subject": subject,
                "message": message
            }
            
            # Make the POST request
            response = requests.post(
                url=url,
                headers=headers,
                json=payload,
                timeout=30  # Add timeout for better error handling
            )
            
            # Parse response
            status_code = response.status_code
            
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                response_data = {"text": response.text}
            
            # Check if request was successful
            if 200 <= status_code < 300:
                return f"Email sent successfully! Status: {status_code}, Response: {json.dumps(response_data, indent=2)}"
            else:
                return f"Email sending failed. Status: {status_code}, Response: {json.dumps(response_data, indent=2)}"
                
        except requests.exceptions.Timeout:
            return "Error: Request timed out. The email API did not respond within 30 seconds."
        except requests.exceptions.ConnectionError:
            return "Error: Could not connect to the email API. Please check your internet connection and try again."
        except requests.exceptions.RequestException as e:
            return f"Error: Request failed with exception: {str(e)}"
        except Exception as e:
            return f"Error: An unexpected error occurred: {str(e)}"