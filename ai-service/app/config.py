from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "postgresql://herwell:herwell_password@localhost:5432/herwell"
    embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    llm_provider: str = "llamacpp"
    llm_base_url: str = "http://localhost:8081"
    llm_model: str = "llama-3.2-3b-instruct"
    llm_timeout: int = 120
    llm_max_tokens: int = 800
    cors_origins: str = "http://localhost:5173,http://localhost:5174,http://localhost:5175,http://localhost:5176"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
