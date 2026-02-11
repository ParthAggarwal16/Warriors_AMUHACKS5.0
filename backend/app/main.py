from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
import uvicorn

from database import get_db, engine, Base
from routers import auth, users, subjects, tasks, study_sessions, analytics
from config import settings

# Create tables
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting StudySyncPro Backend...")
    yield
    # Shutdown
    print("👋 Shutting down StudySyncPro Backend...")

app = FastAPI(
    title="StudySyncPro API",
    description="AI-Powered Academic Recovery Engine Backend",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(subjects.router, prefix="/api/subjects", tags=["Subjects"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(study_sessions.router, prefix="/api/sessions", tags=["Study Sessions"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])

@app.get("/")
async def root():
    return {
        "message": "StudySyncPro API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "connected"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )