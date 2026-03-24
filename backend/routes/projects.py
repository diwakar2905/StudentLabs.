from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from database import get_db
from models import Project, User, Paper, Assignment, Presentation, Export
from routes.auth import get_current_user

router = APIRouter()

# Pydantic schemas
class ProjectCreate(BaseModel):
    title: str
    topic: str

class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    topic: Optional[str] = None
    status: Optional[str] = None

class ProjectResponse(BaseModel):
    id: int
    title: str
    topic: str
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ProjectDetailResponse(ProjectResponse):
    papers_count: int = 0
    has_assignment: bool = False
    has_presentation: bool = False
    exports_count: int = 0

# CRUD Operations
@router.post("/", response_model=ProjectResponse)
async def create_project(project: ProjectCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Create a new project"""
    db_project = Project(
        user_id=current_user.id,
        title=project.title,
        topic=project.topic,
        status="draft"
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@router.get("/", response_model=List[ProjectResponse])
async def list_projects(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """List all projects for the current user"""
    projects = db.query(Project).filter(Project.user_id == current_user.id).all()
    return projects

@router.get("/{project_id}", response_model=ProjectDetailResponse)
async def get_project(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get project details"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return {
        **project.__dict__,
        "papers_count": len(project.papers),
        "has_assignment": project.assignment is not None,
        "has_presentation": project.presentation is not None,
        "exports_count": len(project.exports)
    }

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: int, project_update: ProjectUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Update project"""
    db_project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project_update.title is not None:
        db_project.title = project_update.title
    if project_update.topic is not None:
        db_project.topic = project_update.topic
    if project_update.status is not None:
        db_project.status = project_update.status
    
    db_project.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_project)
    return db_project

@router.delete("/{project_id}")
async def delete_project(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Delete project"""
    db_project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.delete(db_project)
    db.commit()
    return {"message": "Project deleted successfully"}

@router.get("/{project_id}/papers", response_model=List[dict])
async def get_project_papers(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get papers in a project"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return [
        {
            "id": p.id,
            "paper_id": p.paper_id,
            "title": p.title,
            "authors": p.authors,
            "year": p.year,
            "url": p.url
        }
        for p in project.papers
    ]
