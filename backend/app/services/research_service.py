"""
Research service - business logic for research paper management.
Handles paper fetching, searching, and storage.
"""

from sqlalchemy.orm import Session
from app.models import Project, Paper
from app.ai import fetch_arxiv_papers, summarize_abstract
from typing import List, Optional, Dict
import logging

logger = logging.getLogger(__name__)


class ResearchService:
    """Service for research paper operations"""
    
    @staticmethod
    def search_and_fetch_papers(
        topic: str,
        max_results: int = 5,
        project_id: Optional[int] = None
    ) -> Dict:
        """
        Search for papers on arXiv and optionally add to project
        
        Args:
            topic: Research topic/query
            max_results: Maximum number of papers to fetch
            project_id: Optional project to add papers to
            
        Returns:
            Dictionary with papers list and metadata
        """
        try:
            logger.info(f"Fetching papers for topic: {topic}, max_results: {max_results}")
            papers = fetch_arxiv_papers(topic, max_results=max_results)
            
            return {
                "papers": papers,
                "count": len(papers),
                "status": "success",
                "topic": topic
            }
        except Exception as e:
            logger.error(f"Error fetching papers: {str(e)}")
            return {
                "papers": [],
                "count": 0,
                "status": "error",
                "error": str(e)
            }
    
    @staticmethod
    def add_papers_to_project(
        db: Session,
        project_id: int,
        papers: List[Dict]
    ) -> int:
        """
        Add papers to a project
        
        Args:
            db: Database session
            project_id: Project ID
            papers: List of paper dictionaries
            
        Returns:
            Number of papers added
        """
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            logger.error(f"Project {project_id} not found")
            return 0
        
        added_count = 0
        for paper_data in papers:
            try:
                # Check if paper already exists
                existing = db.query(Paper).filter(
                    Paper.project_id == project_id,
                    Paper.paper_id == paper_data.get("paper_id")
                ).first()
                
                if existing:
                    logger.info(f"Paper {paper_data.get('paper_id')} already in project")
                    continue
                
                paper = Paper(
                    project_id=project_id,
                    paper_id=paper_data.get("paper_id", ""),
                    title=paper_data.get("title", ""),
                    abstract=paper_data.get("abstract", ""),
                    authors=",".join(paper_data.get("authors", [])) if paper_data.get("authors") else "",
                    year=paper_data.get("year", 0),
                    url=paper_data.get("url"),
                )
                
                db.add(paper)
                added_count += 1
                logger.info(f"Added paper: {paper_data.get('title')}")
                
            except Exception as e:
                logger.error(f"Error adding paper: {str(e)}")
                continue
        
        db.commit()
        return added_count
    
    @staticmethod
    def get_project_papers(db: Session, project_id: int) -> List[Dict]:
        """Get all papers for a project"""
        papers = db.query(Paper).filter(Paper.project_id == project_id).all()
        
        return [
            {
                "id": p.id,
                "paper_id": p.paper_id,
                "title": p.title,
                "abstract": p.abstract,
                "authors": p.authors,
                "year": p.year,
                "summary": p.summary,
                "url": p.url,
                "created_at": p.created_at
            }
            for p in papers
        ]
    
    @staticmethod
    def summarize_project_papers(db: Session, project_id: int) -> Dict:
        """
        Summarize all papers in a project
        
        Returns:
            Dictionary with summary stats
        """
        papers = db.query(Paper).filter(Paper.project_id == project_id).all()
        
        summarized = 0
        failed = 0
        
        for paper in papers:
            try:
                if paper.abstract and not paper.summary:
                    summary = summarize_abstract(paper.abstract)
                    paper.summary = summary
                    summarized += 1
            except Exception as e:
                logger.error(f"Error summarizing paper {paper.id}: {str(e)}")
                failed += 1
        
        db.commit()
        
        return {
            "total": len(papers),
            "summarized": summarized,
            "failed": failed,
            "status": "success"
        }
