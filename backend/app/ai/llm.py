from ..config import settings

async def generate_response(message: str, resources: list[dict], intent: str) -> tuple[str, bool]:
    provider = settings.llm_provider.lower()
    
    # Handle different resource formats (keyword vs semantic retrieval)
    context_parts = []
    for r in resources:
        if isinstance(r, dict):
            title = r.get('title', r.get('resource_title', 'Unknown'))
            content = r.get('content', r.get('chunk_content', ''))
            if content:
                # Truncate content for context
                content_preview = content[:200] + "..." if len(content) > 200 else content
                context_parts.append(f"- {title}: {content_preview}")
    
    context = "\n".join(context_parts)
    
    if provider == "mock" or not settings.llm_api_key:
        reply = (
            "Mode démo sans modèle IA connecté. "
            "Je peux proposer des pistes générales, sans diagnostic. "
        )
        if resources:
            titles = [r.get('title', r.get('resource_title', 'Unknown')) for r in resources if isinstance(r, dict)]
            reply += "Voici des ressources pertinentes : " + "; ".join(titles) + ". "
            reply += "À retenir : choisissez une petite prochaine étape réaliste, puis prévoyez une pause."
        else:
            reply += "Essayez de découper votre objectif en une étape de 10 à 20 minutes et de prévoir une pause."
        return reply, True

    prompt = (
        "Tu es HERwell AI, un assistant de bien-être et d'organisation non diagnostique pour étudiantes. "
        "Réponds avec empathie, en français simple. Ne pose aucun diagnostic, ne prescris aucun médicament, "
        "ne prétends pas être thérapeute. Utilise les ressources si elles sont pertinentes et ne fabrique pas de sources. "
        "Si le contexte indique un danger, encourage un contact humain immédiat et approprié.\n"
        f"Intention: {intent}\nQuestion: {message}\nRessources disponibles:\n{context or 'Aucune ressource pertinente.'}"
    )
    try:
        if provider == "gemini":
            from google import genai
            client = genai.Client(api_key=settings.llm_api_key)
            result = client.models.generate_content(model=settings.llm_model or "gemini-2.0-flash", contents=prompt)
            return (result.text or "Je n'ai pas pu formuler une réponse."), False
        if provider == "openai":
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=settings.llm_api_key)
            result = await client.chat.completions.create(
                model=settings.llm_model or "gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            return result.choices[0].message.content or "", False
        if provider == "anthropic":
            from anthropic import AsyncAnthropic
            client = AsyncAnthropic(api_key=settings.llm_api_key)
            result = await client.messages.create(
                model=settings.llm_model or "claude-3-5-haiku-latest",
                max_tokens=700,
                messages=[{"role": "user", "content": prompt}]
            )
            return "".join(block.text for block in result.content if getattr(block, "type", "") == "text"), False
        return "Fournisseur LLM non reconnu. Vérifiez LLM_PROVIDER.", True
    except Exception:
        return ("Le modèle IA est momentanément indisponible. Consultez les ressources disponibles "
                "et réessayez plus tard."), True
