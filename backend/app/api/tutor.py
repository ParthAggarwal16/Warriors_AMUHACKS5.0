from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.core.security import verify_token
from app.services.tools import (
    get_youtube_recommendations,
    create_study_plan,
    summarize_content,
    motivate_user,
    search_internet
)

router = APIRouter()

class StudyPlanRequest(BaseModel):
    topic: str
    days_available: int
    hours_per_day: int = 2

class SummaryRequest(BaseModel):
    text: str
    max_length: int = 300

class YouTubeRequest(BaseModel):
    topic: str
    max_results: int = 5

class SearchRequest(BaseModel):
    query: str

class MotivationRequest(BaseModel):
    mood: str = "neutral"

@router.post("/study-plan")
async def generate_study_plan(
    request: StudyPlanRequest,
    token: str = Depends(verify_token)
):
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication"
        )
    
    plan = create_study_plan.run(
        topic=request.topic,
        days_available=request.days_available,
        hours_per_day=request.hours_per_day
    )
    
    return {
        "plan": plan,
        "topic": request.topic,
        "days": request.days_available,
        "hours_per_day": request.hours_per_day,
        "generated_at": datetime.now().isoformat()
    }

@router.post("/summarize")
async def summarize_text(
    request: SummaryRequest,
    token: str = Depends(verify_token)
):
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication"
        )
    
    summary = summarize_content.run(
        text=request.text,
        max_length=request.max_length
    )
    
    return {
        "summary": summary,
        "original_length": len(request.text),
        "summary_length": len(summary)
    }

@router.post("/youtube-recommendations")
async def youtube_recommendations(
    request: YouTubeRequest,
    token: str = Depends(verify_token)
):
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication"
        )
    
    recommendations = get_youtube_recommendations.run(
        topic=request.topic,
        max_results=request.max_results
    )
    
    return {
        "recommendations": recommendations,
        "topic": request.topic,
        "count": request.max_results
    }

@router.post("/motivate")
async def get_motivation(
    request: MotivationRequest,
    token: str = Depends(verify_token)
):
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication"
        )
    
    motivation = motivate_user.run(mood=request.mood)
    
    return {
        "motivation": motivation,
        "mood": request.mood,
        "timestamp": datetime.now().isoformat()
    }

@router.post("/search")
async def search_web(
    request: SearchRequest,
    token: str = Depends(verify_token)
):
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication"
        )
    
    results = search_internet.run(query=request.query)
    
    return {
        "results": results,
        "query": request.query,
        "searched_at": datetime.now().isoformat()
    }

@router.get("/tools")
async def list_tools(token: str = Depends(verify_token)):
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication"
        )
    
    tools = [
        {
            "name": "Study Plan Generator",
            "description": "Create structured study plans with deadlines",
            "endpoint": "/api/tutor/study-plan"
        },
        {
            "name": "Text Summarizer",
            "description": "Summarize long texts concisely",
            "endpoint": "/api/tutor/summarize"
        },
        {
            "name": "YouTube Recommendations",
            "description": "Find educational YouTube videos",
            "endpoint": "/api/tutor/youtube-recommendations"
        },
        {
            "name": "Motivation",
            "description": "Get motivational quotes and encouragement",
            "endpoint": "/api/tutor/motivate"
        },
        {
            "name": "Web Search",
            "description": "Search the internet for information",
            "endpoint": "/api/tutor/search"
        }
    ]
    
    return {"tools": tools}