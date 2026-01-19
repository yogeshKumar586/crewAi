from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, List
import requests
import json

# Added import for environment variable access
try:
    import os
except ImportError:
    pass


class EsicLightRagInput(BaseModel):
    """Input schema for ESIC LightRAG Tool."""
    query: str = Field(..., description="The ESIC-related question from the employee")
    employee_id: str = Field(..., description="The specific employee ID to fetch personalized ESIC data for")


class EsicLightRagTool(BaseTool):
    """Tool for querying ESIC-related information using LightRAG API."""

    name: str = "ESIC LightRAG Tool"
    description: str = (
        "Specialized tool for ESIC (Employee State Insurance Corporation) queries. "
        "Provides detailed information about ESIC IP numbers, dispensary details, "
        "contribution calculations, ESIC cards, eligibility status, medical care provisions, "
        "cash benefits, and procedural guidelines for specific employees."
    )
    args_schema: Type[BaseModel] = EsicLightRagInput

    def _run(self, query: str, employee_id: str) -> str:
        """
        Execute ESIC-related query using LightRAG API.
        
        Args:
            query: The ESIC-related question from the employee
            employee_id: The specific employee ID to fetch personalized data for
            
        Returns:
            str: Response from LightRAG API with ESIC information
        """
        try:
            # Get API URL and API Key from environment variables using os.environ.get()
            api_url = os.environ.get('LIGHTRAG_API_URL')
            api_key = os.environ.get('LIGHTRAG_API_KEY')
            
            if not api_url:
                return "Error: LIGHTRAG_API_URL environment variable is not set. Please configure the LightRAG API endpoint."
            
            if not api_key:
                return "Error: LIGHTRAG_API_KEY environment variable is not set. Please configure the LightRAG API key."
            
            # Prepare the specialized ESIC prompt
            specialized_prompt = (
                f"You are an ESIC (Employee State Insurance Corporation) specialist at AYE Finance. "
                f"respond us based on the query information for employee {employee_id}. "
                f"Query: {query}. "
            )
            
            # Prepare the request payload with updated structure
            payload = {
                "query": specialized_prompt,
                "workspace": "Aye_fin",  # ✅ REQUIRED - Added workspace
                "mode": "mix",  # ✅ Updated from "hybrid" to "mix"
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
            
            # Set headers with Authorization
            headers = {
                "Authorization": f"Bearer {api_key}",  # ⚠️ Added API key authorization
                "Content-Type": "application/json"
            }
            
            # Make the POST request to LightRAG API
            response = requests.post(
                api_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            # Check if request was successful
            if response.status_code == 200:
                try:
                    # Try to parse JSON response
                    json_response = response.json()
                    
                    # Extract relevant information from response
                    if isinstance(json_response, dict):
                        # Look for common response fields
                        if 'response' in json_response:
                            return json_response['response']
                        elif 'answer' in json_response:
                            return json_response['answer']
                        elif 'data' in json_response:
                            return str(json_response['data'])
                        else:
                            # Return the entire response if structure is unknown
                            return json.dumps(json_response, indent=2)
                    else:
                        # If response is not a dict, return as string
                        return str(json_response)
                        
                except json.JSONDecodeError:
                    # If response is not JSON, return as text
                    return response.text
                    
            elif response.status_code == 401:
                return "Error: Unauthorized access to LightRAG API. Please check API credentials."
            elif response.status_code == 403:
                return "Error: Forbidden access to LightRAG API. Insufficient permissions."
            elif response.status_code == 404:
                return "Error: LightRAG API endpoint not found. Please verify the API URL."
            elif response.status_code == 429:
                return "Error: Rate limit exceeded for LightRAG API. Please try again later."
            elif response.status_code >= 500:
                return f"Error: LightRAG API server error (Status: {response.status_code}). Please try again later."
            else:
                return f"Error: API request failed with status code {response.status_code}. Response: {response.text}"
                
        except requests.exceptions.Timeout:
            return "Error: Request to LightRAG API timed out. Please try again."
        except requests.exceptions.ConnectionError:
            return "Error: Unable to connect to LightRAG API. Please check your internet connection and API URL."
        except requests.exceptions.RequestException as e:
            return f"Error: Network request failed - {str(e)}"
        except Exception as e:
            return f"Error: An unexpected error occurred - {str(e)}"