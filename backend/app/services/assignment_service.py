"""
Assignment service - business logic for assignment generation.

Orchestrates assignment building with RAG pipeline:
1. Load papers from project
2. Retrieve relevant context with FAISS
3. Generate assignment sections with AI
4. Save to database

Follows layering principle: All business logic here, not in routes.
Routes should be thin and just call this service.
"""

from sqlalchemy.orm import Session
from app.models import Project, Assignment, Paper
from app.services.rag_service import get_rag_service
from typing import Optional, Dict
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class AssignmentService:
    """Service for assignment operations - uses RAG for generation."""
    
    @staticmethod
    def generate_assignment(
        db: Session,
        project_id: int,
        user_id: int,
        topic: str = None,
        section_types: list = None
    ) -> Dict:
        """
        Generate an assignment for a project using RAG pipeline.
        
        RAG Pipeline:
        1. Prepare FAISS index (load cached or create new)
        2. Retrieve relevant papers
        3. Generate sections with AI (using prompts.py)
        4. Save assignment to database
        
        Args:
            db: Database session
            project_id: Project ID
            user_id: User ID (for ownership check)
            topic: Topic for assignment (uses project topic if None)
            section_types: Specific sections to generate (None = all)
            
        Returns:
            Dictionary with assignment data or error
        """
        try:
            # Step 1: Validate project ownership
            project = db.query(Project).filter(
                Project.id == project_id,
                Project.user_id == user_id
            ).first()
            
            if not project:
                logger.error(f"Project {project_id} not found for user {user_id}")
                return {"status": "error", "error": "Project not found"}
            
            # Step 2: Validate papers exist
            papers = db.query(Paper).filter(Paper.project_id == project_id).all()
            if not papers:
                logger.error(f"No papers in project {project_id}")
                return {"status": "error", "error": "No papers in project"}
            
            logger.info(f"Generating assignment for project {project_id} ({len(papers)} papers)")
            
            # Step 3: Use RAG service to build assignment
            rag_service = get_rag_service()
            
            assignment_result = rag_service.build_complete_assignment(
                db=db,
                project_id=project_id,
                topic=topic or project.topic,
                user_id=user_id,
                section_types=section_types
            )
            
            if not assignment_result:
                logger.error(f"RAG service failed to generate assignment")
                return {"status": "error", "error": "Assignment generation failed"}
            
            # Step 4: Update project status
            project.status = "completed"
            db.commit()
            
            logger.info(f"✅ Assignment generated successfully (ID: {assignment_result['assignment_id']})")
            
            return {
                "status": "success",
                "assignment": {
                    "id": assignment_result['assignment_id'],
                    "title": assignment_result['title'],
                    "topic": assignment_result['topic'],
                    "word_count": assignment_result['word_count'],
                    "paper_count": assignment_result['paper_count'],
                    "created_at": assignment_result['created_at'],
                    "rag_used": True
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating assignment: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error": str(e)
            }
    
    @staticmethod
    def get_assignment(db: Session, project_id: int) -> Optional[Dict]:
        """Get assignment for a project"""
        assignment = db.query(Assignment).filter(
            Assignment.project_id == project_id
        ).first()
        
        if not assignment:
            return None
        
        return {
            "id": assignment.id,
            "title": assignment.title,
            "content": assignment.content,
            "citations": assignment.citations,
            "word_count": assignment.word_count,
            "rag_used": bool(assignment.rag_used),
            "created_at": assignment.created_at
        }
    
    @staticmethod
    def delete_assignment(db: Session, project_id: int, user_id: int) -> bool:
        """Delete assignment for a project"""
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == user_id
        ).first()
        
        if not project:
            return False
        
        assignment = db.query(Assignment).filter(
            Assignment.project_id == project_id
        ).first()
        
        if assignment:
            db.delete(assignment)
            db.commit()
        
        return True
