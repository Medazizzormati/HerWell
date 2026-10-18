"""Fail-closed adapter to HERwell's existing LangGraph/RAG pipeline."""
import importlib
import os
import asyncio


class GraphNotConfigured(RuntimeError):
    pass


async def answer_with_existing_graph(message: str, session_id: str) -> str:
    # Use the internal adapter directly instead of environment variable
    from app.services.herwell_chat import answer
    # Run the synchronous answer function in a thread pool
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, answer, message, session_id)
    return result
