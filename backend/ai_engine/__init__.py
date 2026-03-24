"""
AI Engine Module - Core Brain of StudentLabs

This module contains all AI-powered content generation logic:
- Assignment Builder: Generates academic assignments from papers
- Generator: Creates text sections using transformer models
- PPT Builder: Converts assignments to presentation slides
- Presentation Builder: Creates presentation slides
- arXiv Fetcher: Retrieves real research papers from arXiv
- Summarizer: Condenses paper abstracts using BART transformer
- Citation Manager: Handles citations and references
- Content Synthesizer: Synthesizes information from multiple sources

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
    generate_with_context
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

__all__ = [
    "AssignmentBuilder",
    "build_assignment",
    "generate_text",
    "generate_abstract",
    "generate_introduction",
    "generate_discussion",
    "generate_conclusion",
    "generate_with_context",
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
    "measure_compression_ratio"
]
