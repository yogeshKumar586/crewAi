from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Any, Dict
import requests
import json
import os

class SalaryLightRAGInput(BaseModel):
    """Input schema for Salary LightRAG Tool."""
    query: str = Field(..., description="The salary-related question from the employee")
    employee_id: str = Field(..., description="The specific employee ID to fetch personalized data for")

class SalaryLightRAGTool(BaseTool):
    """Tool for querying salary and compensation data through LightRAG API.
    
    Enhanced with comprehensive debugging capabilities to provide detailed 
    error diagnostics including environment variable status, API call details, 
    and error classification for troubleshooting.
    """

    name: str = "salary_lightrag_tool"
    description: str = (
        "Query salary and compensation data for specific employees through LightRAG API. "
        "Handles inquiries about basic salary, HRA, allowances, deductions, net pay, "
        "gross pay, tax information, and other compensation details. "
        "Requires employee ID and salary-related query. Enhanced with debugging capabilities."
    )
    args_schema: Type[BaseModel] = SalaryLightRAGInput

    def _get_debug_info(self) -> Dict[str, Any]:
        """Collect debug information about environment and configuration."""
        debug_info = {
            "environment_variables": {},
            "configuration": {},
            "system": {}
        }
        
        # Environment Variable Status
        api_url = os.getenv('LIGHTRAG_API_URL', '')
        api_key = os.getenv('LIGHTRAG_API_KEY', '')
        
        debug_info["environment_variables"]["LIGHTRAG_API_URL"] = {
            "is_set": bool(api_url),
            "value_preview": api_url[:50] + "..." if len(api_url) > 50 else api_url if api_url else "NOT_SET"
        }
        
        debug_info["environment_variables"]["LIGHTRAG_API_KEY"] = {
            "is_set": bool(api_key),
            "length": len(api_key) if api_key else 0,
            "preview": f"{api_key[:4]}...{api_key[-4:]}" if len(api_key) > 8 else "NOT_SET" if not api_key else "TOO_SHORT"
        }
        
        return debug_info

    def _mask_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mask sensitive data in headers and payloads for debugging."""
        masked = data.copy()
        
        if "Authorization" in masked:
            auth_value = masked["Authorization"]
            if isinstance(auth_value, str) and len(auth_value) > 12:
                masked["Authorization"] = f"{auth_value[:12]}...{auth_value[-4:]}"
        
        return masked

    def _classify_error(self, error_type: str, response: requests.Response = None, exception: Exception = None) -> str:
        """Classify the type of error that occurred."""
        if error_type == "env_vars":
            return "MISSING_ENVIRONMENT_VARIABLES"
        elif error_type == "validation":
            return "INPUT_VALIDATION_ERROR"
        elif error_type == "timeout":
            return "NETWORK_CONNECTIVITY_ISSUE"
        elif error_type == "connection":
            return "NETWORK_CONNECTIVITY_ISSUE"
        elif error_type == "request":
            return "NETWORK_CONNECTIVITY_ISSUE"
        elif response:
            if response.status_code == 401:
                return "AUTHENTICATION_FAILURE"
            elif response.status_code == 403:
                return "AUTHENTICATION_FAILURE"
            elif response.status_code == 404:
                return "INVALID_API_ENDPOINT"
            elif response.status_code == 429:
                return "API_SERVER_ERROR"
            elif 400 <= response.status_code < 500:
                return "INVALID_API_ENDPOINT"
            elif response.status_code >= 500:
                return "API_SERVER_ERROR"
            else:
                return "RESPONSE_PARSING_ISSUE"
        else:
            return "UNKNOWN_ERROR"

    def _build_debug_response(self, error_msg: str, error_classification: str, debug_info: Dict[str, Any], 
                            api_call_details: Dict[str, Any] = None) -> str:
        """Build comprehensive debug response."""
        debug_response = f"""
=== SALARY LIGHTRAG TOOL DEBUG REPORT ===

ERROR: {error_msg}

ERROR CLASSIFICATION: {error_classification}

1. ENVIRONMENT VARIABLE STATUS:
   - LIGHTRAG_API_URL: {'✓ SET' if debug_info['environment_variables']['LIGHTRAG_API_URL']['is_set'] else '✗ NOT SET'}
     Value: {debug_info['environment_variables']['LIGHTRAG_API_URL']['value_preview']}
   
   - LIGHTRAG_API_KEY: {'✓ SET' if debug_info['environment_variables']['LIGHTRAG_API_KEY']['is_set'] else '✗ NOT SET'}
     Length: {debug_info['environment_variables']['LIGHTRAG_API_KEY']['length']} characters
     Preview: {debug_info['environment_variables']['LIGHTRAG_API_KEY']['preview']}
"""

        if api_call_details:
            debug_response += f"""
2. API CALL DETAILS:
   - Full API URL: {api_call_details.get('url', 'N/A')}
   - Request Method: {api_call_details.get('method', 'POST')}
   - Request Headers: {json.dumps(api_call_details.get('headers', {}), indent=6)}
   - Request Payload Size: {api_call_details.get('payload_size', 'N/A')} characters
   - Payload Structure: {json.dumps(api_call_details.get('payload_structure', {}), indent=6)}
   - Response Status Code: {api_call_details.get('status_code', 'N/A')}
   - Response Headers: {json.dumps(api_call_details.get('response_headers', {}), indent=6)}
   - Raw Response Content (first 200 chars): {api_call_details.get('response_preview', 'N/A')}
"""
        
        debug_response += f"""
3. ERROR ANALYSIS:
   - Error Type: {error_classification}
   - Recommended Action: {self._get_recommended_action(error_classification)}

=== END DEBUG REPORT ===
"""
        return debug_response

    def _get_recommended_action(self, error_classification: str) -> str:
        """Get recommended action based on error classification."""
        recommendations = {
            "MISSING_ENVIRONMENT_VARIABLES": "Set LIGHTRAG_API_URL and LIGHTRAG_API_KEY environment variables",
            "AUTHENTICATION_FAILURE": "Verify LIGHTRAG_API_KEY is correct and has proper permissions",
            "INVALID_API_ENDPOINT": "Check LIGHTRAG_API_URL format and endpoint availability", 
            "NETWORK_CONNECTIVITY_ISSUE": "Check internet connection and API server status",
            "API_SERVER_ERROR": "Wait and retry, or contact LightRAG support if issue persists",
            "RESPONSE_PARSING_ISSUE": "Check API response format compatibility",
            "INPUT_VALIDATION_ERROR": "Verify query and employee_id parameters are valid",
            "UNKNOWN_ERROR": "Contact technical support with debug details"
        }
        return recommendations.get(error_classification, "Contact technical support")

    def _validate_environment_variables(self) -> tuple[str, str]:
        """Validate and return environment variables with enhanced error checking."""
        api_url = os.getenv('LIGHTRAG_API_URL')
        api_key = os.getenv('LIGHTRAG_API_KEY')
        
        if not api_url or api_url.strip() == '':
            raise ValueError(
                "LIGHTRAG_API_URL environment variable is not set or is empty. "
                "Please configure the LightRAG API endpoint (e.g., 'https://api.lightrag.com/v1/query')."
            )
        
        if not api_key or api_key.strip() == '':
            raise ValueError(
                "LIGHTRAG_API_KEY environment variable is not set or is empty. "
                "Please configure your LightRAG API authentication key."
            )
        
        # Validate URL format
        if not api_url.startswith(('http://', 'https://')):
            raise ValueError(
                f"Invalid LIGHTRAG_API_URL format: '{api_url}'. "
                "URL must start with http:// or https://"
            )
        
        return api_url.strip(), api_key.strip()

    def _build_specialized_prompt(self, query: str, employee_id: str) -> str:
        """Build specialized prompt for salary queries."""
        return (
            f"You are a salary specialist at AYE Finance. Focus ONLY on salary, "
            f"employee {employee_id}. Query: {query}. Provide detailed based on the query "
        )

    def _build_payload(self, specialized_prompt: str) -> dict:
        """Build API payload with correct structure."""
        return {
            "query": specialized_prompt,
            "workspace": "Aye_fin",  # CRITICAL: Required workspace parameter
            "mode": "mix",  # FIXED: Changed from "hybrid" to "mix"
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

    def _parse_response(self, response: requests.Response) -> tuple[str, Dict[str, Any]]:
        """Parse API response with enhanced error handling and return debug details."""
        api_call_details = {
            "status_code": response.status_code,
            "response_headers": dict(response.headers),
            "response_preview": response.text[:200] if response.text else "Empty response"
        }
        
        if response.status_code == 200:
            try:
                response_data = response.json()
                
                # If response is a dictionary, extract relevant content
                if isinstance(response_data, dict):
                    # Check for common response keys
                    content_keys = ['response', 'answer', 'result', 'data', 'content', 'text']
                    
                    for key in content_keys:
                        if key in response_data and response_data[key]:
                            content = response_data[key]
                            # Ensure we return actual salary data
                            if isinstance(content, str) and len(content.strip()) > 0:
                                return content.strip(), api_call_details
                            elif isinstance(content, dict):
                                return json.dumps(content, indent=2), api_call_details
                    
                    # If no standard key found but response has data
                    if response_data:
                        return json.dumps(response_data, indent=2), api_call_details
                    else:
                        return "No salary data found in the API response.", api_call_details
                        
                else:
                    # If response is not a dict, return as string
                    result = str(response_data).strip()
                    return (result if result else "Empty response received from API."), api_call_details
                    
            except json.JSONDecodeError as e:
                # If JSON parsing fails, try to return raw text
                raw_text = response.text.strip()
                if raw_text:
                    return raw_text, api_call_details
                else:
                    error_msg = f"API returned invalid JSON and empty content. JSON error: {str(e)}"
                    return error_msg, api_call_details
        else:
            # Enhanced error handling for different status codes
            error_msg = f"LightRAG API request failed with status code {response.status_code}"
            
            if response.status_code == 401:
                error_msg += " (Unauthorized). Please check your LIGHTRAG_API_KEY."
            elif response.status_code == 403:
                error_msg += " (Forbidden). Your API key may not have access to the workspace 'Aye_fin'."
            elif response.status_code == 404:
                error_msg += " (Not Found). Please verify the LIGHTRAG_API_URL endpoint."
            elif response.status_code == 429:
                error_msg += " (Too Many Requests). Please wait before making another request."
            elif response.status_code >= 500:
                error_msg += " (Server Error). The LightRAG service may be temporarily unavailable."
            
            try:
                error_details = response.json()
                error_msg += f" Error details: {json.dumps(error_details, indent=2)}"
            except json.JSONDecodeError:
                if response.text.strip():
                    error_msg += f" Raw error response: {response.text}"
            
            return f"Error: {error_msg}", api_call_details

    def _run(self, query: str, employee_id: str) -> str:
        """
        Execute salary query through LightRAG API with comprehensive debugging.
        
        Args:
            query: The salary-related question from the employee
            employee_id: The specific employee ID to fetch personalized data for
            
        Returns:
            str: Response from LightRAG API containing salary information or detailed debug report
        """
        debug_info = self._get_debug_info()
        api_call_details = {}
        
        try:
            # Validate inputs
            if not query.strip():
                error_classification = self._classify_error("validation")
                return self._build_debug_response(
                    "Query cannot be empty. Please provide a salary-related question.",
                    error_classification,
                    debug_info
                )
            
            if not employee_id.strip():
                error_classification = self._classify_error("validation")
                return self._build_debug_response(
                    "Employee ID cannot be empty. Please provide a valid employee ID.",
                    error_classification,
                    debug_info
                )
            
            # Validate environment variables
            try:
                api_url, api_key = self._validate_environment_variables()
            except ValueError as e:
                error_classification = self._classify_error("env_vars")
                return self._build_debug_response(
                    str(e),
                    error_classification,
                    debug_info
                )
            
            # Build specialized prompt and payload
            specialized_prompt = self._build_specialized_prompt(query, employee_id)
            payload = self._build_payload(specialized_prompt)
            
            # Set headers with proper Authorization format
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            # Prepare API call details for debugging
            api_call_details = {
                "url": api_url,
                "method": "POST",
                "headers": self._mask_sensitive_data(headers),
                "payload_size": len(json.dumps(payload)),
                "payload_structure": {
                    key: f"{type(value).__name__} ({'truncated...' if isinstance(value, str) and len(value) > 100 else str(value)[:100]})"
                    for key, value in payload.items()
                }
            }
            
            # Make POST request to LightRAG API
            response = requests.post(
                api_url,
                headers=headers,
                json=payload,
                timeout=30  # 30 second timeout
            )
            
            # Parse response and get debug details
            result, response_debug = self._parse_response(response)
            api_call_details.update(response_debug)
            
            # If it's an error response, return debug info
            if result.startswith("Error:"):
                error_classification = self._classify_error("api", response)
                return self._build_debug_response(
                    result,
                    error_classification,
                    debug_info,
                    api_call_details
                )
            
            # Success - return the actual result
            return result
                
        except requests.exceptions.Timeout:
            error_classification = self._classify_error("timeout")
            error_msg = "Request to LightRAG API timed out after 30 seconds. The service may be experiencing high load."
            return self._build_debug_response(
                error_msg,
                error_classification,
                debug_info,
                api_call_details
            )
            
        except requests.exceptions.ConnectionError:
            error_classification = self._classify_error("connection")
            error_msg = "Could not connect to LightRAG API. Please check your internet connection and verify that the LIGHTRAG_API_URL is correct."
            return self._build_debug_response(
                error_msg,
                error_classification,
                debug_info,
                api_call_details
            )
            
        except requests.exceptions.RequestException as e:
            error_classification = self._classify_error("request")
            error_msg = f"Request to LightRAG API failed. Network error details: {str(e)}"
            return self._build_debug_response(
                error_msg,
                error_classification,
                debug_info,
                api_call_details
            )
            
        except Exception as e:
            error_classification = "UNKNOWN_ERROR"
            error_msg = f"An unexpected error occurred while querying salary data. Details: {str(e)}"
            return self._build_debug_response(
                error_msg,
                error_classification,
                debug_info,
                api_call_details
            )