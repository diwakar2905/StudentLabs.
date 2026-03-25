"""
FastAPI Application Factory

Creates and configures the FastAPI application with:
- Database initialization
- API routes
- Middleware
- Error handlers
- CORS setup
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import logging
from contextlib import asynccontextmanager

from app.core.config import settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup/shutdown events.
    
    Startup:
    - Initialize database
    - Register Celery tasks
    
    Shutdown:
    - Close database connections
    """
    # Startup
    try:
        logger.info("🚀 Starting StudentLabs backend...")
        
        # Initialize database
        from app.database import init_db
        init_db()
        logger.info("✅ Database initialized")
        
        # Register Celery tasks
        try:
            from app.tasks.assignment_tasks import TaskRegistry
            TaskRegistry.register_all_tasks()
            logger.info("✅ Celery tasks registered")
        except Exception as e:
            logger.warning(f"Celery not configured (async tasks will be unavailable): {e}")
        
        logger.info("✅ Application startup complete")
        
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}", exc_info=True)
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down StudentLabs backend...")
    logger.info("✅ Application shutdown complete")


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.
    
    Returns:
        FastAPI application instance
    """
    
    # Create app
    app = FastAPI(
        title="StudentLabs API",
        description="Academic research assignment and presentation generation platform",
        version="1.0.0",
        lifespan=lifespan
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Register API routes
    from app.api import include_api_routes
    include_api_routes(app)
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "service": "StudentLabs Backend",
            "version": "1.0.0"
        }
    
    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint with API information"""
        return {
            "name": "StudentLabs API",
            "description": "Academic research platform",
            "version": "1.0.0",
            "docs": "/docs",
            "health": "/health"
        }
    
    # Error handlers
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle unexpected errors"""
        logger.error(f"Unhandled error: {str(exc)}", exc_info=True)
        
        return {
            "status": "error",
            "detail": "Internal server error",
            "path": str(request.url)
        }
    
    logger.info("✅ FastAPI application created successfully")
    
    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    # Run server
    uvicorn.run(
        app,
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.DEBUG
    )
