from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import Base, engine, SessionLocal
from .api.routes import router
from .api.voice_router import router as voice_router
from .ai.rag import seed_resources

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_resources(db)
    finally:
        db.close()
    yield

app = FastAPI(title="HERwell AI API", version="0.1.0",
              description="Non-diagnostic wellbeing and study support MVP.",
              lifespan=lifespan)
origins = [item.strip() for item in settings.cors_origins.split(",") if item.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=False,
                   allow_methods=["*"], allow_headers=["*"])
app.include_router(router)
app.include_router(voice_router)

@app.get("/health")
def health():
    return {"status": "ok", "service": "herwell-ai", "llm_provider": settings.llm_provider}
