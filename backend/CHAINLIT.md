# Chainlit Interface

## Overview
The Chainlit interface provides a conversational UI for HERwell AI using the same shared LangGraph workflow as the FastAPI backend.

## Installation
Chainlit is already installed in the backend virtual environment.

## Running Chainlit

```bash
cd backend
.venv/Scripts/activate  # Windows
source .venv/bin/activate  # Linux/Mac
chainlit run app/chainlit_app.py --host localhost --port 8000
```

The interface will be available at `http://localhost:8000`

## Features
- **Shared Workflow**: Uses the same `run_chat()` function from `app/ai/graph.py` as the FastAPI API
- **Session State**: Maintains chat history per session
- **Safety Checks**: All safety pre-checks and post-checks from the shared workflow are applied
- **Source Citations**: Displays retrieved sources when available
- **Degraded Mode**: Shows notice when running in mock mode
- **Multilingual**: Supports French, English, and Arabic content

## Environment Variables
The Chainlit app uses the same environment variables as the FastAPI backend:
- `DATABASE_URL`: Database connection string
- `LLM_PROVIDER`: LLM provider (mock, gemini, openai, anthropic)
- `LLM_API_KEY`: API key for the chosen provider
- `LLM_MODEL`: Model name

## Status
**NOT TESTED**: The Chainlit interface has been implemented but not tested in the current environment. To test:

1. Ensure the backend database is initialized: `alembic upgrade head`
2. Set environment variables in `.env`
3. Run the Chainlit server: `chainlit run app/chainlit_app.py`
4. Open the URL in a browser
5. Test chat interactions

## Known Limitations
- Chainlit requires a running web server, which cannot be tested in the current automated environment
- The shared LangGraph workflow is called synchronously; for production, consider async/await patterns
- Session persistence is not configured (sessions are lost on server restart)
