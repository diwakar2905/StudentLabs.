from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from database import get_db
from models import Paper, Project, User
from routes.auth import get_current_user
router = APIRouter()

class SearchQuery(BaseModel):
    project_id: Optional[int] = None
    topic: str

class PaperAdd(BaseModel):
    paper_id: str
    title: str
    abstract: str
    authors: List[str]
    year: int
    url: Optional[str] = None

class SearchResult(BaseModel):
    paper_id: str
    title: str
    abstract: str
    authors: List[str]
    year: int

class SummarizeRequest(BaseModel):
    paper_id: str

@router.post("/search", response_model=List[SearchResult])
async def search_papers(query: SearchQuery, db: Session = Depends(get_db)):
    """Search for papers (mock data) and optionally add to project"""
    # Mock Semantic Scholar / arXiv API behavior
    mock_papers = [
        {
            "paper_id": "arxiv:1234.5678",
            "title": f"Recent Advances in {query.topic}",
            "abstract": "This paper discusses the core methodologies and significant findings related to the topic...",
            "authors": ["John Doe", "Jane Smith"],
            "year": 2024,
            "url": "https://arxiv.org/abs/1234.5678"
        },
        {
            "paper_id": "semantic:987654321",
            "title": f"A Comprehensive Review of {query.topic}",
            "abstract": "We present a thorough literature review of the subject matter, highlighting the latest trends...",
            "authors": ["Alice Johnson"],
            "year": 2023,
            "url": "https://semantic-scholar.org/987654321"
        },
        {
            "paper_id": "arxiv:2024.1111",
            "title": f"Emerging Trends in {query.topic}",
            "abstract": "This research explores emerging developments and future directions in the field...",
            "authors": ["Bob Smith", "Carol Davis"],
            "year": 2024,
            "url": "https://arxiv.org/abs/2024.1111"
        }
    ]
    
    # If project_id provided, add papers to project
    if query.project_id:
        project = db.query(Project).filter(Project.id == query.project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Add papers to project
        for paper_data in mock_papers:
            existing_paper = db.query(Paper).filter(
                Paper.project_id == query.project_id,
                Paper.paper_id == paper_data["paper_id"]
            ).first()
            
            if not existing_paper:
                new_paper = Paper(
                    project_id=query.project_id,
                    paper_id=paper_data["paper_id"],
                    title=paper_data["title"],
                    abstract=paper_data["abstract"],
                    authors=", ".join(paper_data["authors"]),
                    year=paper_data["year"],
                    url=paper_data.get("url")
                )
                db.add(new_paper)
        
        db.commit()
    
    return mock_papers

@router.post("/{project_id}/papers/add")
async def add_papers_to_project(
    project_id: int,
    papers: List[PaperAdd],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add papers to a project"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    added_papers = []
    for paper_data in papers:
        existing_paper = db.query(Paper).filter(
            Paper.project_id == project_id,
            Paper.paper_id == paper_data.paper_id
        ).first()
        
        if not existing_paper:
            new_paper = Paper(
                project_id=project_id,
                paper_id=paper_data.paper_id,
                title=paper_data.title,
                abstract=paper_data.abstract,
                authors=", ".join(paper_data.authors),
                year=paper_data.year,
                url=paper_data.url
            )
            db.add(new_paper)
            added_papers.append(paper_data.dict())
        else:
            raise HTTPException(status_code=400, detail=f"Paper {paper_data.paper_id} already in project")
    
    db.commit()
    
    return {
        "status": "success",
        "papers_added": len(added_papers),
        "papers": added_papers
    }

@router.post("/summarize")
async def summarize_paper(request: SummarizeRequest):
    # Mock extracting core methodology/findings
    return {
        "paper_id": request.paper_id,
        "summary": "The methodology involves a novel approach to the problem, yielding a 20% improvement in accuracy. Key findings suggest that existing frameworks can be adapted effectively."
    }
