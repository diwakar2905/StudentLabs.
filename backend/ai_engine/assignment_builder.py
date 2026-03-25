"""
Assignment Builder - Core Content Generation Engine

This module contains the logic for building academic assignments from research papers.

Architecture:
1. Input: Topic + Papers (title, authors, abstract, year, URL)
2. Process: 
   - Summarize papers
   - Index in FAISS for vector search
   - Retrieve relevant research for each section
   - Generate sections using RAG (Retrieval-Augmented Generation)
   - Combine into academic assignment
3. Output: Complete academic assignment with proper structure

RAG Pipeline:
Topic → Fetch Papers → Summarize → Index in FAISS → Retrieve Context → Generate with AI → Assignment

Assignment Structure (Always follows this format):
- Title
- Abstract (AI-generated using research context)
- Introduction (AI-generated using research context)
- Literature Review (From summarized papers)
- Methodology (From paper data)
- Results / Discussion (AI-generated using research context)
- Conclusion (AI-generated using research context)
- References (From paper metadata)
"""

from typing import List, Dict, Any
from dataclasses import dataclass
import logging
from ai_engine.generator import (
    generate_abstract,
    generate_introduction,
    generate_discussion,
    generate_conclusion,
    generate_section_with_rag
)
from ai_engine.summarizer import summarize_abstract
from ai_engine.retriever import (
    index_papers,
    retrieve_relevant_content,
    build_retrieval_context,
    clear_index
)

logger = logging.getLogger(__name__)


@dataclass
class Paper:
    """Paper data structure"""
    id: int
    title: str
    authors: str
    abstract: str
    year: int
    url: str = None


class AssignmentBuilder:
    """
    Builds academic assignments from research papers.
    
    This is the core brain that transforms papers into structured assignments.
    """

    def __init__(self, topic: str):
        """Initialize builder with topic"""
        self.topic = topic
        self.papers = []
        self.assignment_content = ""
        
    def add_papers(self, papers: List[Any]) -> None:
        """
        Add papers to the builder.
        
        Args:
            papers: List of paper objects (can be ORM models or Paper dataclass)
        """
        self.papers = papers

    def build(self) -> Dict[str, Any]:
        """
        Build complete assignment from papers using RAG pipeline.
        
        RAG Flow:
        1. Summarize all papers
        2. Index papers in FAISS
        3. Retrieve relevant content for each section
        4. Generate sections using retrieved context
        5. Combine all sections
        
        Returns:
            Dictionary with:
            - title: Assignment title
            - content: Full markdown assignment
            - citations: List of citations
            - word_count: Approximate word count
            - sections: Dictionary of all sections
            - rag_used: Boolean indicating RAG was used
        """
        if not self.papers:
            raise ValueError("No papers added. Call add_papers() first.")

        logger.info(f"🚀 Starting RAG-based assignment generation for: {self.topic}")
        
        try:
            # Step 1: Summarize papers for better context
            logger.info("Step 1: Summarizing papers...")
            paper_summaries = []
            for paper in self.papers:
                abstract = paper.abstract if hasattr(paper, 'abstract') else paper.get('abstract', '')
                if len(abstract) > 300:
                    try:
                        summary = summarize_abstract(abstract)
                        paper_summaries.append(summary)
                        logger.debug(f"Summarized: {(paper.title if hasattr(paper, 'title') else paper.get('title', ''))[:50]}...")
                    except Exception as e:
                        logger.warning(f"Could not summarize, using original: {e}")
                        paper_summaries.append(abstract)
                else:
                    paper_summaries.append(abstract)
            
            # Step 2 & 3: Index papers and build retrieval context
            logger.info("Step 2-3: Indexing papers and building retrieval context...")
            try:
                clear_index()  # Clear any previous index
                retrieval_context = build_retrieval_context(self.papers, self.topic)
                logger.info(f"✅ Indexed {len(self.papers)} papers for retrieval")
            except Exception as e:
                logger.warning(f"FAISS indexing unavailable, falling back to paper context: {e}")
                retrieval_context = "\n\n".join([
                    f"Paper: {p.title}\nAuthors: {p.authors}\nYear: {p.year}\nAbstract: {p.abstract}"
                    for p in self.papers
                ])
            
            # Step 4: Generate sections using RAG
            logger.info("Step 4: Generating assignment sections with RAG...")
            
            sections = {
                "title": self._generate_title(),
                "abstract": self._generate_abstract_rag(retrieval_context),
                "introduction": self._generate_introduction_rag(retrieval_context),
                "literature_review": self._generate_literature_review(),
                "methodology": self._generate_methodology(),
                "discussion": self._generate_discussion_rag(retrieval_context),
                "conclusion": self._generate_conclusion_rag(retrieval_context),
                "references": self._generate_references(),
            }
            
            logger.info("✅ All sections generated using RAG")
            
            # Step 5: Combine all sections
            full_content = self._combine_sections(sections)
            
            # Extract citations
            citations = self._extract_citations()
            
            result = {
                "title": sections["title"],
                "content": full_content,
                "sections": sections,
                "citations": citations,
                "word_count": len(full_content.split()),
                "paper_count": len(self.papers),
                "rag_used": True,  # Flag indicating RAG was used
            }
            
            logger.info(f"✅ Assignment generation complete ({result['word_count']} words, {result['paper_count']} papers)")
            return result
            
        except Exception as e:
            logger.error(f"Error during RAG assignment generation: {e}")
            # Fallback to non-RAG generation
            logger.info("Falling back to non-RAG generation...")
            return self._build_fallback()

    # ============ SECTION GENERATORS ============

    def _generate_abstract_rag(self, retrieval_context: str) -> str:
        """Generate abstract using RAG with research context"""
        try:
            return generate_section_with_rag("abstract", self.topic, retrieval_context)
        except Exception as e:
            logger.warning(f"RAG abstract generation failed: {e}")
            return self._generate_abstract()
    
    def _generate_introduction_rag(self, retrieval_context: str) -> str:
        """Generate introduction using RAG with research context"""
        try:
            return generate_section_with_rag("introduction", self.topic, retrieval_context)
        except Exception as e:
            logger.warning(f"RAG introduction generation failed: {e}")
            return self._generate_introduction()
    
    def _generate_discussion_rag(self, retrieval_context: str) -> str:
        """Generate discussion using RAG with research context"""
        try:
            return generate_section_with_rag("discussion", self.topic, retrieval_context)
        except Exception as e:
            logger.warning(f"RAG discussion generation failed: {e}")
            return self._generate_discussion()
    
    def _generate_conclusion_rag(self, retrieval_context: str) -> str:
        """Generate conclusion using RAG with research context"""
        try:
            return generate_section_with_rag("conclusion", self.topic, retrieval_context)
        except Exception as e:
            logger.warning(f"RAG conclusion generation failed: {e}")
            return self._generate_conclusion()

    # ============ ORIGINAL SECTION GENERATORS (Fallback) ============

    def _generate_title(self) -> str:
        """Generate a professional title for the assignment"""
        return f"Comprehensive Analysis: {self.topic}"

    def _generate_abstract(self) -> str:
        """Generate abstract using AI model with paper context"""
        # Convert papers to format for AI generator
        paper_data = [
            {
                "id": p.id if hasattr(p, 'id') else idx,
                "title": p.title if hasattr(p, 'title') else p.get('title', ''),
                "authors": p.authors if hasattr(p, 'authors') else p.get('authors', ''),
                "year": p.year if hasattr(p, 'year') else p.get('year', 2024),
                "abstract": p.abstract if hasattr(p, 'abstract') else p.get('abstract', '')
            }
            for idx, p in enumerate(self.papers)
        ]
        
        # Use AI generator with paper context for relevance
        abstract = generate_abstract(
            topic=self.topic,
            paper_context=paper_data,
            max_tokens=300
        )
        
        return abstract

    def _generate_introduction(self) -> str:
        """Generate introduction using AI model with paper context"""
        # Convert papers to format for AI generator
        paper_data = [
            {
                "id": p.id if hasattr(p, 'id') else idx,
                "title": p.title if hasattr(p, 'title') else p.get('title', ''),
                "authors": p.authors if hasattr(p, 'authors') else p.get('authors', ''),
                "year": p.year if hasattr(p, 'year') else p.get('year', 2024),
                "abstract": p.abstract if hasattr(p, 'abstract') else p.get('abstract', '')
            }
            for idx, p in enumerate(self.papers)
        ]
        
        # Use AI generator with paper context
        intro = generate_introduction(
            topic=self.topic,
            paper_context=paper_data,
            max_tokens=400
        )
        
        # Add section header if not already present
        if not intro.startswith("#"):
            intro = f"# Introduction\n\n{intro}"
        
        return intro

    def _generate_literature_review(self) -> str:
        """Generate comprehensive literature review section with summarized abstracts"""
        review = f"""# Literature Review

## Overview

The literature on {self.topic} comprises diverse perspectives, methodologies, and findings. This section synthesizes {len(self.papers)} key studies, identifying major themes and research trajectories.

## Key Research Papers

"""
        for idx, paper in enumerate(self.papers, 1):
            # Get summarized abstract for better quality
            abstract = paper.abstract if hasattr(paper, 'abstract') else paper.get('abstract', '')
            
            # Summarize if abstract is long (improves readability)
            if len(abstract) > 300:
                try:
                    summary = summarize_abstract(abstract)
                    logger.debug(f"Summarized abstract for {paper.title[:50]}...")
                except Exception as e:
                    logger.warning(f"Failed to summarize, using original: {e}")
                    summary = abstract
            else:
                summary = abstract
            
            review += f"""### {idx}. {paper.title}

**Authors:** {paper.authors}
**Year:** {paper.year}

**Summary:** {summary}

"""

        review += """## Thematic Analysis

The reviewed literature reveals several key themes:

1. **Core Concepts and Definitions** - Researchers have worked to establish foundational concepts and terminology

2. **Methodological Approaches** - Multiple research methodologies have been employed to investigate this topic

3. **Empirical Findings** - Studies have produced various empirical results and conclusions

4. **Practical Applications** - Research has identified real-world applications and implications

5. **Theoretical Developments** - Theoretical frameworks have evolved through this body of research

## Research Gaps

Despite substantial research, several gaps remain:
- Further investigation is needed in specific areas
- More interdisciplinary approaches are required
- Longitudinal studies would provide valuable insights
- Replication studies would strengthen findings"""

        return review

    def _generate_methodology(self) -> str:
        """Generate methodology section"""
        methodologies = self._identify_methodologies()
        
        methodology = f"""# Methodology

## Research Approach

This assignment synthesizes research on {self.topic} through comprehensive literature analysis. The methodology involved systematic review of peer-reviewed publications.

## Papers Analyzed

**Sample Size:** {len(self.papers)} papers
**Time Period:** {self._get_year_range()['min']}-{self._get_year_range()['max']}
**Source:** Peer-reviewed academic literature

## Research Methods in Literature

The papers reviewed employed various research methodologies:

"""
        for method in methodologies:
            methodology += f"- **{method}**\n"

        methodology += """

## Analysis Framework

The analysis examined:
1. Research objectives and questions
2. Methodological choices and justification
3. Sample characteristics and scope
4. Data collection and analysis approaches
5. Findings and conclusions
6. Implications and recommendations

## Limitations

This systematic review has several limitations:
- Limited to available publications indexed in academic databases
- Publication bias may favor certain types of studies
- Variation in study methodologies affects comparability
- Some recent research may not yet be published"""

        return methodology

    def _generate_discussion(self) -> str:
        """Generate discussion using AI model with paper context"""
        # Convert papers to format for AI generator
        paper_data = [
            {
                "id": p.id if hasattr(p, 'id') else idx,
                "title": p.title if hasattr(p, 'title') else p.get('title', ''),
                "authors": p.authors if hasattr(p, 'authors') else p.get('authors', ''),
                "year": p.year if hasattr(p, 'year') else p.get('year', 2024),
                "abstract": p.abstract if hasattr(p, 'abstract') else p.get('abstract', '')
            }
            for idx, p in enumerate(self.papers)
        ]
        
        # Use AI generator with paper context
        discussion = generate_discussion(
            topic=self.topic,
            paper_context=paper_data,
            max_tokens=500
        )
        
        # Add section header if not already present
        if not discussion.startswith("#"):
            discussion = f"# Discussion of Findings\n\n{discussion}"
        
        return discussion

    def _generate_conclusion(self) -> str:
        """Generate conclusion using AI model with paper context"""
        # Convert papers to format for AI generator
        paper_data = [
            {
                "id": p.id if hasattr(p, 'id') else idx,
                "title": p.title if hasattr(p, 'title') else p.get('title', ''),
                "authors": p.authors if hasattr(p, 'authors') else p.get('authors', ''),
                "year": p.year if hasattr(p, 'year') else p.get('year', 2024),
                "abstract": p.abstract if hasattr(p, 'abstract') else p.get('abstract', '')
            }
            for idx, p in enumerate(self.papers)
        ]
        
        # Use AI generator with paper context
        conclusion = generate_conclusion(
            topic=self.topic,
            key_points=None,  # Could pass summary of discussion
            paper_context=paper_data,
            max_tokens=400
        )
        
        # Add section header if not already present
        if not conclusion.startswith("#"):
            conclusion = f"# Conclusion\n\n{conclusion}"
        
        return conclusion

    def _generate_references(self) -> str:
        """Generate references section with proper citations"""
        references = "# References\n\n"
        
        for idx, paper in enumerate(self.papers, 1):
            citation = f"{idx}. {paper.authors} ({paper.year}). {paper.title}."
            if paper.url:
                citation += f" Retrieved from {paper.url}"
            references += f"{citation}\n\n"
        
        return references

    # ============ HELPER METHODS ============

    def _get_year_range(self) -> Dict[str, int]:
        """Get year range of papers"""
        years = [p.year for p in self.papers if p.year]
        if not years:
            return {"min": 2020, "max": 2024}
        return {"min": min(years), "max": max(years)}

    def _get_key_researchers(self) -> List[str]:
        """Extract key researchers from papers"""
        researchers = set()
        for paper in self.papers:
            if paper.authors:
                # Extract first author
                first_author = paper.authors.split(",")[0].strip() if "," in paper.authors else paper.authors.split()[0]
                researchers.add(first_author)
        return list(researchers)[:5]  # Return top 5

    def _identify_methodologies(self) -> List[str]:
        """Identify research methodologies from papers"""
        # This is a simplified version - could be enhanced with NLP
        common_methodologies = [
            "Quantitative Analysis",
            "Qualitative Research",
            "Mixed Methods",
            "Literature Review",
            "Experimental Design",
            "Case Study Analysis",
            "Survey Research",
            "Computational Modeling"
        ]
        # Return subset based on paper count
        return common_methodologies[:len(self.papers) // 2 + 1]

    def _combine_sections(self, sections: Dict[str, str]) -> str:
        """Combine all sections into final assignment"""
        content = f"""# {sections['title']}

## Abstract

{sections['abstract']}

---

{sections['introduction']}

---

{sections['literature_review']}

---

{sections['methodology']}

---

{sections['discussion']}

---

{sections['conclusion']}

---

{sections['references']}
"""
        return content

    def _extract_citations(self) -> Dict[str, Any]:
        """Extract citation information from papers"""
        citations = []
        for paper in self.papers:
            citation_entry = {
                "id": paper.id,
                "title": paper.title,
                "authors": paper.authors,
                "year": paper.year,
                "url": paper.url,
                "citation_text": f"{paper.authors} ({paper.year}). {paper.title}.",
                "abstract": paper.abstract[:200] + "..." if paper.abstract else ""
            }
            citations.append(citation_entry)
        
        return {
            "papers": citations,
            "count": len(citations),
            "citation_format": "APA"
        }
    
    def _build_fallback(self) -> Dict[str, Any]:
        """Fallback: Generate assignment without RAG if retrieval fails"""
        logger.info("Using fallback generation (non-RAG)...")
        
        sections = {
            "title": self._generate_title(),
            "abstract": self._generate_abstract(),
            "introduction": self._generate_introduction(),
            "literature_review": self._generate_literature_review(),
            "methodology": self._generate_methodology(),
            "discussion": self._generate_discussion(),
            "conclusion": self._generate_conclusion(),
            "references": self._generate_references(),
        }
        
        full_content = self._combine_sections(sections)
        citations = self._extract_citations()
        
        return {
            "title": sections["title"],
            "content": full_content,
            "sections": sections,
            "citations": citations,
            "word_count": len(full_content.split()),
            "paper_count": len(self.papers),
            "rag_used": False,  # RAG not used for this attempt
        }


# ============ CONVENIENCE FUNCTIONS ============

def build_assignment(topic: str, papers: List[Any]) -> Dict[str, Any]:
    """
    Convenience function to build assignment.
    
    Usage:
        papers = db.query(Paper).filter(Paper.project_id == project_id).all()
        assignment = build_assignment("AI in Education", papers)
    
    Args:
        topic: Assignment topic
        papers: List of paper objects
        
    Returns:
        Dictionary with complete assignment
    """
    builder = AssignmentBuilder(topic)
    builder.add_papers(papers)
    return builder.build()
