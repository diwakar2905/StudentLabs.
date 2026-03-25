"""
Assignment API Routes

REST endpoints for generating and managing academic assignments.
Routes follow the principle: THIN layer calling SERVICES.

All business logic is in AssignmentService and RAGService.
Routes handle: request validation, response formatting, error handling.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
import logging
from datetime import datetime

from app.core.database import get_db
from app.schemas import (
    AssignmentCreate,
    AssignmentResponse,
    AssignmentGenerateRequest,
)
from app.services.assignment_service import AssignmentService
from app.services.rag_service import get_rag_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/projects", tags=["assignments"])


@router.post("/{project_id}/assignments/generate", response_model=dict)
def generate_assignment(
    project_id: int,
    request: AssignmentGenerateRequest,
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = None,
):
    """
    Generate an academic assignment for a project using RAG.
    
    REST Endpoint:
    POST /api/projects/{project_id}/assignments/generate
    
    Request Body:
    {
        "user_id": 123,
        "topic": "Optional custom topic",
        "async": false,  # If true, returns job ID and processes in background
        "section_types": ["abstract", "introduction", "literature"]  # Optional
    }
    
    Response (Sync):
    {
        "status": "success",
        "assignment": {
            "id": 1,
            "title": "RAG Assignment: Topic",
            "topic": "Topic",
            "word_count": 5234,
            "paper_count": 5,
            "created_at": "2024-01-15T10:30:00",
            "rag_used": true
        }
    }
    
    Response (Async):
    {
        "status": "queued",
        "job_id": "abc123",
        "message": "Assignment generation queued"
    }
    """
    try:
        # Validate project and user ownership
        from app.models import Project
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == request.user_id
        ).first()
        
        if not project:
            logger.warning(f"Project {project_id} not found for user {request.user_id}")
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Async generation (queue task)
        if request.async_mode:
            from app.tasks.assignment_tasks import generate_assignment_async
            
            task = generate_assignment_async.delay(
                project_id=project_id,
                user_id=request.user_id,
                topic=request.topic,
                section_types=request.section_types
            )
            
            logger.info(f"Assignment generation queued: job_id={task.id}")
            return {
                "status": "queued",
                "job_id": task.id,
                "message": f"Assignment generation queued. Check /api/jobs/{task.id} for status"
            }
        
        # Sync generation (immediate)
        logger.info(f"Generating assignment synchronously for project {project_id}")
        
        result = AssignmentService.generate_assignment(
            db=db,
            project_id=project_id,
            user_id=request.user_id,
            topic=request.topic,
            section_types=request.section_types
        )
        
        if result["status"] == "error":
            logger.error(f"Assignment generation failed: {result['error']}")
            raise HTTPException(status_code=500, detail=result["error"])
        
        logger.info(f"✅ Assignment generated successfully: {result['assignment']['id']}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error generating assignment: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{project_id}/assignments", response_model=dict)
def get_assignment(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    Get assignment for a project.
    
    REST Endpoint:
    GET /api/projects/{project_id}/assignments
    
    Response:
    {
        "status": "success",
        "assignment": {
            "id": 1,
            "title": "RAG Assignment: Topic",
            "content": {
                "abstract": "...",
                "introduction": "...",
                ...
            },
            "citations": [...],
            "word_count": 5234,
            "rag_used": true,
            "created_at": "2024-01-15T10:30:00"
        }
    }
    """
    try:
        from app.models import Assignment
        
        assignment = db.query(Assignment).filter(
            Assignment.project_id == project_id
        ).first()
        
        if not assignment:
            raise HTTPException(status_code=404, detail="No assignment found for this project")
        
        return {
            "status": "success",
            "assignment": {
                "id": assignment.id,
                "title": assignment.title,
                "content": assignment.content,
                "citations": assignment.citations or [],
                "word_count": assignment.word_count,
                "rag_used": bool(assignment.rag_used),
                "created_at": assignment.created_at.isoformat()
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving assignment: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{project_id}/assignments")
def delete_assignment(
    project_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete assignment for a project.
    
    REST Endpoint:
    DELETE /api/projects/{project_id}/assignments?user_id={user_id}
    
    Response:
    {
        "status": "success",
        "message": "Assignment deleted"
    }
    """
    try:
        success = AssignmentService.delete_assignment(
            db=db,
            project_id=project_id,
            user_id=user_id
        )
        
        if not success:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        return {
            "status": "success",
            "message": "Assignment deleted"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting assignment: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{project_id}/rag-stats", response_model=dict)
def get_rag_stats(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    Get RAG pipeline statistics for a project.
    
    REST Endpoint:
    GET /api/projects/{project_id}/rag-stats
    
    Response:
    {
        "status": "success",
        "stats": {
            "project_id": 123,
            "papers_indexed": 50,
            "assignments_generated": 3,
            "embeddings_stored": 50,
            "index_cached": true
        }
    }
    """
    try:
        rag_service = get_rag_service()
        stats = rag_service.get_project_stats(db, project_id)
        
        # Check if index is cached on disk
        from ai_engine.retriever import load_index
        index_cached = load_index(project_id)
        
        stats['index_cached'] = index_cached
        
        return {
            "status": "success",
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Error getting RAG stats: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{project_id}/rag-index/refresh")
def refresh_rag_index(
    project_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Force refresh of FAISS index for a project.
    
    Useful when papers are added/updated.
    
    REST Endpoint:
    POST /api/projects/{project_id}/rag-index/refresh
    
    Response:
    {
        "status": "success",
        "message": "Index refreshed",
        "papers_indexed": 50
    }
    """
    try:
        # Verify ownership
        from app.models import Project
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == user_id
        ).first()
        
        if not project:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        rag_service = get_rag_service()
        success, msg = rag_service.prepare_project_index(
            db=db,
            project_id=project_id,
            force_refresh=True
        )
        
        if not success:
            raise HTTPException(status_code=500, detail=msg)
        
        stats = rag_service.get_project_stats(db, project_id)
        
        return {
            "status": "success",
            "message": "Index refreshed",
            "papers_indexed": stats.get("papers_indexed", 0)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error refreshing index: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
