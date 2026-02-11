from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from database import get_db
from models import User, StudySession
from schemas import StudySessionCreate, StudySessionUpdate, StudySessionResponse
from auth import get_current_user

router = APIRouter()

@router.post("/", response_model=StudySessionResponse, status_code=status.HTTP_201_CREATED)
async def create_study_session(
    session: StudySessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new study session (start a session)
    """
    new_session = StudySession(
        **session.model_dump(),
        user_id=current_user.id
    )
    
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    
    return new_session

@router.get("/", response_model=List[StudySessionResponse])
async def get_study_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    subject_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100
):
    """
    Get all study sessions for current user
    """
    query = db.query(StudySession).filter(StudySession.user_id == current_user.id)
    
    if subject_id:
        query = query.filter(StudySession.subject_id == subject_id)
    
    sessions = query.order_by(StudySession.start_time.desc()).offset(skip).limit(limit).all()
    
    return sessions

@router.get("/active", response_model=Optional[StudySessionResponse])
async def get_active_session(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get currently active study session (if any)
    """
    active_session = db.query(StudySession).filter(
        StudySession.user_id == current_user.id,
        StudySession.end_time == None
    ).order_by(StudySession.start_time.desc()).first()
    
    return active_session

@router.get("/today", response_model=List[StudySessionResponse])
async def get_today_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get today's study sessions
    """
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    
    sessions = db.query(StudySession).filter(
        StudySession.user_id == current_user.id,
        StudySession.start_time >= today_start,
        StudySession.start_time < today_end
    ).order_by(StudySession.start_time.desc()).all()
    
    return sessions

@router.get("/{session_id}", response_model=StudySessionResponse)
async def get_study_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific study session
    """
    session = db.query(StudySession).filter(
        StudySession.id == session_id,
        StudySession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study session not found"
        )
    
    return session

@router.put("/{session_id}", response_model=StudySessionResponse)
async def update_study_session(
    session_id: int,
    session_update: StudySessionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a study session
    """
    session = db.query(StudySession).filter(
        StudySession.id == session_id,
        StudySession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study session not found"
        )
    
    update_data = session_update.model_dump(exclude_unset=True)
    
    # If end_time is being set, calculate duration
    if "end_time" in update_data and update_data["end_time"]:
        duration = (update_data["end_time"] - session.start_time).total_seconds() / 60
        update_data["duration_minutes"] = int(duration)
    
    for field, value in update_data.items():
        setattr(session, field, value)
    
    db.commit()
    db.refresh(session)
    
    return session

@router.post("/{session_id}/end", response_model=StudySessionResponse)
async def end_study_session(
    session_id: int,
    productivity_rating: Optional[int] = None,
    notes: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    End a study session
    """
    session = db.query(StudySession).filter(
        StudySession.id == session_id,
        StudySession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study session not found"
        )
    
    if session.end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session already ended"
        )
    
    session.end_time = datetime.utcnow()
    duration = (session.end_time - session.start_time).total_seconds() / 60
    session.duration_minutes = int(duration)
    
    if productivity_rating:
        session.productivity_rating = productivity_rating
    
    if notes:
        session.notes = notes
    
    db.commit()
    db.refresh(session)
    
    return session

@router.delete("/{session_id}")
async def delete_study_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a study session
    """
    session = db.query(StudySession).filter(
        StudySession.id == session_id,
        StudySession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study session not found"
        )
    
    db.delete(session)
    db.commit()
    
    return {"message": "Study session deleted successfully"}

@router.get("/stats/weekly")
async def get_weekly_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get study statistics for the past week
    """
    week_ago = datetime.utcnow() - timedelta(days=7)
    
    sessions = db.query(StudySession).filter(
        StudySession.user_id == current_user.id,
        StudySession.start_time >= week_ago,
        StudySession.end_time != None
    ).all()
    
    total_minutes = sum(s.duration_minutes or 0 for s in sessions)
    total_breaks = sum(s.break_count for s in sessions)
    avg_productivity = sum(s.productivity_rating or 0 for s in sessions if s.productivity_rating) / len(sessions) if sessions else 0
    
    return {
        "total_sessions": len(sessions),
        "total_hours": total_minutes / 60,
        "total_breaks": total_breaks,
        "average_productivity": round(avg_productivity, 2),
        "sessions": sessions
    }