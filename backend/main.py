# """FastAPI backend for HR Bot with direct flow calls."""

# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# import sys
# from pathlib import Path
# import os
# from dotenv import load_dotenv
# import logging

# # Add parent src directory to path
# sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# from services.flow_manager import FlowManager

# # Load environment variables from parent directory first (for OpenAI key)
# parent_env = Path(__file__).parent.parent / ".env"
# if parent_env.exists():
#     load_dotenv(parent_env)

# # Then load backend-specific env (can override parent)
# load_dotenv()

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# )
# logger = logging.getLogger(__name__)

# # Create FastAPI app
# app = FastAPI(
#     title="HR Bot API",
#     version="2.0",
#     description="Python backend with direct CrewAI flow calls"
# )

# # CORS configuration
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:8080")],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Initialize flow manager
# flow_manager = FlowManager()

# # Request/Response models
# class ChatRequest(BaseModel):
#     user_id: str
#     user_query: str

# class ChatResponse(BaseModel):
#     response: str
#     employee_id: str | None = None
#     employee_email: str | None = None

# class HealthResponse(BaseModel):
#     status: str
#     active_sessions: int

# # API Endpoints
# @app.post("/api/chat", response_model=ChatResponse)
# async def chat(request: ChatRequest):
#     """Process chat message with user's flow instance."""
#     try:
#         logger.info(f"Processing query for user: {request.user_id}")
        
#         # Run flow in separate thread to avoid event loop conflict
#         import asyncio
#         result = await asyncio.to_thread(
#             flow_manager.process_query,
#             user_id=request.user_id,
#             query=request.user_query
#         )
        
#         return result
#     except Exception as e:
#         logger.error(f"Error processing query: {str(e)}", exc_info=True)
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/api/health", response_model=HealthResponse)
# async def health():
#     """Health check endpoint."""
#     return {
#         "status": "healthy",
#         "active_sessions": flow_manager.get_active_sessions()
#     }

# @app.delete("/api/session/{user_id}")
# async def clear_session(user_id: str):
#     """Clear user's session."""
#     flow_manager.clear_session(user_id)
#     logger.info(f"Cleared session for user: {user_id}")
#     return {"message": f"Session cleared for user: {user_id}"}

# @app.get("/")
# async def root():
#     """Root endpoint."""
#     return {
#         "message": "HR Bot API",
#         "version": "2.0",
#         "docs": "/docs"
#     }

# if __name__ == "__main__":
#     import uvicorn
#     port = int(os.getenv("PORT", 8000))
#     uvicorn.run(app, host="0.0.0.0", port=port)
