from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "sqlite:///./herwell.db"
    llm_provider: str = "mock"
    llm_api_key: str = ""
    llm_model: str = ""
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173,http://127.0.0.1:64193"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
