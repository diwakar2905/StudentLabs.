"""
RAG Service - Retrieval-Augmented Generation Orchestrator

This service manages the complete RAG pipeline for assignment generation:
1. Retrieve relevant papers from project
2. Index papers with FAISS for semantic search
3. Retrieve relevant content for query
4. Generate assignment sections with AI
5. Save results to database

Architecture follows the principle: Business logic in services, not routes.
Manages persistence, caching, and coordination of retrieval + generation.
"""

import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime

from sqlalchemy.orm import Session

from app.models import (
    Project,
    Paper,
    Assignment,
    Embedding,
)
from app.ai.prompts import get_prompt
from ai_engine.retriever import (
    index_papers as index_papers_faiss,
    retrieve_relevant_content as retrieve_faiss,
    save_index as save_faiss_index,
    load_index as load_faiss_index,
)
from ai_engine.generator import generate_text

logger = logging.getLogger(__name__)


class RAGService:
    """
    Orchestrates Retrieval-Augmented Generation for assignment creation.
    
    Responsibilities:
    - Load papers for project
    - Index papers with FAISS (with disk persistence)
    - Retrieve relevant content for queries
    - Coordinate with generator for section generation
    - Store results and embeddings in database
    - Cache indexes per project
    """
    
    def __init__(self):
        """Initialize RAG service."""
        pass
    
    def prepare_project_index(
        self,
        db: Session,
        project_id: int,
        force_refresh: bool = False
    ) -> Tuple[bool, str]:
        """
        Prepare FAISS index for a project.
        
        Steps:
        1. Check if index exists on disk (use cached)
        2. If not, fetch papers from DB
        3. Index papers with FAISS
        4. Save index to disk
        
        Args:
            db: Database session
            project_id: Project ID
            force_refresh: Re-index even if cached (default: False)
        
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            # Try to load from disk if available and not forcing refresh
            if not force_refresh:
                if load_faiss_index(project_id):
                    logger.info(f"✅ Loaded cached FAISS index for project {project_id}")
                    return True, f"Loaded pre-indexed {project_id} from cache"
            
            # Fetch all papers for project
            papers = db.query(Paper).filter(Paper.project_id == project_id).all()
            
            if not papers:
                logger.warning(f"No papers found for project {project_id}")
                return False, "No papers in project"
            
            # Convert to dict format for FAISS indexing
            paper_dicts = [
                {
                    'id': p.id,
                    'paper_id': p.id,
                    'title': p.title,
                    'abstract': p.abstract or "",
                    'authors': ', '.join(p.authors) if p.authors else "Unknown",
                    'year': p.year or 2024,
                    'url': p.url or "",
                }
                for p in papers
            ]
            
            # Index papers and auto-save to disk
            num_indexed = index_papers_faiss(
                paper_dicts,
                project_id=project_id,
                save_to_disk=True
            )
            
            logger.info(f"✅ Indexed {num_indexed} papers for project {project_id}")
            return True, f"Indexed {num_indexed} papers"
        
        except Exception as e:
            logger.error(f"Error preparing index: {e}")
            return False, f"Error: {str(e)}"
    
    def retrieve_context(
        self,
        project_id: int,
        query: str,
        top_k: int = 3
    ) -> List[str]:
        """
        Retrieve relevant paper content for a query.
        
        Args:
            project_id: Project ID (loads index from disk if needed)
            query: Search query
            top_k: Number of papers to retrieve
        
        Returns:
            List[str]: Relevant paper abstracts/content
        """
        try:
            relevant = retrieve_faiss(
                query,
                top_k=top_k,
                project_id=project_id
            )
            logger.info(f"Retrieved {len(relevant)} relevant papers for query")
            return relevant
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return []
    
    def generate_assignment_section(
        self,
        section_type: str,
        topic: str,
        context: str,
        papers_summary: str = None
    ) -> str:
        """
        Generate a single assignment section using RAG.
        
        Args:
            section_type: Type of section (abstract, introduction, literature, etc.)
            topic: Assignment topic
            context: Retrieved paper context
            papers_summary: Summary of papers used
        
        Returns:
            str: Generated section text
        """
        try:
            # Get appropriate prompt template
            prompt = get_prompt(
                section_type,
                topic=topic,
                context=context,
                papers_summary=papers_summary or ""
            )
            
            # Generate with AI
            section_text = generate_text(
                prompt=prompt,
                max_tokens=500
            )
            
            logger.debug(f"Generated {section_type} section ({len(section_text)} chars)")
            return section_text
        
        except Exception as e:
            logger.error(f"Error generating section: {e}")
            return ""
    
    def build_complete_assignment(
        self,
        db: Session,
        project_id: int,
        topic: str,
        user_id: int,
        section_types: List[str] = None
    ) -> Optional[Dict]:
        """
        Build a complete research assignment using RAG.
        
        Full RAG Pipeline:
        1. Prepare FAISS index for project
        2. Retrieve relevant papers
        3. Generate each section with context
        4. Save assignment to database
        5. Return assignment data
        
        Args:
            db: Database session
            project_id: Project ID
            topic: Research topic
            user_id: User ID
            section_types: Sections to generate (default: all)
        
        Returns:
            Dict: Assignment data or None if error
        """
        try:
            # Default sections
            if not section_types:
                section_types = [
                    'abstract',
                    'introduction',
                    'literature',
                    'methodology',
                    'findings',
                    'discussion',
                    'conclusion'
                ]
            
            logger.info(f"Starting RAG assignment generation for project {project_id}")
            
            # Step 1: Prepare FAISS index
            success, msg = self.prepare_project_index(db, project_id)
            if not success:
                logger.error(f"Failed to prepare index: {msg}")
                return None
            
            # Step 2: Retrieve relevant context
            context = self.retrieve_context(
                project_id=project_id,
                query=topic,
                top_k=5
            )
            
            if not context:
                logger.warning("No context retrieved, generating without RAG")
                context_text = f"Topic: {topic}"
            else:
                context_text = "\n\n".join(context)
            
            # Step 3: Generate sections
            assignment_sections = {}
            total_words = 0
            
            for section_type in section_types:
                try:
                    section_text = self.generate_assignment_section(
                        section_type=section_type,
                        topic=topic,
                        context=context_text,
                        papers_summary=f"Retrieved {len(context)} relevant papers"
                    )
                    
                    if section_text:
                        assignment_sections[section_type] = section_text
                        total_words += len(section_text.split())
                        logger.debug(f"✅ Generated {section_type}")
                    else:
                        logger.warning(f"Failed to generate {section_type}")
                
                except Exception as e:
                    logger.error(f"Error generating {section_type}: {e}")
                    assignment_sections[section_type] = f"[Error generating {section_type}]"
            
            # Step 4: Save to database
            assignment = Assignment(
                project_id=project_id,
                title=f"RAG Assignment: {topic}",
                content=assignment_sections,  # Will be stored as JSON via SQLAlchemy
                citations=context if context else [],
                word_count=total_words,
                rag_used=1  # Mark as RAG-generated
            )
            
            db.add(assignment)
            db.commit()
            db.refresh(assignment)
            
            # Step 5: Return result
            logger.info(f"✅ Assignment generated: {assignment.id} ({total_words} words)")
            
            return {
                'assignment_id': assignment.id,
                'title': assignment.title,
                'topic': topic,
                'word_count': total_words,
                'paper_count': len(context),
                'created_at': assignment.created_at.isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error building assignment: {e}")
            return None
    
    def store_embeddings(
        self,
        db: Session,
        project_id: int,
        paper_id: int,
        embedding_vector: List[float]
    ) -> bool:
        """
        Store embedding vector in database for analytics.
        
        Args:
            db: Database session
            project_id: Project ID
            paper_id: Paper ID
            embedding_vector: Embedding vector
        
        Returns:
            bool: Success status
        """
        try:
            embedding = Embedding(
                project_id=project_id,
                paper_id=paper_id,
                vector=embedding_vector,
                created_at=datetime.utcnow()
            )
            
            db.add(embedding)
            db.commit()
            
            return True
        
        except Exception as e:
            logger.error(f"Error storing embedding: {e}")
            return False
    
    def get_project_stats(self, db: Session, project_id: int) -> Dict:
        """
        Get RAG statistics for a project.
        
        Args:
            db: Database session
            project_id: Project ID
        
        Returns:
            Dict: Project statistics
        """
        try:
            paper_count = db.query(Paper).filter(
                Paper.project_id == project_id
            ).count()
            
            assignment_count = db.query(Assignment).filter(
                Assignment.project_id == project_id
            ).count()
            
            embedding_count = db.query(Embedding).filter(
                Embedding.project_id == project_id
            ).count()
            
            return {
                'project_id': project_id,
                'papers_indexed': paper_count,
                'assignments_generated': assignment_count,
                'embeddings_stored': embedding_count,
            }
        
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}


# Global instance
_rag_service = None


def get_rag_service() -> RAGService:
    """Get or create RAG service instance."""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
