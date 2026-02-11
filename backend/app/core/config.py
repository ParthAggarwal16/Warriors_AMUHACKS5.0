from pydantic_settings import BaseSettings
from typing import List
from enum import Enum

class LLMProvider(str, Enum):
    GROQ = "groq"
    OPENAI = "openai"

class Settings(BaseSettings):
    APP_NAME: str = "AI Tutor"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    GROQ_API_KEY: str
    GROQ_MODEL: str = "mixtral-8x7b-32768"
    
    YOUTUBE_API_KEY: str
    
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_COLLECTION: str = "conversation_memory"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/aitutor"
    
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    LLM_PROVIDER: LLMProvider = LLMProvider.GROQ
    TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 4096
    
    MEMORY_WINDOW_SIZE: int = 10
    CONVERSATION_SUMMARY_LENGTH: int = 200
    
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()