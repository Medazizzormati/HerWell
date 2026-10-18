from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .llm_provider import LLMProvider
from .rag import RAGPipeline

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

# Initialize components
llm_provider = LLMProvider()
rag_pipeline = RAGPipeline(settings.database_url, settings.embedding_model)

SYSTEM_PROMPT = """
Tu es HERwell AI, un assistant de bien-être et d'organisation non diagnostique pour étudiantes.
Réponds avec empathie, en français simple. Ne pose aucun diagnostic, ne prescris aucun médicament,
ne prétends pas être thérapeute. Utilise les ressources si elles sont pertinentes et ne fabrique pas de sources.
Si le contexte indique un danger, encourage un contact humain immédiat et approprié.
"""

@app.on_event("startup")
async def startup():
    """Initialize RAG pipeline on startup."""
    try:
        rag_pipeline.create_pgvector_tables()
        rag_pipeline.load_model()
    except Exception as e:
        print(f"Warning: RAG initialization failed: {e}")

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "herwell-ai-service",
        "llm_provider": settings.llm_provider,
        "embedding_model": settings.embedding_model,
        "rag_enabled": True
    }

@app.post("/api/chat")
async def chat(request: dict):
    """
    Chat endpoint that calls the LLM with RAG context.
    """
    message = request.get("message", "")
    use_rag = request.get("use_rag", True)
    
    if not message or not message.strip():
        raise HTTPException(status_code=400, detail="Message is required")
    
    # Retrieve context using RAG
    context = []
    if use_rag:
        try:
            context = rag_pipeline.retrieve_with_metadata(message, limit=3)
        except Exception as e:
            print(f"RAG retrieval failed: {e}")
    
    # Build context string from retrieved resources
    context_str = ""
    if context:
        context_parts = []
        for item in context:
            title = item.get("resource_title", "Unknown")
            content = item.get("content", "")
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
            "sources": [
                {
                    "title": item.get("resource_title", "Unknown"),
                    "url": item.get("source_url", ""),
                    "similarity": item.get("similarity", 0)
                }
                for item in context
            ],
            "grounded": len(context) > 0,
            "insufficient_context": len(context) == 0
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"LLM service error: {str(e)}")

@app.post("/api/ingest")
async def ingest_document(request: dict):
    """
    Ingest a document into the RAG system.
    """
    resource_id = request.get("resource_id")
    title = request.get("title")
    content = request.get("content")
    
    if not all([resource_id, title, content]):
        raise HTTPException(status_code=400, detail="resource_id, title, and content are required")
    
    try:
        rag_pipeline.ingest_document(resource_id, title, content)
        return {"status": "success", "message": "Document ingested successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

@app.post("/api/search")
async def search(request: dict):
    """
    Search for relevant documents.
    """
    query = request.get("query")
    limit = request.get("limit", 5)
    
    if not query or not query.strip():
        raise HTTPException(status_code=400, detail="Query is required")
    
    try:
        results = rag_pipeline.retrieve_with_metadata(query, limit=limit)
        return {"results": results, "count": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.on_event("shutdown")
async def shutdown():
    llm_provider.close()
