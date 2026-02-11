from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import User, Subject
from schemas import SubjectCreate, SubjectUpdate, SubjectResponse
from auth import get_current_user

router = APIRouter()

@router.post("/", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED)
async def create_subject(
    subject: SubjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new subject
    """
    new_subject = Subject(
        **subject.model_dump(),
        user_id=current_user.id
    )
    
    db.add(new_subject)
    db.commit()
    db.refresh(new_subject)
    
    return new_subject

@router.get("/", response_model=List[SubjectResponse])
async def get_subjects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    Get all subjects for current user
    """
    subjects = db.query(Subject).filter(
        Subject.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return subjects

@router.get("/{subject_id}", response_model=SubjectResponse)
async def get_subject(
    subject_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific subject
    """
    subject = db.query(Subject).filter(
        Subject.id == subject_id,
        Subject.user_id == current_user.id
    ).first()
    
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    
    return subject

@router.put("/{subject_id}", response_model=SubjectResponse)
async def update_subject(
    subject_id: int,
    subject_update: SubjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a subject
    """
    subject = db.query(Subject).filter(
        Subject.id == subject_id,
        Subject.user_id == current_user.id
    ).first()
    
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    
    update_data = subject_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(subject, field, value)
    
    db.commit()
    db.refresh(subject)
    
    return subject

@router.delete("/{subject_id}")
async def delete_subject(
    subject_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a subject
    """
    subject = db.query(Subject).filter(
        Subject.id == subject_id,
        Subject.user_id == current_user.id
    ).first()
    
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    
    db.delete(subject)
    db.commit()
    
    return {"message": "Subject deleted successfully"}

@router.get("/{subject_id}/stats")
async def get_subject_stats(
    subject_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get statistics for a specific subject
    """
    subject = db.query(Subject).filter(
        Subject.id == subject_id,
        Subject.user_id == current_user.id
    ).first()
    
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    
    from models import Task, StudySession
    
    # Get task statistics
    total_tasks = db.query(Task).filter(
        Task.subject_id == subject_id,
        Task.user_id == current_user.id
    ).count()
    
    completed_tasks = db.query(Task).filter(
        Task.subject_id == subject_id,
        Task.user_id == current_user.id,
        Task.status == "completed"
    ).count()
    
    # Get study session statistics
    total_study_hours = db.query(StudySession).filter(
        StudySession.subject_id == subject_id,
        StudySession.user_id == current_user.id
    ).with_entities(
        db.func.sum(StudySession.duration_minutes)
    ).scalar() or 0
    
    return {
        "subject_id": subject_id,
        "subject_name": subject.name,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "total_study_hours": total_study_hours / 60,
        "progress_percentage": (subject.completed_chapters / subject.total_chapters * 100) if subject.total_chapters > 0 else 0,
        "confidence_score": subject.confidence_score
    }