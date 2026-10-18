"""Adapter for voice chat to use the existing LangGraph service."""
from app.database import get_db
from app.ai.graph import run_chat


async def answer(message: str, session_id: str) -> str:
    """
    Call the existing LangGraph workflow for voice chat.
    Returns the AI response text.
    """
    db = next(get_db())
    try:
        result = await run_chat(db, message)
        return result.get("response", "")
    finally:
        db.close()
