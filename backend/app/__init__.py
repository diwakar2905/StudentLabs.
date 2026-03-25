"""
StudentLabs Application Package

Layered Architecture:
├── api/resources       - Routes (request/response only)
├── services/           - Business logic layer
├── ai/                 - AI/ML models and functions
├── models/             - Database ORM models
├── schemas/            - Pydantic validation schemas
├── tasks/              - Celery async background jobs
├── core/               - Configuration and database setup
└── utils/              - Helper functions and utilities
"""

from app.core import settings, get_db, init_db, Base
from app.models import User, Project, Paper, Assignment, Presentation, Export, Summary
from app.schemas import (
    UserCreate, UserLogin, UserResponse,
    ProjectCreate, ProjectResponse,
    PaperResponse,
    AssignmentResponse,
    PresentationResponse,
    ExportResponse,
)
from app.services import (
    UserService,
    ProjectService,
    ResearchService,
    AssignmentService,
    ExportService,
)

__all__ = [
    # Core
    "settings",
    "get_db",
    "init_db",
    "Base",
    
    # Models
    "User",
    "Project",
    "Paper",
    "Assignment",
    "Presentation",
    "Export",
    "Summary",
    
    # Schemas
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "ProjectCreate",
    "ProjectResponse",
    "PaperResponse",
    "AssignmentResponse",
    "PresentationResponse",
    "ExportResponse",
    
    # Services
    "UserService",
    "ProjectService",
    "ResearchService",
    "AssignmentService",
    "ExportService",
]
