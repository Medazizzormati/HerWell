from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import Base, engine, SessionLocal
from .api.routes import router
from .api.voice_router import router as voice_router
from .api.auth_router import router as auth_router
from .ai.rag import seed_resources

app = FastAPI(title="HERwell AI API", version="0.1.0",
              description="Non-diagnostic wellbeing and study support MVP.")

# Configure CORS BEFORE including routers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Temporary for debugging
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_resources(db)
    finally:
        db.close()
    yield

app.router.lifespan_context = lifespan

app.include_router(router)
app.include_router(voice_router)
app.include_router(auth_router)

@app.get("/health")
def health():
    return {"status": "ok", "service": "herwell-ai", "llm_provider": settings.llm_provider}
