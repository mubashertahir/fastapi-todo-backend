from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api import deps
from app.models.project import Project
from app.models.user import User
from app.schemas.project import ProjectCreate, Project as ProjectSchema, ProjectUpdate
from app.schemas.msg import Msg

router = APIRouter()

@router.get("/", response_model=List[ProjectSchema])
async def read_projects(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    query = select(Project).filter(Project.owner_id == current_user.id, Project.is_deleted == False).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/", response_model=ProjectSchema, status_code=status.HTTP_201_CREATED)
async def create_project(
    *,
    db: AsyncSession = Depends(deps.get_db),
    project_in: ProjectCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    project = Project(
        name=project_in.name,
        description=project_in.description,
        owner_id=current_user.id
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project

@router.put("/{project_id}", response_model=ProjectSchema, status_code=status.HTTP_200_OK)
async def update_project(
    *,
    db: AsyncSession = Depends(deps.get_db),
    project_id: int,
    project_in: ProjectUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    query = select(Project).filter(Project.id == project_id, Project.owner_id == current_user.id, Project.is_deleted == False)
    result = await db.execute(query)
    project = result.scalars().first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    for field, value in project_in.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
        
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project

@router.delete("/{project_id}", status_code=status.HTTP_200_OK, response_model=Msg)
async def delete_project(
    *,
    db: AsyncSession = Depends(deps.get_db),
    project_id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    # Soft delete
    query = select(Project).filter(Project.id == project_id, Project.owner_id == current_user.id, Project.is_deleted == False)
    result = await db.execute(query)
    project = result.scalars().first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    project.is_deleted = True
    db.add(project)
    await db.commit()
    return {"msg": "Project deleted successfully"}
