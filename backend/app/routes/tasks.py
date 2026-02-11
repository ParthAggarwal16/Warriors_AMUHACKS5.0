from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database import get_db
from models import User, Task, TaskStatus
from schemas import TaskCreate, TaskUpdate, TaskResponse
from auth import get_current_user

router = APIRouter()

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new task
    """
    new_task = Task(
        **task.model_dump(),
        user_id=current_user.id
    )
    
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    
    return new_task

@router.get("/", response_model=List[TaskResponse])
async def get_tasks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    status_filter: Optional[str] = None,
    subject_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100
):
    """
    Get all tasks for current user with optional filters
    """
    query = db.query(Task).filter(Task.user_id == current_user.id)
    
    if status_filter:
        query = query.filter(Task.status == status_filter)
    
    if subject_id:
        query = query.filter(Task.subject_id == subject_id)
    
    tasks = query.order_by(Task.deadline).offset(skip).limit(limit).all()
    
    return tasks

@router.get("/upcoming", response_model=List[TaskResponse])
async def get_upcoming_tasks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    days: int = 7
):
    """
    Get upcoming tasks within specified days
    """
    from datetime import timedelta
    
    end_date = datetime.utcnow() + timedelta(days=days)
    
    tasks = db.query(Task).filter(
        Task.user_id == current_user.id,
        Task.status != TaskStatus.COMPLETED,
        Task.deadline <= end_date,
        Task.deadline >= datetime.utcnow()
    ).order_by(Task.deadline).all()
    
    return tasks

@router.get("/overdue", response_model=List[TaskResponse])
async def get_overdue_tasks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all overdue tasks
    """
    tasks = db.query(Task).filter(
        Task.user_id == current_user.id,
        Task.status != TaskStatus.COMPLETED,
        Task.deadline < datetime.utcnow()
    ).order_by(Task.deadline).all()
    
    # Update status to overdue
    for task in tasks:
        task.status = TaskStatus.OVERDUE
    
    db.commit()
    
    return tasks

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific task
    """
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return task

@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a task
    """
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    update_data = task_update.model_dump(exclude_unset=True)
    
    # If status is being changed to completed, set completed_at
    if "status" in update_data and update_data["status"] == TaskStatus.COMPLETED:
        update_data["completed_at"] = datetime.utcnow()
    
    for field, value in update_data.items():
        setattr(task, field, value)
    
    db.commit()
    db.refresh(task)
    
    return task

@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a task
    """
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    db.delete(task)
    db.commit()
    
    return {"message": "Task deleted successfully"}

@router.post("/{task_id}/complete", response_model=TaskResponse)
async def complete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark a task as completed
    """
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    task.status = TaskStatus.COMPLETED
    task.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(task)
    
    return task