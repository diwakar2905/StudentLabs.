from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Optional
from database import get_db
from models import Project, Assignment, Presentation, Export, User
from tasks.export_tasks import export_assignment_pdf, export_presentation_pptx
from routes.auth import get_current_user

router = APIRouter()

class ExportPDFRequest(BaseModel):
    project_id: int
    assignment_id: int

class ExportPPTXRequest(BaseModel):
    project_id: int
    presentation_id: int

@router.post("/pdf")
async def export_assignment_pdf_endpoint(
    req: ExportPDFRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export assignment as PDF (async job)"""
    project = db.query(Project).filter(
        Project.id == req.project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    assignment = db.query(Assignment).filter(
        Assignment.id == req.assignment_id,
        Assignment.project_id == req.project_id
    ).first()
    
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # Queue async export job
    task = export_assignment_pdf.delay(req.project_id, req.assignment_id)
    
    return {
        "status": "queued",
        "job_id": task.id,
        "message": "PDF export job queued successfully",
        "poll_url": f"/api/v1/jobs/{task.id}"
    }

@router.post("/pptx")
async def export_presentation_pptx_endpoint(
    req: ExportPPTXRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export presentation as PPTX (async job)"""
    project = db.query(Project).filter(
        Project.id == req.project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    presentation = db.query(Presentation).filter(
        Presentation.id == req.presentation_id,
        Presentation.project_id == req.project_id
    ).first()
    
    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not found")
    
    # Queue async export job
    task = export_presentation_pptx.delay(req.project_id, req.presentation_id)
    
    return {
        "status": "queued",
        "job_id": task.id,
        "message": "PPTX export job queued successfully",
        "poll_url": f"/api/v1/jobs/{task.id}"
    }

@router.get("/{project_id}/downloads")
async def get_project_exports(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all exports for a project"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    exports = db.query(Export).filter(Export.project_id == project_id).all()
    
    return {
        "project_id": project_id,
        "exports_count": len(exports),
        "exports": [
            {
                "id": e.id,
                "file_type": e.file_type,
                "file_path": e.file_path,
                "file_url": e.file_url,
                "created_at": e.created_at
            }
            for e in exports
        ]
    }
