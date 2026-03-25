"""
Celery Tasks - Async Processing

Long-running operations are queued as Celery tasks:
- Assignment generation
- Document export
- Paper summarization

Each task:
- Runs in background worker
- Reports progress to Redis
- Retries on failure
- Logs all operations
"""

import logging
from typing import Optional, List, Dict
from datetime import datetime

logger = logging.getLogger(__name__)

# Import will be done lazily to avoid import errors if celery not configured
_celery_app = None


def get_celery_app():
    """Get or initialize Celery app"""
    global _celery_app
    if _celery_app is None:
        try:
            from backend.celery_app import celery
            _celery_app = celery
        except ImportError:
            logger.warning("Celery not initialized. Tasks will run synchronously.")
            return None
    return _celery_app


# Task 1: Generate Assignment Async
@staticmethod
def setup_assignment_generation_task():
    """Setup the async assignment generation task"""
    celery = get_celery_app()
    if not celery:
        logger.warning("Celery not available, task registration skipped")
        return None
    
    @celery.task(bind=True, max_retries=3)
    def generate_assignment_async(
        self,
        project_id: int,
        user_id: int,
        topic: Optional[str] = None,
        section_types: Optional[List[str]] = None
    ):
        """
        Async task: Generate assignment for project using RAG.
        
        Celery Task:
        - Queue Name: assignments
        - Retry: 3 times on failure
        - Timeout: 3600 seconds (1 hour)
        - Progress Updates: Via task.update_state()
        
        Args:
            project_id: Project ID
            user_id: User ID
            topic: Optional custom topic
            section_types: Optional list of sections to generate
        
        Returns:
            Dict with assignment data
        """
        try:
            # Update task state: running
            self.update_state(
                state='PROGRESS',
                meta={'current': 0, 'total': 100, 'status': 'Initializing...'}
            )
            
            # Import here to avoid circular imports
            from app.core.database import SessionLocal
            from app.services.assignment_service import AssignmentService
            
            db = SessionLocal()
            
            try:
                logger.info(f"Starting async assignment generation: project={project_id}, user={user_id}")
                
                # Update progress
                self.update_state(
                    state='PROGRESS',
                    meta={'current': 10, 'total': 100, 'status': 'Validating project...'}
                )
                
                # Call service
                result = AssignmentService.generate_assignment(
                    db=db,
                    project_id=project_id,
                    user_id=user_id,
                    topic=topic,
                    section_types=section_types
                )
                
                if result["status"] == "error":
                    logger.error(f"Assignment generation failed: {result['error']}")
                    raise Exception(result["error"])
                
                logger.info(f"✅ Assignment generated: {result['assignment']['id']}")
                
                # Return result
                return {
                    "status": "success",
                    "assignment": result["assignment"]
                }
                
            finally:
                db.close()
        
        except Exception as exc:
            logger.error(f"Error in async assignment generation: {str(exc)}", exc_info=True)
            
            # Retry logic
            if self.request.retries < self.max_retries:
                logger.info(f"Retrying task... (attempt {self.request.retries + 1}/{self.max_retries})")
                raise self.retry(exc=exc, countdown=60)
            else:
                logger.error(f"Task failed after {self.max_retries} retries")
                return {
                    "status": "failed",
                    "error": str(exc)
                }
    
    return generate_assignment_async


# Task 2: Export Assignment to PDF
@staticmethod
def setup_export_pdf_task():
    """Setup the async PDF export task"""
    celery = get_celery_app()
    if not celery:
        return None
    
    @celery.task(bind=True, max_retries=2)
    def export_assignment_pdf(
        self,
        assignment_id: int,
        user_id: int
    ):
        """
        Async task: Export assignment to PDF.
        
        Args:
            assignment_id: Assignment ID
            user_id: User ID
        
        Returns:
            Dict with file path
        """
        try:
            self.update_state(
                state='PROGRESS',
                meta={'current': 0, 'total': 100, 'status': 'Exporting to PDF...'}
            )
            
            from app.core.database import SessionLocal
            from app.services.export_service import ExportService
            
            db = SessionLocal()
            
            try:
                logger.info(f"Exporting assignment {assignment_id} to PDF")
                
                result = ExportService.export_to_pdf(
                    db=db,
                    assignment_id=assignment_id,
                    user_id=user_id
                )
                
                if not result:
                    raise Exception("PDF export failed")
                
                logger.info(f"✅ PDF exported: {result}")
                return {"status": "success", "file_path": result}
                
            finally:
                db.close()
        
        except Exception as exc:
            logger.error(f"Error exporting PDF: {str(exc)}", exc_info=True)
            
            if self.request.retries < self.max_retries:
                raise self.retry(exc=exc, countdown=30)
            else:
                return {"status": "failed", "error": str(exc)}
    
    return export_assignment_pdf


# Task 3: Summarize Papers
@staticmethod
def setup_summarize_papers_task():
    """Setup the async paper summarization task"""
    celery = get_celery_app()
    if not celery:
        return None
    
    @celery.task(bind=True, max_retries=2)
    def summarize_project_papers(
        self,
        project_id: int,
        user_id: int
    ):
        """
        Async task: Summarize all papers in project.
        
        Args:
            project_id: Project ID
            user_id: User ID
        
        Returns:
            Dict with summary status
        """
        try:
            from app.core.database import SessionLocal
            from app.services.research_service import ResearchService
            
            db = SessionLocal()
            
            try:
                logger.info(f"Summarizing papers for project {project_id}")
                
                summarized_count = ResearchService.summarize_papers(
                    db=db,
                    project_id=project_id,
                    user_id=user_id
                )
                
                logger.info(f"✅ {summarized_count} papers summarized")
                return {
                    "status": "success",
                    "papers_summarized": summarized_count
                }
                
            finally:
                db.close()
        
        except Exception as exc:
            logger.error(f"Error summarizing papers: {str(exc)}", exc_info=True)
            
            if self.request.retries < self.max_retries:
                raise self.retry(exc=exc, countdown=30)
            else:
                return {"status": "failed", "error": str(exc)}
    
    return summarize_project_papers


# Initialize all tasks
class TaskRegistry:
    """Registry of all Celery tasks"""
    
    @staticmethod
    def register_all_tasks():
        """Register all tasks with Celery app"""
        celery = get_celery_app()
        if not celery:
            logger.warning("Celery not available, skipping task registration")
            return
        
        logger.info("Registering Celery tasks...")
        
        # Register tasks
        assignments_task = setup_assignment_generation_task()
        pdf_task = setup_export_pdf_task()
        summarize_task = setup_summarize_papers_task()
        
        if assignments_task:
            celery.register_task(assignments_task)
        if pdf_task:
            celery.register_task(pdf_task)
        if summarize_task:
            celery.register_task(summarize_task)
        
        logger.info("✅ Tasks registered successfully")


# Convenience functions for easy import
def get_assignment_task():
    """Get assignment generation task"""
    return setup_assignment_generation_task()


def get_export_pdf_task():
    """Get PDF export task"""
    return setup_export_pdf_task()


def get_summarize_task():
    """Get summarization task"""
    return setup_summarize_papers_task()
