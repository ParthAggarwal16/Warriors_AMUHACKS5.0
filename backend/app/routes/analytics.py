from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List

from database import get_db
from models import User, Subject, Task, StudySession, TaskStatus
from schemas import DashboardAnalytics, SubjectProgress, TaskResponse
from auth import get_current_user

router = APIRouter()

@router.get("/dashboard", response_model=DashboardAnalytics)
async def get_dashboard_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive dashboard analytics
    """
    # Total subjects
    total_subjects = db.query(Subject).filter(
        Subject.user_id == current_user.id
    ).count()
    
    # Total tasks
    total_tasks = db.query(Task).filter(
        Task.user_id == current_user.id
    ).count()
    
    # Pending tasks
    pending_tasks = db.query(Task).filter(
        Task.user_id == current_user.id,
        Task.status.in_([TaskStatus.PENDING, TaskStatus.IN_PROGRESS])
    ).count()
    
    # Completed tasks
    completed_tasks = db.query(Task).filter(
        Task.user_id == current_user.id,
        Task.status == TaskStatus.COMPLETED
    ).count()
    
    # Total study hours
    total_minutes = db.query(StudySession).filter(
        StudySession.user_id == current_user.id,
        StudySession.end_time != None
    ).with_entities(
        db.func.sum(StudySession.duration_minutes)
    ).scalar() or 0
    
    total_study_hours = total_minutes / 60
    
    # Subject progress
    subjects = db.query(Subject).filter(
        Subject.user_id == current_user.id
    ).all()
    
    subjects_progress = []
    for subject in subjects:
        progress_percentage = (subject.completed_chapters / subject.total_chapters * 100) if subject.total_chapters > 0 else 0
        
        subjects_progress.append(SubjectProgress(
            subject_id=subject.id,
            subject_name=subject.name,
            progress_percentage=round(progress_percentage, 2),
            completed_chapters=subject.completed_chapters,
            total_chapters=subject.total_chapters,
            confidence_score=subject.confidence_score
        ))
    
    # Upcoming deadlines (next 7 days)
    next_week = datetime.utcnow() + timedelta(days=7)
    upcoming_deadlines = db.query(Task).filter(
        Task.user_id == current_user.id,
        Task.status != TaskStatus.COMPLETED,
        Task.deadline <= next_week,
        Task.deadline >= datetime.utcnow()
    ).order_by(Task.deadline).limit(5).all()
    
    return DashboardAnalytics(
        total_subjects=total_subjects,
        total_tasks=total_tasks,
        pending_tasks=pending_tasks,
        completed_tasks=completed_tasks,
        total_study_hours=round(total_study_hours, 2),
        subjects_progress=subjects_progress,
        upcoming_deadlines=upcoming_deadlines
    )

@router.get("/study-time/daily")
async def get_daily_study_time(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    days: int = 7
):
    """
    Get daily study time for the past N days
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    
    sessions = db.query(StudySession).filter(
        StudySession.user_id == current_user.id,
        StudySession.start_time >= start_date,
        StudySession.end_time != None
    ).all()
    
    # Group by date
    daily_stats = {}
    for session in sessions:
        date_key = session.start_time.strftime("%Y-%m-%d")
        if date_key not in daily_stats:
            daily_stats[date_key] = {
                "date": date_key,
                "total_minutes": 0,
                "session_count": 0
            }
        
        daily_stats[date_key]["total_minutes"] += session.duration_minutes or 0
        daily_stats[date_key]["session_count"] += 1
    
    # Convert to list and add hours
    result = []
    for stats in daily_stats.values():
        stats["total_hours"] = round(stats["total_minutes"] / 60, 2)
        result.append(stats)
    
    return sorted(result, key=lambda x: x["date"])

@router.get("/productivity/trend")
async def get_productivity_trend(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    days: int = 14
):
    """
    Get productivity trend over time
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    
    sessions = db.query(StudySession).filter(
        StudySession.user_id == current_user.id,
        StudySession.start_time >= start_date,
        StudySession.end_time != None,
        StudySession.productivity_rating != None
    ).all()
    
    # Group by date
    daily_productivity = {}
    for session in sessions:
        date_key = session.start_time.strftime("%Y-%m-%d")
        if date_key not in daily_productivity:
            daily_productivity[date_key] = {
                "date": date_key,
                "ratings": []
            }
        
        daily_productivity[date_key]["ratings"].append(session.productivity_rating)
    
    # Calculate average
    result = []
    for date, data in daily_productivity.items():
        avg_rating = sum(data["ratings"]) / len(data["ratings"])
        result.append({
            "date": date,
            "average_productivity": round(avg_rating, 2),
            "session_count": len(data["ratings"])
        })
    
    return sorted(result, key=lambda x: x["date"])

@router.get("/subject-time-distribution")
async def get_subject_time_distribution(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    days: int = 30
):
    """
    Get time distribution across subjects
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    
    sessions = db.query(StudySession).filter(
        StudySession.user_id == current_user.id,
        StudySession.start_time >= start_date,
        StudySession.end_time != None,
        StudySession.subject_id != None
    ).all()
    
    # Group by subject
    subject_time = {}
    for session in sessions:
        subject_id = session.subject_id
        if subject_id not in subject_time:
            subject = db.query(Subject).filter(Subject.id == subject_id).first()
            subject_time[subject_id] = {
                "subject_id": subject_id,
                "subject_name": subject.name if subject else "Unknown",
                "total_minutes": 0,
                "session_count": 0
            }
        
        subject_time[subject_id]["total_minutes"] += session.duration_minutes or 0
        subject_time[subject_id]["session_count"] += 1
    
    # Add hours and percentage
    total_minutes = sum(data["total_minutes"] for data in subject_time.values())
    
    result = []
    for data in subject_time.values():
        data["total_hours"] = round(data["total_minutes"] / 60, 2)
        data["percentage"] = round((data["total_minutes"] / total_minutes * 100), 2) if total_minutes > 0 else 0
        result.append(data)
    
    return sorted(result, key=lambda x: x["total_minutes"], reverse=True)

@router.get("/task-completion-rate")
async def get_task_completion_rate(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get task completion statistics
    """
    total_tasks = db.query(Task).filter(
        Task.user_id == current_user.id
    ).count()
    
    completed_tasks = db.query(Task).filter(
        Task.user_id == current_user.id,
        Task.status == TaskStatus.COMPLETED
    ).count()
    
    pending_tasks = db.query(Task).filter(
        Task.user_id == current_user.id,
        Task.status.in_([TaskStatus.PENDING, TaskStatus.IN_PROGRESS])
    ).count()
    
    overdue_tasks = db.query(Task).filter(
        Task.user_id == current_user.id,
        Task.status != TaskStatus.COMPLETED,
        Task.deadline < datetime.utcnow()
    ).count()
    
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    return {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks,
        "overdue_tasks": overdue_tasks,
        "completion_rate": round(completion_rate, 2)
    }