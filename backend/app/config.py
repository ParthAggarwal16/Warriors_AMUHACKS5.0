"""
Application configuration settings using Pydantic.
Loads environment variables and provides typed configuration.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
from enum import Enum


class LLMProvider(str, Enum):
    """Supported LLM providers"""
    GROQ = "groq"
    # OPENAI = "openai"


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="forbid"  # ensures only defined fields are allowed
    )

    # Application
    APP_NAME: str = "AI Tutor"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Groq Configuration
    GROQ_API_KEY: str
    GROQ_MODEL: str 

    # YouTube Configuration
    YOUTUBE_API_KEY: str

    # Database Configuration (NO DEFAULT)
    DATABASE_URL: str

    # Qdrant Configuration
    QDRANT_URL: str  # e.g., "https://<your-cluster-id>.us-east4-0.gcp.cloud.qdrant.io"
    QDRANT_API_KEY: str  # <--- add this for Qdrant Cloud authentication
    QDRANT_COLLECTION_NAME: str = "conversation_memory"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

    # JWT Configuration
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # LangChain Configuration
    LLM_PROVIDER: LLMProvider = LLMProvider.GROQ
    TEMPERATURE: float = 1.0
    MAX_TOKENS: int = 4096

    # Memory Configuration
    MEMORY_WINDOW_SIZE: int = 10
    MAX_CONVERSATION_HISTORY: int = 20

    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000"
    ]


settings = Settings()
