"""
Chainlit interface for HERwell AI.
Uses the same shared LangGraph workflow as FastAPI.
"""

import chainlit as cl
import logging
from typing import Optional

from app.ai.graph import run_chat
from app.config import settings

logger = logging.getLogger(__name__)


@cl.on_chat_start
async def on_chat_start():
    """Initialize chat session."""
    await cl.Message(
        content="👋 Bienvenue sur HERwell AI !\n\n"
        "Je suis votre assistant de bien-être et d'organisation d'études.\n\n"
        "Je peux vous aider avec :\n"
        "• Gestion du stress et bien-être\n"
        "• Techniques d'étude et organisation\n"
        "• Planification d'emploi du temps\n"
        "• Ressources éducatives\n\n"
        "⚠️ **Important** : Je ne suis pas un professionnel de santé mentale. "
        "En cas de crise ou d'urgence, contactez les services d'aide locaux.\n\n"
        f"**Fournisseur LLM** : {settings.llm_provider}",
    ).send()
    
    # Store session state
    cl.user_session.set("chat_history", [])


@cl.on_message
async def on_message(message: cl.Message):
    """Handle incoming messages."""
    user_message = message.content
    
    # Add user message to history
    history = cl.user_session.get("chat_history", [])
    history.append({"role": "user", "content": user_message})
    cl.user_session.set("chat_history", history)
    
    # Show thinking indicator
    thinking_msg = cl.Message(content="🤔 Réflexion en cours...")
    await thinking_msg.send()
    
    try:
        # Run the shared LangGraph workflow
        result = run_chat(
            user_message=user_message,
            chat_history=history[:-1],  # Exclude current message
            session_id=cl.user_session.get("id", "default")
        )
        
        # Update thinking message with response
        await thinking_msg.remove()
        
        # Send response
        response_content = result.get("response", "Désolé, je n'ai pas pu générer de réponse.")
        
        # Add sources if available
        if result.get("sources"):
            sources_text = "\n\n**Sources** :\n"
            for source in result["sources"][:3]:
                sources_text += f"• {source.get('title', 'Sans titre')} - {source.get('source', '')}\n"
            response_content += sources_text
        
        # Add degraded mode notice if applicable
        if result.get("degraded_mode"):
            response_content += "\n\n⚠️ Mode dégradé : Utilisation du mode mock (pas de connexion LLM)."
        
        await cl.Message(content=response_content).send()
        
        # Add assistant message to history
        history.append({"role": "assistant", "content": response_content})
        cl.user_session.set("chat_history", history)
        
        # Log safety routing if triggered
        if result.get("safety_routed"):
            logger.warning(f"Safety routing triggered for session {cl.user_session.get('id')}")
        
    except Exception as e:
        logger.error(f"Error in Chainlit chat: {e}")
        await thinking_msg.remove()
        await cl.Message(
            content="❌ Une erreur s'est produite. Veuillez réessayer."
        ).send()


@cl.on_settings_update
async def on_settings_update(settings: cl.Settings):
    """Handle settings updates."""
    logger.info(f"Settings updated: {settings}")


if __name__ == "__main__":
    # Run Chainlit application
    import sys
    from chainlit.cli import run_chainlit
    
    sys.argv = ["chainlit", "run", "app/chainlit_app.py", "--host", "localhost", "--port", "8000"]
    run_chainlit()
