"""
Main FastAPI application entry point.
Configures middleware, routes, and startup/shutdown events.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import uvicorn

from app.config import settings
from app.database import init_db, engine
from app.api import auth, chat

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    
    Yields:
        None: Application runs during this phase
    """
    # Startup
    print("🚀 Starting AI Tutor Backend...")
    print(f"📡 Environment: {'Development' if settings.DEBUG else 'Production'}")
    print(f"🔧 Debug Mode: {settings.DEBUG}")
    print(f"🗄️ Database: {settings.DATABASE_URL}")
    print(f"🧠 Qdrant: {settings.QDRANT_URL}")
    
    # Initialize database
    try:
        await init_db()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"⚠️ Database initialization warning: {e}")
    
    yield
    
    # Shutdown
    print("👋 Shutting down AI Tutor Backend...")
    await engine.dispose()

# Create FastAPI application
app = FastAPI(
    title="AI Tutor API",
    description="Intelligent AI Tutor with LangChain, Groq API, and Qdrant Memory",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])

# Health check endpoint
@app.get("/")
async def root():
    """
    Root endpoint for API health check.
    
    Returns:
        dict: API status information
    """
    return {
        "message": "AI Tutor API",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs" if settings.DEBUG else None
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    
    Returns:
        dict: Health status
    """
    return {
        "status": "healthy",
        "service": "ai-tutor",
        "timestamp": "2024-01-01T00:00:00Z"  # Replace with actual timestamp
    }

if __name__ == "__main__":
    """
    Main entry point for running the application.
    """
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )