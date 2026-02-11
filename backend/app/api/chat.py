"""
Chat API endpoints for AI Tutor.
Handles chat messages, conversation management, and tool usage.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
import json
import uuid
from datetime import datetime

from app.database import get_db
from app.models.schemas import (
    ChatMessage, ChatResponse, StudyPlanRequest, 
    YouTubeRequest, SummarizeRequest
)
from app.services.auth_service import AuthService
from app.services.groq_service import GroqService
from app.services.youtube_service import YouTubeService

router = APIRouter()
groq_service = GroqService()
youtube_service = YouTubeService()


@router.post("/message", response_model=ChatResponse)
async def send_chat_message(
    chat_data: ChatMessage,
    token: str = Depends(AuthService.verify_token),
    db: AsyncSession = Depends(get_db)
):
    """
    Send a chat message and get AI response.
    Memory retrieval and storage handled inside GroqService.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication"
        )

    user_id = token.get("user_id")
    conversation_id = chat_data.conversation_id or str(uuid.uuid4())

    try:
        # Generate AI response (memory handled inside service)
        response = await groq_service.generate_response(
            user_id=user_id,
            conversation_id=conversation_id,
            message=chat_data.message
        )

        return ChatResponse(
            response=response,
            conversation_id=conversation_id,
            timestamp=datetime.now()
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing message: {str(e)}"
        )


@router.post("/stream")
async def stream_chat_message(
    chat_data: ChatMessage,
    token: str = Depends(AuthService.verify_token),
    db: AsyncSession = Depends(get_db)
):
    """
    Stream chat response in real-time.
    Memory retrieval and storage handled inside GroqService.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication"
        )

    user_id = token.get("user_id")
    conversation_id = chat_data.conversation_id or str(uuid.uuid4())

    async def generate():
        """Generator function for streaming response"""
        try:
            async for chunk in groq_service.generate_streaming_response(
                user_id=user_id,
                conversation_id=conversation_id,
                message=chat_data.message
            ):
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"

            yield f"data: {json.dumps({'done': True})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )


@router.post("/study-plan")
async def generate_study_plan(
    plan_data: StudyPlanRequest,
    token: str = Depends(AuthService.verify_token)
):
    """
    Generate a study plan for a given topic.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication"
        )

    try:
        study_plan = await groq_service.create_study_plan(
            topic=plan_data.topic,
            days=plan_data.days_available,
            hours_per_day=plan_data.hours_per_day
        )

        return {
            "topic": plan_data.topic,
            "days": plan_data.days_available,
            "hours_per_day": plan_data.hours_per_day,
            "plan": study_plan,
            "generated_at": datetime.now()
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating study plan: {str(e)}"
        )


@router.post("/youtube-recommendations")
async def get_youtube_recommendations(
    youtube_data: YouTubeRequest,
    token: str = Depends(AuthService.verify_token)
):
    """
    Get YouTube video recommendations for a learning topic.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication"
        )

    try:
        recommendations = await youtube_service.get_educational_recommendations(
            topic=youtube_data.topic,
            max_results=youtube_data.max_results
        )

        return {
            "topic": youtube_data.topic,
            "recommendations": recommendations,
            "fetched_at": datetime.now()
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching YouTube recommendations: {str(e)}"
        )


@router.post("/summarize")
async def summarize_text(
    summarize_data: SummarizeRequest,
    token: str = Depends(AuthService.verify_token)
):
    """
    Summarize long text content.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication"
        )

    try:
        summary = await groq_service.summarize_text(
            text=summarize_data.text,
            max_length=summarize_data.max_length
        )

        return {
            "summary": summary,
            "original_length": len(summarize_data.text),
            "summary_length": len(summary),
            "compression_ratio": f"{len(summary)/len(summarize_data.text)*100:.1f}%",
            "generated_at": datetime.now()
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error summarizing text: {str(e)}"
        )


