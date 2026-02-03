from typing import Any, List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api import deps
from app.models.task import Task
from app.models.project import Project
from app.models.user import User
from app.schemas.task import TaskCreate, Task as TaskSchema, TaskUpdate
from app.schemas.msg import Msg

router = APIRouter()

def send_email_notification(email: str, message: str):
    # Dummy email sender
    print(f"SENDING EMAIL TO {email}: {message}")

@router.get("/", response_model=List[TaskSchema])
async def read_tasks(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    project_id: int = None,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    query = select(Task).filter(Task.owner_id == current_user.id, Task.is_deleted == False)
    if project_id:
        query = query.filter(Task.project_id == project_id)
        
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/", response_model=TaskSchema, status_code=status.HTTP_201_CREATED)
async def create_task(
    *,
    db: AsyncSession = Depends(deps.get_db),
    task_in: TaskCreate,
    current_user: User = Depends(deps.get_current_user),
    background_tasks: BackgroundTasks,
) -> Any:
    if task_in.project_id is not None:
        result = await db.execute(select(Project).filter(Project.id == task_in.project_id, Project.owner_id == current_user.id))
        project = result.scalars().first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

    task = Task(
        title=task_in.title,
        description=task_in.description,
        status=task_in.status,
        priority=task_in.priority,
        due_date=task_in.due_date,
        project_id=task_in.project_id,
        owner_id=current_user.id
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)

    if task.due_date:
        now = datetime.now(task.due_date.tzinfo)
        if now < task.due_date < now + timedelta(days=1):
            background_tasks.add_task(send_email_notification, current_user.email, f"Task '{task.title}' created and is due soon (tomorrow)!")

    return task

@router.put("/{task_id}", response_model=TaskSchema, status_code=status.HTTP_200_OK)
async def update_task(
    *,
    db: AsyncSession = Depends(deps.get_db),
    task_id: int,
    task_in: TaskUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    query = select(Task).filter(Task.id == task_id, Task.is_deleted == False)
    result = await db.execute(query)
    task = result.scalars().first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this task")

    if task_in.project_id is not None:
        result = await db.execute(select(Project).filter(Project.id == task_in.project_id, Project.owner_id == current_user.id))
        project = result.scalars().first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

    for field, value in task_in.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
        
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task

@router.delete("/{task_id}", status_code=status.HTTP_200_OK, response_model=Msg)
async def delete_task(
    *,
    db: AsyncSession = Depends(deps.get_db),
    task_id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    query = select(Task).filter(Task.id == task_id, Task.owner_id == current_user.id, Task.is_deleted == False)
    result = await db.execute(query)
    task = result.scalars().first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    task.is_deleted = True
    db.add(task)
    await db.commit()
    return {"msg": "Task deleted successfully"}
