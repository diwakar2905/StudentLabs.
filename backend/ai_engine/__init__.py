"""
AI Engine Module - Core Brain of StudentLabs

This module contains all AI-powered content generation logic:
- Assignment Builder: Generates academic assignments from papers
- Generator: Creates text sections using transformer models
- Presentation Builder: Creates presentation slides
- Citation Manager: Handles citations and references
- Content Synthesizer: Synthesizes information from multiple sources

The AI Engine is separated from the backend routing and database logic
to maintain clean code architecture and enable easy improvements.
"""

from .assignment_builder import AssignmentBuilder
from .generator import (
    generate_text,
    generate_abstract,
    generate_introduction,
    generate_discussion,
    generate_conclusion,
    generate_with_context
)

__all__ = [
    "AssignmentBuilder",
    "generate_text",
    "generate_abstract",
    "generate_introduction",
    "generate_discussion",
    "generate_conclusion",
    "generate_with_context"
]
