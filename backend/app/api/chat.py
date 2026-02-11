from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import json
import uuid

from app.db.session import get_db
from app.db.models import Conversation, Message
from app.core.security import verify_token
from app.services.grok_agent import GroqTutorAgent
from app.services.qdrant_mem import QdrantMemoryManager

router = APIRouter()

@router.post("/conversation")
async def create_conversation(
    title: str = "New Conversation",
    token: str = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication"
        )
    
    user_id = token.get("user_id")
    conversation_id = str(uuid.uuid4())
    
    conversation = Conversation(
        user_id=user_id,
        conversation_id=conversation_id,
        title=title
    )
    
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)
    
    return {
        "conversation_id": conversation_id,
        "title": title,
        "created_at": conversation.created_at
    }

@router.get("/conversations")
async def get_conversations(
    token: str = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication"
        )
    
    user_id = token.get("user_id")
    
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
    )
    
    conversations = result.scalars().all()
    
    return [
        {
            "id": conv.id,
            "conversation_id": conv.conversation_id,
            "title": conv.title,
            "created_at": conv.created_at,
            "updated_at": conv.updated_at
        }
        for conv in conversations
    ]

@router.post("/message")
async def send_message(
    conversation_id: str,
    message: str,
    token: str = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication"
        )
    
    user_id = token.get("user_id")
    
    result = await db.execute(
        select(Conversation).where(
            (Conversation.conversation_id == conversation_id) &
            (Conversation.user_id == user_id)
        )
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    user_message = Message(
        conversation_id=conversation_id,
        role="user",
        content=message
    )
    
    db.add(user_message)
    await db.commit()
    
    agent = GroqTutorAgent(user_id=str(user_id), conversation_id=conversation_id)
    response = await agent.process_message(message)
    
    ai_message = Message(
        conversation_id=conversation_id,
        role="assistant",
        content=response
    )
    
    db.add(ai_message)
    await db.commit()
    
    conversation.updated_at = db.func.now()
    await db.commit()
    
    return {
        "response": response,
        "conversation_id": conversation_id
    }

@router.post("/stream")
async def stream_message(
    conversation_id: str,
    message: str,
    token: str = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication"
        )
    
    user_id = token.get("user_id")
    
    async def generate():
        agent = GroqTutorAgent(user_id=str(user_id), conversation_id=conversation_id)
        
        user_message = Message(
            conversation_id=conversation_id,
            role="user",
            content=message
        )
        
        db.add(user_message)
        await db.commit()
        
        full_response = ""
        
        try:
            async for chunk in agent.llm.astream(message):
                if hasattr(chunk, 'content'):
                    content = chunk.content
                    full_response += content
                    yield f"data: {json.dumps({'chunk': content})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        ai_message = Message(
            conversation_id=conversation_id,
            role="assistant",
            content=full_response
        )
        
        db.add(ai_message)
        await db.commit()
        
        result = await db.execute(
            select(Conversation).where(Conversation.conversation_id == conversation_id)
        )
        conversation = result.scalar_one_or_none()
        
        if conversation:
            conversation.updated_at = db.func.now()
            await db.commit()
        
        yield f"data: {json.dumps({'done': True})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")

@router.get("/history/{conversation_id}")
async def get_conversation_history(
    conversation_id: str,
    token: str = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication"
        )
    
    user_id = token.get("user_id")
    
    result = await db.execute(
        select(Conversation).where(
            (Conversation.conversation_id == conversation_id) &
            (Conversation.user_id == user_id)
        )
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.timestamp.asc())
    )
    
    messages = result.scalars().all()
    
    return [
        {
            "id": msg.id,
            "role": msg.role,
            "content": msg.content,
            "timestamp": msg.timestamp
        }
        for msg in messages
    ]

@router.delete("/conversation/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    token: str = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication"
        )
    
    user_id = token.get("user_id")
    
    result = await db.execute(
        select(Conversation).where(
            (Conversation.conversation_id == conversation_id) &
            (Conversation.user_id == user_id)
        )
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    await db.execute(
        Message.__table__.delete().where(Message.conversation_id == conversation_id)
    )
    
    await db.delete(conversation)
    await db.commit()
    
    memory_manager = QdrantMemoryManager()
    memory_manager.delete_conversation(str(user_id), conversation_id)
    
    return {"message": "Conversation deleted successfully"}