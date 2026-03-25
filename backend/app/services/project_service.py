"""
Project service - business logic for project management.
Handles CRUD operations and project metadata.
"""

from sqlalchemy.orm import Session
from app.models import Project, User
from typing import List, Optional


class ProjectService:
    """Service for project-related business logic"""
    
    @staticmethod
    def create_project(db: Session, user_id: int, title: str, topic: str) -> Project:
        """
        Create a new project
        
        Args:
            db: Database session
            user_id: Owner user ID
            title: Project title
            topic: Project topic
            
        Returns:
            Created Project object
        """
        project = Project(
            user_id=user_id,
            title=title,
            topic=topic,
            status="draft"
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        return project
    
    @staticmethod
    def get_project_by_id(db: Session, project_id: int, user_id: int) -> Optional[Project]:
        """Get project by ID, checking user ownership"""
        return db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == user_id
        ).first()
    
    @staticmethod
    def list_user_projects(db: Session, user_id: int) -> List[Project]:
        """List all projects for a user"""
        return db.query(Project).filter(Project.user_id == user_id).all()
    
    @staticmethod
    def update_project(
        db: Session,
        project_id: int,
        user_id: int,
        title: Optional[str] = None,
        topic: Optional[str] = None,
        status: Optional[str] = None
    ) -> Optional[Project]:
        """
        Update a project
        
        Returns:
            Updated Project object or None if not found
        """
        project = ProjectService.get_project_by_id(db, project_id, user_id)
        if not project:
            return None
        
        if title is not None:
            project.title = title
        if topic is not None:
            project.topic = topic
        if status is not None:
            project.status = status
        
        db.commit()
        db.refresh(project)
        return project
    
    @staticmethod
    def delete_project(db: Session, project_id: int, user_id: int) -> bool:
        """
        Delete a project
        
        Returns:
            True if deleted, False if not found
        """
        project = ProjectService.get_project_by_id(db, project_id, user_id)
        if not project:
            return False
        
        db.delete(project)
        db.commit()
        return True
    
    @staticmethod
    def get_project_detail(db: Session, project_id: int, user_id: int) -> Optional[dict]:
        """Get project detail with counts"""
        project = ProjectService.get_project_by_id(db, project_id, user_id)
        if not project:
            return None
        
        return {
            "id": project.id,
            "title": project.title,
            "topic": project.topic,
            "status": project.status,
            "created_at": project.created_at,
            "updated_at": project.updated_at,
            "papers_count": len(project.papers) if project.papers else 0,
            "has_assignment": project.assignment is not None,
            "has_presentation": project.presentation is not None,
            "exports_count": len(project.exports) if project.exports else 0,
        }
