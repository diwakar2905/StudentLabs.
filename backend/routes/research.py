from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import logging
from database import get_db
from models import Paper, Project, User
from routes.auth import get_current_user
from ai_engine.arxiv_fetcher import fetch_arxiv_papers
from ai_engine.summarizer import summarize_abstract

logger = logging.getLogger(__name__)
router = APIRouter()

class SearchQuery(BaseModel):
    project_id: Optional[int] = None
    topic: str
    max_results: int = 5

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
    source: str = "arXiv"

class SummarizeRequest(BaseModel):
    paper_id: str

@router.post("/search", response_model=List[SearchResult])
async def search_papers(query: SearchQuery, db: Session = Depends(get_db)):
    """Search for real papers from arXiv and optionally add to project"""
    
    try:
        # Fetch real papers from arXiv
        logger.info(f"🔍 Searching arXiv for: {query.topic}")
        papers = fetch_arxiv_papers(query.topic, max_results=query.max_results)
        
        if not papers:
            logger.warning(f"No papers found for topic: {query.topic}")
            raise HTTPException(status_code=404, detail=f"No papers found for '{query.topic}'")
        
        logger.info(f"✅ Found {len(papers)} papers on arXiv")
        
        # If project_id provided, add papers to project
        if query.project_id:
            project = db.query(Project).filter(Project.id == query.project_id).first()
            if not project:
                raise HTTPException(status_code=404, detail="Project not found")
            
            logger.info(f"Adding papers to project {query.project_id}...")
            
            # Add papers to project
            for paper_data in papers:
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
                    logger.debug(f"Added paper: {paper_data['title'][:50]}...")
            
            db.commit()
            logger.info(f"✅ Added {len(papers)} papers to project")
        
        # Format response
        result_papers = []
        for paper in papers:
            result_papers.append({
                "paper_id": paper["paper_id"],
                "title": paper["title"],
                "abstract": paper["abstract"],
                "authors": paper["authors"],
                "year": paper["year"],
                "source": paper.get("source", "arXiv")
            })
        
        return result_papers
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching papers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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
    """Summarize a paper's abstract using AI"""
    logger.info(f"Summarizing paper: {request.paper_id}")
    
    # Dummy abstract for demo - in real use, fetch from DB
    sample_abstract = """
    This paper presents a comprehensive study of deep learning approaches for medical image analysis.
    We examine state-of-the-art convolutional neural networks and their applications in pathology.
    Our analysis covers 50+ recent papers and demonstrates that transformer-based models achieve
    superior performance on benchmark datasets. We also discuss the computational complexity and
    practical deployment challenges. The results suggest that hybrid approaches combining visual
    features with semantic understanding provide the best accuracy-efficiency tradeoff for clinical
    applications. Future work will focus on interpretability and generalization across diverse
    imaging modalities.
    """
    
    try:
        # Use AI summarizer
        summary = summarize_abstract(sample_abstract)
        
        return {
            "paper_id": request.paper_id,
            "original_abstract": sample_abstract,
            "summary": summary,
            "compression_ratio": round(len(summary) / len(sample_abstract), 2),
            "message": "✅ Abstract summarized successfully"
        }
    except Exception as e:
        logger.error(f"Error summarizing paper: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to summarize: {str(e)}")
