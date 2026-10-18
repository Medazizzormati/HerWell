from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings

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
    
    # TODO: Implement real LLM call
    return {
        "response": "AI service not yet fully configured. Mock response.",
        "sources": [],
        "grounded": False,
        "insufficient_context": True
    }

@app.post("/api/embed")
async def embed(request: dict):
    """
    Generate embeddings for text.
    """
    text = request.get("text", "")
    # TODO: Implement real embedding generation
    return {"embedding": [], "model": settings.embedding_model}
