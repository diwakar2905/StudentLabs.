from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from database import get_db
from models import Project, Assignment, Presentation, User, Paper
from datetime import datetime
import json
from tasks.generation_tasks import generate_assignment_async, generate_presentation_async
from celery_app import celery_app
from routes.auth import get_current_user

router = APIRouter()

class AssignmentRequest(BaseModel):
    project_id: int
    paper_ids: Optional[List[str]] = None

class AssignmentUpdateRequest(BaseModel):
    title: str
    content: str
    citations: Optional[dict] = None

class PPTRequest(BaseModel):
    project_id: int
    assignment_id: Optional[int] = None

class PPTSlide(BaseModel):
    title: str
    content: str
    speaker_notes: Optional[str] = None

class PPTUpdateRequest(BaseModel):
    slides: List[PPTSlide]

# Helper to get current user
def get_current_user_dep() -> int:
    # This is now handled by the import from auth.py
    return None

@router.post("/{project_id}/assignment", response_model=dict)
async def generate_assignment(
    project_id: int,
    req: AssignmentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate high-quality assignment for a project"""
    # Verify project belongs to user
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Update project status
    project.status = "in_progress"
    
    # Get papers for the project (or use provided paper IDs)
    if req.paper_ids:
        papers = db.query(Paper).filter(
            Paper.project_id == project_id,
            Paper.paper_id.in_(req.paper_ids)
        ).all()
    else:
        papers = db.query(Paper).filter(Paper.project_id == project_id).all()
    
    if not papers:
        raise HTTPException(status_code=400, detail="No papers found for this project")
    
    # Generate high-quality assignment with better structure
    assignment_title = f"Comprehensive Analysis: {project.topic}"
    
    # Build literature review section
    literature_review = f"""### Literature Review
Based on analysis of {len(papers)} peer-reviewed publications, significant progress has been made in {project.topic}. The research landscape reveals:

**Key Thematic Areas:**
"""
    for i, paper in enumerate(papers, 1):
        literature_review += f"\n{i}. {paper.title} ({paper.authors}, {paper.year})"
        literature_review += f"\n   - {paper.abstract[:150]}..."
    
    # Build full assignment content
    assignment_content = f"""# {assignment_title}

## Executive Summary
This assignment synthesizes current research in "{project.topic}" through comprehensive analysis of peer-reviewed literature. The document provides structured insights into methodologies, findings, and future directions in this field.

## 1. Introduction
The field of {project.topic} has witnessed significant evolution. This analysis examines the current state of research, identifies key findings, and discusses implications for future work.

## 2. {literature_review}

## 3. Methodology Synthesis
The reviewed papers employ diverse methodological approaches:
- Empirical research designs
- Systematic literature reviews
- Computational modeling
- Qualitative analysis

## 4. Key Findings
The research demonstrates:
1. Significant advancement in understanding core concepts
2. Novel methodologies improving existing approaches
3. Practical applications with measurable outcomes
4. Interdisciplinary connections and implications

## 5. Critical Analysis
**Strengths of Current Research:**
- Rigorous methodological approaches
- Reproducible results across studies
- Clear practical applications

**Limitations and Gaps:**
- Need for longitudinal studies
- Limited interdisciplinary collaboration in some areas
- Emerging technologies requiring further investigation

## 6. Implications and Recommendations
Based on the literature review, several recommendations emerge:
1. Further research into emerging methodologies
2. Cross-disciplinary collaboration opportunities
3. Translation of findings into practical applications
4. Development of standardized assessment frameworks

## 7. Future Directions
The field shows promise in several areas:
- Integration of artificial intelligence and machine learning
- Scalability of current methodologies
- Real-world implementation strategies
- Ethical considerations in application

## 8. Conclusion
The research in {project.topic} demonstrates both maturity and exciting potential for future development. This analysis provides a foundation for continued scholarly investigation and practical application.

## References
"""
    
    # Build citations in proper academic format
    citations_list = []
    for paper in papers:
        citation = f"{paper.authors} ({paper.year}). {paper.title}."
        if paper.url:
            citation += f" Retrieved from {paper.url}"
        citations_list.append(citation)
        assignment_content += f"\n{citation}\n"
    
    citations = {
        "papers": [
            {
                "id": p.paper_id,
                "title": p.title,
                "authors": p.authors,
                "year": p.year,
                "citation": f"{p.authors} ({p.year}). {p.title}.",
                "url": p.url
            }
            for p in papers
        ],
        "count": len(papers)
    }
    
   # Save or update assignment
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
        "status": "success",
        "project_id": project_id,
        "title": assignment_title,
        "preview": assignment_content[:500] + "...",
        "citations_count": len(papers),
        "word_count": len(assignment_content.split()),
        "message": "High-quality assignment generated successfully"
    }


@router.put("/{project_id}/assignment")
async def update_assignment(
    project_id: int,
    req: AssignmentUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update assignment content"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    assignment = db.query(Assignment).filter(
        Assignment.project_id == project_id
    ).first()
    
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    assignment.title = req.title
    assignment.content = req.content
    if req.citations:
        assignment.citations = req.citations
    
    db.commit()
    return {"status": "success", "message": "Assignment updated"}

@router.post("/{project_id}/ppt")
async def generate_ppt(
    project_id: int,
    req: PPTRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate presentation for a project"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == user_id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get assignment content if available
    assignment = db.query(Assignment).filter(
        Assignment.project_id == project_id
    ).first()
    
    # Generate presentation slides (mock AI call)
    slides = [
        {
            "slide_number": 1,
            "title": project.topic,
            "layout": "title",
            "content": "Introduction and Overview",
            "speaker_notes": f"Welcome to this presentation on {project.topic}. Today we'll explore key concepts and findings."
        },
        {
            "slide_number": 2,
            "title": "Key Concepts",
            "layout": "bullet",
            "content": [
                "Definition and scope of the topic",
                "Historical context",
                "Recent developments"
            ],
            "speaker_notes": "These are the foundational concepts we need to understand."
        },
        {
            "slide_number": 3,
            "title": "Literature Review",
            "layout": "bullet",
            "content": [
                "Analysis of {} research papers".format(len(project.papers)) if project.papers else "Current research landscape",
                "Key findings from the literature",
                "Common themes and patterns"
            ],
            "speaker_notes": "Recent research in this field has revealed important insights."
        },
        {
            "slide_number": 4,
            "title": "Key Findings",
            "layout": "bullet",
            "content": [
                "Main discovery 1",
                "Main discovery 2",
                "Main discovery 3"
            ],
            "speaker_notes": "These findings have significant implications for the field."
        },
        {
            "slide_number": 5,
            "title": "Conclusion",
            "layout": "title",
            "content": "Summary and Future Directions",
            "speaker_notes": "Thank you for your attention. Let's open the floor for questions."
        }
    ]
    
    # Save or update presentation
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
        "status": "success",
        "project_id": project_id,
        "slides_count": len(slides),
        "slides": slides,
        "message": "Presentation generated successfully"
    }

@router.put("/{project_id}/ppt")
async def update_ppt(
    project_id: int,
    req: PPTUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update presentation slides"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    presentation = db.query(Presentation).filter(
        Presentation.project_id == project_id
    ).first()
    
    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not found")
    
    # Convert slides to JSON format
    slides_data = [slide.dict() for slide in req.slides]
    presentation.slides_json = slides_data
    
    db.commit()
    return {"status": "success", "message": "Presentation updated"}

@router.get("/{project_id}/assignment")
async def get_assignment(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get assignment for a project"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    assignment = db.query(Assignment).filter(
        Assignment.project_id == project_id
    ).first()
    
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not generated yet")
    
    return {
        "id": assignment.id,
        "title": assignment.title,
        "content": assignment.content,
        "citations": assignment.citations,
        "created_at": assignment.created_at
    }

@router.get("/{project_id}/ppt")
async def get_ppt(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get presentation for a project"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == user_id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    presentation = db.query(Presentation).filter(
        Presentation.project_id == project_id
    ).first()
    
    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not generated yet")
    
    return {
        "id": presentation.id,
        "slides": presentation.slides_json,
        "slides_count": len(presentation.slides_json) if presentation.slides_json else 0,
        "created_at": presentation.created_at
    }

# Async job endpoints

@router.post("/{project_id}/assignment-async", response_model=dict)
async def generate_assignment_async_endpoint(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Queue assignment generation as background job"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    papers = db.query(Paper).filter(Paper.project_id == project_id).all()
    if not papers:
        raise HTTPException(status_code=400, detail="No papers found for this project")
    
    # Queue async task
    task = generate_assignment_async.delay(project_id)
    
    return {
        "status": "queued",
        "job_id": task.id,
        "project_id": project_id,
        "message": "Assignment generation queued",
        "poll_status_url": f"/api/v1/jobs/{task.id}",
        "poll_result_url": f"/api/v1/jobs/{task.id}/result"
    }

@router.post("/{project_id}/ppt-async", response_model=dict)
async def generate_ppt_async_endpoint(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Queue presentation generation as background job"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == user_id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Queue async task
    task = generate_presentation_async.delay(project_id)
    
    return {
        "status": "queued",
        "job_id": task.id,
        "project_id": project_id,
        "message": "Presentation generation queued",
        "poll_status_url": f"/api/v1/jobs/{task.id}",
        "poll_result_url": f"/api/v1/jobs/{task.id}/result"
    }

