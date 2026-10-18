from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .llm_provider import LLMProvider

app = FastAPI(title="HERwell AI Service", version="1.0.0",
              description="AI inference and RAG service for HERwell")

# Configure CORS
origins = [item.strip() for item in settings.cors_origins.split(",") if item.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Initialize LLM provider
llm_provider = LLMProvider()

SYSTEM_PROMPT = """
Tu es HERwell AI, un assistant de bien-être et d'organisation non diagnostique pour étudiantes.
Réponds avec empathie, en français simple. Ne pose aucun diagnostic, ne prescris aucun médicament,
ne prétends pas être thérapeute. Utilise les ressources si elles sont pertinentes et ne fabrique pas de sources.
Si le contexte indique un danger, encourage un contact humain immédiat et approprié.
"""

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "herwell-ai-service",
        "llm_provider": settings.llm_provider,
        "embedding_model": settings.embedding_model
    }

@app.post("/api/chat")
async def chat(request: dict):
    """
    Chat endpoint that calls the LLM with RAG context.
    """
    message = request.get("message", "")
    context = request.get("context", [])
    
    if not message or not message.strip():
        raise HTTPException(status_code=400, detail="Message is required")
    
    # Build context string from retrieved resources
    context_str = ""
    if context:
        context_parts = []
        for item in context:
            if isinstance(item, dict):
                title = item.get("title", item.get("resource_title", "Unknown"))
                content = item.get("content", item.get("chunk_content", ""))
                if content:
                    content_preview = content[:300] + "..." if len(content) > 300 else content
                    context_parts.append(f"- {title}: {content_preview}")
        context_str = "\n".join(context_parts)
    
    # Build prompt with context
    prompt = f"Question: {message}\n"
    if context_str:
        prompt += f"\nRessources disponibles:\n{context_str}\n"
    else:
        prompt += "\nAucune ressource pertinente disponible.\n"
    
    try:
        response = await llm_provider.generate(prompt, SYSTEM_PROMPT)
        return {
            "response": response,
            "sources": [item.get("title", "Unknown") for item in context if isinstance(item, dict)],
            "grounded": len(context) > 0,
            "insufficient_context": len(context) == 0
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"LLM service error: {str(e)}")

@app.on_event("shutdown")
async def shutdown():
    llm_provider.close()
