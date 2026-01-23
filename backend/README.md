# HR Bot Python Backend

FastAPI backend with direct CrewAI flow calls for conversational experience.

## Features

- ✅ Direct flow instance management
- ✅ User-specific sessions with TTL caching
- ✅ Automatic memory persistence
- ✅ True conversational experience

## Setup

### 1. Install Dependencies

```bash
# Install backend dependencies
pip install -r requirements.txt

# Install parent CrewAI project
pip install -e ..
```

### 2. Configure Environment

Copy `.env` and update if needed:
```bash
cp .env .env.local
```

### 3. Run Server

```bash
# Development
uvicorn main:app --reload --port 8000

# Production
uvicorn main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

### POST /api/chat
Process chat message

**Request:**
```json
{
  "user_id": "user-123",
  "user_query": "what is my leave balance?"
}
```

**Response:**
```json
{
  "response": "Your leave balance is...",
  "employee_id": "EMP001",
  "employee_email": "test@example.com"
}
```

### GET /api/health
Health check

**Response:**
```json
{
  "status": "healthy",
  "active_sessions": 5
}
```

### DELETE /api/session/{user_id}
Clear user session

## Architecture

```
Frontend → FastAPI → FlowManager → HRBotFlow (same instance)
                                    ↓
                                Memory persists ✅
```

## Session Management

- **Max Sessions:** 100 concurrent users
- **TTL:** 30 minutes (1800 seconds)
- **Storage:** In-memory with TTLCache
- **Cleanup:** Automatic on timeout
