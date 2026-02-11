"""
Pydantic schemas for request/response validation.
Defines data models for API input/output.
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    """Base user schema with common fields"""
    email: EmailStr
    username: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    """Schema for user creation"""
    password: str

class UserUpdate(BaseModel):
    """Schema for user updates"""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None

class UserResponse(UserBase):
    """Schema for user responses"""
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Auth Schemas
class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Schema for JWT token data"""
    username: Optional[str] = None

# Chat Schemas
class ChatMessage(BaseModel):
    """Schema for chat messages"""
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    """Schema for chat responses"""
    response: str
    conversation_id: str
    timestamp: datetime

class StudyPlanRequest(BaseModel):
    """Schema for study plan generation"""
    topic: str
    days_available: int
    hours_per_day: int = 2

class YouTubeRequest(BaseModel):
    """Schema for YouTube recommendations"""
    topic: str
    max_results: int = 5

class SummarizeRequest(BaseModel):
    """Schema for text summarization"""
    text: str
    max_length: int = 300