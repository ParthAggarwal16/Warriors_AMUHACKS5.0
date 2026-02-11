"""
Application configuration settings using Pydantic.
Loads environment variables and provides typed configuration.
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
from enum import Enum

class LLMProvider(str, Enum):
    """Supported LLM providers"""
    GROQ = "groq"
    OPENAI = "openai"

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "AI Tutor"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Groq Configuration
    GROQ_API_KEY: str
    GROQ_MODEL: str = "mixtral-8x7b-32768"
    
    # YouTube Configuration
    YOUTUBE_API_KEY: str
    
    # Database Configuration
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/aitutor"
    
    # Qdrant Configuration
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_COLLECTION_NAME: str = "conversation_memory"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # JWT Configuration
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # LangChain Configuration
    LLM_PROVIDER: LLMProvider = LLMProvider.GROQ
    TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 4096
    
    # Memory Configuration
    MEMORY_WINDOW_SIZE: int = 10
    MAX_CONVERSATION_HISTORY: int = 20
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()