from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Dict, Any
import requests
import json
import os

class MedicalLightRAGToolInput(BaseModel):
    """Input schema for Medical LightRAG Tool."""
    query: str = Field(..., description="The medical/insurance-related question from the employee")
    employee_id: str = Field(..., description="The specific employee ID to fetch personalized medical data for")

class MedicalLightRAGTool(BaseTool):
    """Tool for querying medical insurance information using LightRAG API.
    
    This tool specializes in medical insurance queries and provides detailed information
    including medical limits, used amounts, available balances, ESIC details, 
    dispensary/hospital information, medical card links, eligible family members,
    claim procedures, and coverage details.
    """

    name: str = "medical_lightrag_tool"
    description: str = (
        "Query medical insurance information for employees using LightRAG API. "
        "Provides detailed medical coverage data including limits, balances, ESIC details, "
        "dispensary information, medical cards, family member eligibility, and claim procedures. "
        "Requires employee ID and medical/insurance-related query."
    )
    args_schema: Type[BaseModel] = MedicalLightRAGToolInput

    def _validate_environment_variables(self) -> tuple[str, str]:
        """Validate and retrieve required environment variables.
        
        Returns:
            tuple: (api_url, api_key) if valid
            
        Raises:
            ValueError: If environment variables are missing or invalid
        """
        api_url = os.environ.get('LIGHTRAG_API_URL')
        api_key = os.environ.get('LIGHTRAG_API_KEY')
        
        if not api_url:
            raise ValueError("LIGHTRAG_API_URL environment variable is not set or is empty")
        
        if not api_key:
            raise ValueError("LIGHTRAG_API_KEY environment variable is not set or is empty")
            
        # Basic URL validation
        if not api_url.startswith(('http://', 'https://')):
            raise ValueError("LIGHTRAG_API_URL must be a valid HTTP/HTTPS URL")
            
        # Basic API key validation
        if len(api_key.strip()) < 10:
            raise ValueError("LIGHTRAG_API_KEY appears to be too short or invalid")
            
        return api_url.strip(), api_key.strip()

    def _parse_api_response(self, response_data: Dict[str, Any]) -> str:
        """Parse and extract meaningful medical data from API response.
        
        Args:
            response_data: The JSON response from the API
            
        Returns:
            str: Formatted medical information
        """
        try:
            # Handle different response formats
            if isinstance(response_data, dict):
                # Check for common response structures
                if 'response' in response_data:
                    medical_content = response_data['response']
                elif 'answer' in response_data:
                    medical_content = response_data['answer']
                elif 'content' in response_data:
                    medical_content = response_data['content']
                elif 'data' in response_data:
                    medical_content = response_data['data']
                else:
                    # If no standard field, look for the main content
                    medical_content = str(response_data)
                
                # Extract additional metadata if available
                metadata = {}
                if 'sources' in response_data:
                    metadata['sources'] = response_data['sources']
                if 'confidence' in response_data:
                    metadata['confidence'] = response_data['confidence']
                if 'timestamp' in response_data:
                    metadata['timestamp'] = response_data['timestamp']
                
                # Format the response with medical data emphasis
                formatted_response = f"🏥 Medical Insurance Information:\n\n{medical_content}"
                
                if metadata:
                    formatted_response += f"\n\n📋 Additional Information:\n{json.dumps(metadata, indent=2)}"
                
                return formatted_response
            else:
                return f"🏥 Medical Insurance Information:\n\n{str(response_data)}"
                
        except Exception as e:
            return f"⚠️ Warning: Could not parse response optimally, returning raw data:\n\n{json.dumps(response_data, indent=2, default=str)}\n\nParsing error: {str(e)}"

    def _run(self, query: str, employee_id: str) -> str:
        """Execute the medical insurance query using LightRAG API.
        
        Args:
            query: The medical/insurance-related question
            employee_id: The employee ID for personalized data
            
        Returns:
            str: The API response with medical insurance information
        """
        try:
            # Validate environment variables first
            api_url, api_key = self._validate_environment_variables()
            
            # Construct the specialized medical insurance prompt
            specialized_prompt = (
                f"You are a medical insurance specialist at AYE Finance. "
                f"respond us based on the query "
                f"information for employee {employee_id}. "
                f"Query: {query}. "
            )

            # ✅ CRITICAL FIX 1-3: Prepare the request payload with all required parameters
            payload = {
                "query": specialized_prompt,
                "workspace": "Aye_fin",  # ✅ FIX 1: REQUIRED - Added workspace parameter
                "mode": "mix",  # ✅ FIX 2: Updated from "hybrid" to "mix"
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

            # ✅ FIX 3: Set up headers with proper Authorization format
            headers = {
                "Authorization": f"Bearer {api_key}",  # ✅ Proper Bearer token format
                "Content-Type": "application/json",
                "Accept": "application/json"
            }

            # Make the POST request to LightRAG API with enhanced error handling
            try:
                response = requests.post(
                    api_url,
                    headers=headers,
                    json=payload,
                    timeout=30  # 30 second timeout
                )
                
                # ✅ FIX 4: Enhanced error handling for API responses
                if response.status_code == 200:
                    try:
                        response_data = response.json()
                        # ✅ FIX 5: Better response parsing to extract actual medical data
                        return self._parse_api_response(response_data)
                        
                    except json.JSONDecodeError as e:
                        return f"⚠️ API Response Parsing Error: The API returned a successful response but the JSON could not be parsed.\nError: {str(e)}\nRaw Response: {response.text[:500]}..."
                        
                elif response.status_code == 401:
                    return "🔐 Authentication Error: Invalid API key or unauthorized access. Please check your LIGHTRAG_API_KEY."
                    
                elif response.status_code == 403:
                    return "🚫 Access Forbidden: The API key doesn't have permission to access this resource."
                    
                elif response.status_code == 404:
                    return "🔍 Not Found: The API endpoint was not found. Please check the LIGHTRAG_API_URL."
                    
                elif response.status_code == 429:
                    return "⏱️ Rate Limited: Too many requests. Please wait a moment and try again."
                    
                elif response.status_code >= 500:
                    return f"🛠️ Server Error: The LightRAG API is experiencing issues (Status: {response.status_code}). Please try again later.\nResponse: {response.text[:200]}..."
                    
                else:
                    return (
                        f"❌ API Error: Request failed with status code {response.status_code}\n"
                        f"Response: {response.text[:300]}..."
                    )

            # ✅ FIX 4: Enhanced network error handling
            except requests.exceptions.Timeout:
                return (
                    "⏰ Timeout Error: The LightRAG API did not respond within 30 seconds. "
                    "This might indicate server overload or network issues. Please try again."
                )
            
            except requests.exceptions.ConnectionError as e:
                return (
                    f"🌐 Connection Error: Unable to connect to the LightRAG API.\n"
                    f"Please check:\n"
                    f"- Network connectivity\n"
                    f"- API URL correctness: {api_url}\n"
                    f"- Server availability\n"
                    f"Error details: {str(e)}"
                )
            
            except requests.exceptions.HTTPError as e:
                return f"🔗 HTTP Error: {str(e)}"
                
            except requests.exceptions.RequestException as e:
                return f"📡 Request Error: An unexpected network error occurred: {str(e)}"

        # ✅ FIX 4: Enhanced error handling for environment variables
        except ValueError as e:
            return f"⚙️ Configuration Error: {str(e)}"
            
        except Exception as e:
            return (
                f"🚨 Unexpected Error: An unexpected error occurred while processing your medical insurance query.\n"
                f"Error type: {type(e).__name__}\n"
                f"Error details: {str(e)}\n"
                f"Please contact system administrator if this persists."
            )