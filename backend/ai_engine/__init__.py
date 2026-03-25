"""
AI Engine Module - Core Brain of StudentLabs

This module contains all AI-powered content generation logic:
- Assignment Builder: Generates academic assignments from papers using RAG
- Generator: Creates text sections using transformer models with research context
- PPT Builder: Converts assignments to presentation slides
- arXiv Fetcher: Retrieves real research papers from arXiv
- Summarizer: Condenses paper abstracts using BART transformer
- Retriever: FAISS-based vector search for Retrieval-Augmented Generation (RAG)
- Citation Manager: Handles citations and references
- Content Synthesizer: Synthesizes information from multiple sources

RAG Pipeline:
Topic → Fetch Papers → Summarize → Index in FAISS → Retrieve Context → Generate with AI → Assignment

The AI Engine is separated from the backend routing and database logic
to maintain clean code architecture and enable easy improvements.
"""

from .assignment_builder import AssignmentBuilder, build_assignment
from .generator import (
    generate_text,
    generate_abstract,
    generate_introduction,
    generate_discussion,
    generate_conclusion,
    generate_with_context,
    generate_section_with_rag
)
from .ppt_builder import (
    build_presentation,
    extract_sections,
    extract_key_points,
    create_slides_from_sections,
    slides_to_python_pptx,
    save_presentation,
    build_and_export_presentation
)
from .arxiv_fetcher import (
    fetch_arxiv_papers,
    search_arxiv,
    get_recent_papers
)
from .summarizer import (
    summarize_text,
    summarize_abstract,
    summarize_papers,
    get_abstract_pair,
    measure_compression_ratio
)
from .retriever import (
    index_papers,
    retrieve_relevant_content,
    get_paper_metadata,
    get_indexed_paper_count,
    clear_index,
    build_retrieval_context
)

__all__ = [
    "AssignmentBuilder",
    "build_assignment",
    "generate_text",
    "generate_abstract",
    "generate_introduction",
    "generate_discussion",
    "generate_conclusion",
    "generate_with_context",
    "generate_section_with_rag",
    "build_presentation",
    "extract_sections",
    "extract_key_points",
    "create_slides_from_sections",
    "slides_to_python_pptx",
    "save_presentation",
    "build_and_export_presentation",
    "fetch_arxiv_papers",
    "search_arxiv",
    "get_recent_papers",
    "summarize_text",
    "summarize_abstract",
    "summarize_papers",
    "get_abstract_pair",
    "measure_compression_ratio",
    "index_papers",
    "retrieve_relevant_content",
    "get_paper_metadata",
    "get_indexed_paper_count",
    "clear_index",
    "build_retrieval_context"
]
