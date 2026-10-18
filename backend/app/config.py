from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    database_url: str = "sqlite:///./herwell.db"
    llm_provider: str = "mock"
    llm_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    llm_model: Optional[str] = None
    cors_origins: str = "http://localhost:5173,http://localhost:5174,http://localhost:5175,http://localhost:5176,http://127.0.0.1:5173,http://127.0.0.1:5174,http://127.0.0.1:5175,http://127.0.0.1:5176,http://127.0.0.1:64193"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
