"""
Services layer - all business logic for the application.

Services contain the core logic and coordinate between:
- API routes (thin layer)
- Database models
- AI engine
- External APIs
"""

from app.services.user_service import UserService
from app.services.project_service import ProjectService
from app.services.research_service import ResearchService
from app.services.assignment_service import AssignmentService
from app.services.export_service import ExportService

__all__ = [
    "UserService",
    "ProjectService",
    "ResearchService",
    "AssignmentService",
    "ExportService",
]
