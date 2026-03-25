"""
Main API Router

Registers all API routes and provides the FastAPI app configuration.
"""

from fastapi import APIRouter
import logging

logger = logging.getLogger(__name__)

# Create main router
api_router = APIRouter(prefix="/api")


def include_api_routes(app):
    """
    Include all API routes in the FastAPI app.
    
    Usage in main.py:
        from app.api import include_api_routes
        include_api_routes(app)
    """
    try:
        # Import route modules
        from app.api import assignments
        
        # Include routers
        api_router.include_router(assignments.router)
        
        # Add to app
        app.include_router(api_router)
        
        logger.info("✅ API routes registered:")
        logger.info("  - POST   /api/projects/{id}/assignments/generate")
        logger.info("  - GET    /api/projects/{id}/assignments")
        logger.info("  - DELETE /api/projects/{id}/assignments")
        logger.info("  - GET    /api/projects/{id}/rag-stats")
        logger.info("  - POST   /api/projects/{id}/rag-index/refresh")
        
    except Exception as e:
        logger.error(f"Error registering API routes: {str(e)}", exc_info=True)
        raise
