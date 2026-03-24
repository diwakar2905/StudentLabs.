from celery_app import celery_app
from database import SessionLocal
from models import Export, Assignment, Presentation
import json

@celery_app.task(bind=True, max_retries=3)
def export_assignment_pdf(self, project_id: int, assignment_id: int):
    """Async task to export assignment as PDF"""
    db = SessionLocal()
    try:
        assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
        if not assignment:
            return {"error": "Assignment not found", "assignment_id": assignment_id}
        
        # Mock PDF generation
        # In production, use ReportLab to generate actual PDF
        file_path = f"/generated/assignment_{project_id}_{assignment_id}.pdf"
        
        export = Export(
            project_id=project_id,
            file_type="pdf",
            file_path=file_path,
            file_url=f"http://localhost:8000/downloads{file_path}"
        )
        db.add(export)
        db.commit()
        
        return {
            "status": "completed",
            "project_id": project_id,
            "file_type": "pdf",
            "file_path": file_path
        }
    
    except Exception as exc:
        db.rollback()
        raise self.retry(exc=exc, countdown=60)
    
    finally:
        db.close()

@celery_app.task(bind=True, max_retries=3)
def export_presentation_pptx(self, project_id: int, presentation_id: int):
    """Async task to export presentation as PPTX"""
    db = SessionLocal()
    try:
        presentation = db.query(Presentation).filter(Presentation.id == presentation_id).first()
        if not presentation:
            return {"error": "Presentation not found", "presentation_id": presentation_id}
        
        # Mock PPTX generation
        # In production, use python-pptx to generate actual PPTX
        file_path = f"/generated/presentation_{project_id}_{presentation_id}.pptx"
        
        export = Export(
            project_id=project_id,
            file_type="pptx",
            file_path=file_path,
            file_url=f"http://localhost:8000/downloads{file_path}"
        )
        db.add(export)
        db.commit()
        
        return {
            "status": "completed",
            "project_id": project_id,
            "file_type": "pptx",
            "file_path": file_path
        }
    
    except Exception as exc:
        db.rollback()
        raise self.retry(exc=exc, countdown=60)
    
    finally:
        db.close()
