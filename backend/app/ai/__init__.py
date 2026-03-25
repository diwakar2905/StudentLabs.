"""
AI Engine module - all machine learning and AI models.

This layer contains:
- Paper fetching (arXiv API)
- Text summarization (BART)
- Vector embeddings and retrieval (FAISS)
- Text generation (Mistral-7B)
- Assignment and presentation building
"""

# Import from existing ai_engine modules
# These will be refactored here gradually

try:
    from ai_engine.arxiv_fetcher import (
        fetch_arxiv_papers,
        search_arxiv,
        get_recent_papers,
    )
except ImportError:
    fetch_arxiv_papers = None
    search_arxiv = None
    get_recent_papers = None

try:
    from ai_engine.summarizer import (
        summarize_text,
        summarize_abstract,
        summarize_papers,
    )
except ImportError:
    summarize_text = None
    summarize_abstract = None
    summarize_papers = None

try:
    from ai_engine.retriever import (
        index_papers,
        retrieve_relevant_content,
        build_retrieval_context,
        get_paper_metadata,
        get_indexed_paper_count,
        clear_index,
    )
except ImportError:
    index_papers = None
    retrieve_relevant_content = None
    build_retrieval_context = None
    get_paper_metadata = None
    get_indexed_paper_count = None
    clear_index = None

try:
    from ai_engine.generator import (
        generate_text,
        generate_abstract,
        generate_introduction,
        generate_discussion,
        generate_conclusion,
        generate_section_with_rag,
    )
except ImportError:
    generate_text = None
    generate_abstract = None
    generate_introduction = None
    generate_discussion = None
    generate_conclusion = None
    generate_section_with_rag = None

try:
    from ai_engine.assignment_builder import (
        build_assignment,
        AssignmentBuilder,
    )
except ImportError:
    build_assignment = None
    AssignmentBuilder = None

try:
    from ai_engine.ppt_builder import (
        extract_sections,
        extract_key_points,
        build_and_export_presentation,
    )
except ImportError:
    extract_sections = None
    extract_key_points = None
    build_and_export_presentation = None


# ============= Module Exports =============

__all__ = [
    # Paper fetching
    "fetch_arxiv_papers",
    "search_arxiv",
    "get_recent_papers",
    
    # Summarization
    "summarize_text",
    "summarize_abstract",
    "summarize_papers",
    
    # Vector search & retrieval (RAG core)
    "index_papers",
    "retrieve_relevant_content",
    "build_retrieval_context",
    "get_paper_metadata",
    "get_indexed_paper_count",
    "clear_index",
    
    # Text generation
    "generate_text",
    "generate_abstract",
    "generate_introduction",
    "generate_discussion",
    "generate_conclusion",
    "generate_section_with_rag",
    
    # Assignment building (orchestrator)
    "build_assignment",
    "AssignmentBuilder",
    
    # Presentation building
    "extract_sections",
    "extract_key_points",
    "build_and_export_presentation",
]
