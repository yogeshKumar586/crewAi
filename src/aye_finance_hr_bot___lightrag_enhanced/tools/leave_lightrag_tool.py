from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
import requests
import json

# Environment variable access
try:
    import os
except ImportError:
    pass

class LeaveLightRAGRequest(BaseModel):
    """Input schema for Leave LightRAG Tool."""
    query: str = Field(..., description="The leave-related question from the employee")
    employee_id: str = Field(..., description="The specific employee ID to fetch personalized data for")

class LeaveLightRAGTool(BaseTool):
    """Tool for querying leave policy-related information using LightRAG API.
    
    This tool specializes in leave and attendance queries, providing detailed
    information about leave balances, policies, and procedures for specific employees.
    """

    name: str = "leave_lightrag_tool"
    description: str = (
        "A specialized tool for leave policy-related queries using LightRAG API. "
        "Provides detailed leave information including leave balance, available leave types "
        "(casual, sick, earned leave), grade-specific policies, location-specific rules, "
        "joining date considerations, leave usage history, approval procedures, and policy guidelines "
        "for specific employees at AYE Finance."
    )
    args_schema: Type[BaseModel] = LeaveLightRAGRequest

    def _run(self, query: str, employee_id: str) -> str:
        """Execute the leave policy query using LightRAG API.
        
        Args:
            query: The leave-related question from the employee
            employee_id: The specific employee ID to fetch personalized data for
            
        Returns:
            str: The response from LightRAG API with leave policy information
        """
        try:
            # Get the API URL and API Key from environment variables
            api_url = os.environ.get('LIGHTRAG_API_URL')
            api_key = os.environ.get('LIGHTRAG_API_KEY')
            
            if not api_url:
                return "Error: LIGHTRAG_API_URL environment variable is not set. Please configure the LightRAG API endpoint."
            
            if not api_key:
                return "Error: LIGHTRAG_API_KEY environment variable is not set. Please configure the LightRAG API key."
            
            # Create the specialized prompt as requested
            specialized_prompt = (
                f"You are a leave policy specialist at AYE Finance. Focus ONLY on leave policies, "
                f"leave balance, vacation, time-off, and attendance-related information for employee {employee_id}. "
                f"Query: {query}. Provide detailed leave information including leave balance, "
                f"available leave types (casual, sick, earned leave), grade-specific policies, "
                f"location-specific rules, joining date considerations, leave usage history, "
                f"approval procedures, and policy guidelines."
            )
            
            # Set up headers with Authorization
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            # Prepare the updated payload structure
            payload = {
                "query": specialized_prompt,
                "workspace": "Aye_fin",
                "mode": "mix",
                "response_type": "Multiple Paragraphs",
                "top_k": 40,
                "chunk_top_k": 20,
                "max_entity_tokens": 6000,
                "max_relation_tokens": 8000,
                "max_total_tokens": 30000,
                "only_need_context": False,
                "only_need_prompt": False,
                "stream": False,
                "history_turns": 0,
                "enable_rerank": False,
                "conversation_history": [],
                "user_prompt": (
                    "Use only the information available in the knowledge base. "
                    "Do not fabricate, infer, or assume any data that is not explicitly "
                    "supported by the retrieved content. If the information is missing or "
                    "incomplete, clearly state that the answer is not available in the "
                    "knowledge base. Do not attempt to guess or generalize."
                )
            }
            
            # Make the POST request to LightRAG API
            response = requests.post(
                api_url,
                headers=headers,
                data=json.dumps(payload),
                timeout=30  # 30 second timeout
            )
            
            # Check if the request was successful
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    # Return the response content
                    if isinstance(response_data, dict):
                        return response_data.get("response", str(response_data))
                    else:
                        return str(response_data)
                except json.JSONDecodeError:
                    return f"Leave policy information retrieved but response format is not JSON: {response.text}"
            else:
                return f"Error querying LightRAG API: HTTP {response.status_code} - {response.text}"
                
        except requests.exceptions.Timeout:
            return "Error: Request to LightRAG API timed out. Please try again later."
        except requests.exceptions.ConnectionError:
            return "Error: Could not connect to LightRAG API. Please check the API URL and network connection."
        except requests.exceptions.RequestException as e:
            return f"Error making request to LightRAG API: {str(e)}"
        except Exception as e:
            return f"Unexpected error occurred while querying leave information: {str(e)}"