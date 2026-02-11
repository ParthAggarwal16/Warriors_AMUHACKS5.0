from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

# Enums
class PriorityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    google_id: Optional[str] = None
    profile_picture: Optional[str] = None

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    default_study_hours_per_day: Optional[float] = None
    learning_pace: Optional[str] = None
    stress_level: Optional[int] = Field(None, ge=1, le=10)

class UserResponse(UserBase):
    id: int
    google_id: Optional[str]
    profile_picture: Optional[str]
    default_study_hours_per_day: float
    learning_pace: str
    stress_level: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Subject Schemas
class SubjectBase(BaseModel):
    name: str
    code: Optional[str] = None
    description: Optional[str] = None
    difficulty_level: Optional[str] = "medium"
    total_chapters: Optional[int] = 0
    credits: Optional[int] = None

class SubjectCreate(SubjectBase):
    pass

class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    difficulty_level: Optional[str] = None
    total_chapters: Optional[int] = None
    completed_chapters: Optional[int] = None
    backlog_level: Optional[int] = Field(None, ge=0, le=100)
    confidence_score: Optional[float] = Field(None, ge=0, le=100)

class SubjectResponse(SubjectBase):
    id: int
    user_id: int
    completed_chapters: int
    backlog_level: int
    confidence_score: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Task Schemas
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    task_type: Optional[str] = None
    subject_id: Optional[int] = None
    priority: Optional[PriorityLevel] = PriorityLevel.MEDIUM
    deadline: Optional[datetime] = None
    estimated_hours: Optional[float] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    task_type: Optional[str] = None
    subject_id: Optional[int] = None
    priority: Optional[PriorityLevel] = None
    status: Optional[TaskStatus] = None
    deadline: Optional[datetime] = None
    estimated_hours: Optional[float] = None
    completed_hours: Optional[float] = None

class TaskResponse(TaskBase):
    id: int
    user_id: int
    status: TaskStatus
    completed_hours: float
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Study Session Schemas
class StudySessionBase(BaseModel):
    subject_id: Optional[int] = None
    start_time: datetime
    session_type: Optional[str] = "focused"

class StudySessionCreate(StudySessionBase):
    pass

class StudySessionUpdate(BaseModel):
    end_time: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    productivity_rating: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = None
    break_count: Optional[int] = None
    total_break_minutes: Optional[int] = None

class StudySessionResponse(StudySessionBase):
    id: int
    user_id: int
    end_time: Optional[datetime]
    duration_minutes: Optional[int]
    productivity_rating: Optional[int]
    notes: Optional[str]
    break_count: int
    total_break_minutes: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[int] = None
    email: Optional[str] = None

class GoogleAuthRequest(BaseModel):
    token: str

# Analytics Schemas
class SubjectProgress(BaseModel):
    subject_id: int
    subject_name: str
    progress_percentage: float
    completed_chapters: int
    total_chapters: int
    confidence_score: float

class DashboardAnalytics(BaseModel):
    total_subjects: int
    total_tasks: int
    pending_tasks: int
    completed_tasks: int
    total_study_hours: float
    subjects_progress: List[SubjectProgress]
    upcoming_deadlines: List[TaskResponse]

# Conversation Schemas
class ConversationCreate(BaseModel):
    agent_type: str
    user_message: str
    context: Optional[dict] = None

class ConversationResponse(BaseModel):
    id: int
    agent_type: str
    user_message: str
    agent_response: str
    context: Optional[dict]
    created_at: datetime
    
    class Config:
        from_attributes = True