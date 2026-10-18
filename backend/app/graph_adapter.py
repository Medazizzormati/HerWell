"""Fail-closed adapter to HERwell's existing LangGraph/RAG pipeline."""
import importlib
import os


class GraphNotConfigured(RuntimeError):
    pass


def answer_with_existing_graph(message: str, session_id: str) -> str:
    # Use the internal adapter directly instead of environment variable
    from app.services.herwell_chat import answer
    return answer(message, session_id)
