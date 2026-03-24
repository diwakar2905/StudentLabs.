from celery_app import celery_app
from database import SessionLocal
from models import Project, Assignment, Presentation, Paper
from datetime import datetime
import json
from ai_engine.assignment_builder import build_assignment

@celery_app.task(bind=True, max_retries=3)
def generate_assignment_async(self, project_id: int):
    """Async task to generate assignment"""
    db = SessionLocal()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return {"error": "Project not found", "project_id": project_id}
        
        # Get papers
        papers = db.query(Paper).filter(Paper.project_id == project_id).all()
        if not papers:
            return {"error": "No papers found", "project_id": project_id}
        
        # Use AI Engine to generate assignment
        assignment_data = build_assignment(project.topic, papers)
        
        assignment_title = assignment_data["title"]
        assignment_content = assignment_data["content"]
        citations = assignment_data["citations"]
        
        # Save assignment
        existing_assignment = db.query(Assignment).filter(
            Assignment.project_id == project_id
        ).first()
        
        if existing_assignment:
            existing_assignment.title = assignment_title
            existing_assignment.content = assignment_content
            existing_assignment.citations = citations
        else:
            assignment = Assignment(
                project_id=project_id,
                title=assignment_title,
                content=assignment_content,
                citations=citations
            )
            db.add(assignment)
        
        db.commit()
        
        return {
            "status": "completed",
            "project_id": project_id,
            "title": assignment_title,
            "word_count": len(assignment_content.split()),
            "citations_count": len(papers)
        }
    
    except Exception as exc:
        db.rollback()
        # Retry on error
        raise self.retry(exc=exc, countdown=60)
    
    finally:
        db.close()

@celery_app.task(bind=True, max_retries=3)
def generate_presentation_async(self, project_id: int):
    """Async task to generate presentation"""
    db = SessionLocal()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return {"error": "Project not found", "project_id": project_id}
        
        papers = db.query(Paper).filter(Paper.project_id == project_id).all()
        
        slides = [
            {
                "slide_number": 1,
                "title": project.topic,
                "layout": "title",
                "content": "Introduction and Overview",
                "speaker_notes": f"Welcome to this presentation on {project.topic}."
            },
            {
                "slide_number": 2,
                "title": "Literature Review",
                "layout": "bullet",
                "content": [
                    f"Analysis of {len(papers)} research papers",
                    "Key findings from the literature",
                    "Common themes and patterns"
                ],
                "speaker_notes": "Recent research in this field has revealed important insights."
            },
            {
                "slide_number": 3,
                "title": "Conclusion",
                "layout": "title",
                "content": "Summary and Future Directions",
                "speaker_notes": "Thank you for your attention."
            }
        ]
        
        # Save presentation
        existing_ppt = db.query(Presentation).filter(
            Presentation.project_id == project_id
        ).first()
        
        if existing_ppt:
            existing_ppt.slides_json = slides
        else:
            presentation = Presentation(
                project_id=project_id,
                slides_json=slides
            )
            db.add(presentation)
        
        db.commit()
        
        return {
            "status": "completed",
            "project_id": project_id,
            "slides_count": len(slides)
        }
    
    except Exception as exc:
        db.rollback()
        raise self.retry(exc=exc, countdown=60)
    
    finally:
        db.close()

@celery_app.task
def check_pending_tasks():
    """Check and process pending tasks"""
    return {"status": "checked", "timestamp": datetime.utcnow().isoformat()}
