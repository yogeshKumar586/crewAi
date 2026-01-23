# """Flow manager for handling user flow instances with caching."""

# from cachetools import TTLCache
# import sys
# from pathlib import Path
# from datetime import datetime
# import logging

# # Add parent src directory to path
# sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
# from aye_finance_hr_bot_v2.flows.hr_bot_flow import HRBotFlow

# logger = logging.getLogger(__name__)

# class FlowManager:
#     """Manages flow instances per user with TTL-based caching."""
    
#     def __init__(self, max_sessions=100, ttl_seconds=1800):
#         """
#         Initialize flow manager.
        
#         Args:
#             max_sessions: Maximum number of concurrent sessions (default: 100)
#             ttl_seconds: Session timeout in seconds (default: 1800 = 30 minutes)
#         """
#         self.flows = TTLCache(maxsize=max_sessions, ttl=ttl_seconds)
#         self.last_activity = {}
#         logger.info(f"FlowManager initialized: max_sessions={max_sessions}, ttl={ttl_seconds}s")
    
#     def get_or_create_flow(self, user_id: str) -> HRBotFlow:
#         """
#         Get existing flow or create new one for user.
        
#         Args:
#             user_id: Unique user identifier
            
#         Returns:
#             HRBotFlow instance for the user
#         """
#         if user_id not in self.flows:
#             logger.info(f"Creating new flow for user: {user_id}")
#             self.flows[user_id] = HRBotFlow()
#         else:
#             logger.debug(f"Reusing existing flow for user: {user_id}")
        
#         self.last_activity[user_id] = datetime.now()
#         return self.flows[user_id]
    
#     def process_query(self, user_id: str, query: str) -> dict:
#         """
#         Process user query with their flow instance.
        
#         Args:
#             user_id: Unique user identifier
#             query: User's query string
            
#         Returns:
#             Dictionary with response and state information
#         """
#         flow = self.get_or_create_flow(user_id)
        
#         # Set query in flow state
#         flow.state.employee_query = query
        
#         # Execute flow
#         logger.info(f"Executing flow for user {user_id}: {query[:50]}...")
#         result = flow.kickoff()
        
#         # Return response with state
#         return {
#             "response": str(result),
#             "employee_id": flow.state.employee_id,
#             "employee_email": flow.state.employee_email
#         }
    
#     def clear_session(self, user_id: str):
#         """
#         Clear user's session.
        
#         Args:
#             user_id: Unique user identifier
#         """
#         if user_id in self.flows:
#             del self.flows[user_id]
#             if user_id in self.last_activity:
#                 del self.last_activity[user_id]
#             logger.info(f"Cleared session for user: {user_id}")
#         else:
#             logger.warning(f"No session found for user: {user_id}")
    
#     def get_active_sessions(self) -> int:
#         """
#         Get count of active sessions.
        
#         Returns:
#             Number of active sessions
#         """
#         return len(self.flows)
    
#     def cleanup_expired_sessions(self):
#         """Cleanup expired sessions (called automatically by TTLCache)."""
#         # TTLCache handles this automatically
#         pass
