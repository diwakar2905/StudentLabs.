"""
StudentLabs Application Entry Point (Refactored for Layered Architecture)

This is the template for the new main.py structure.
It demonstrates how to use the refactored layered architecture.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import logging

# Core imports (new structure)
from app.core import settings, init_db

# Configure logging
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

# ============= App Initialization =============

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered academic assignment and presentation generator",
)

# ============= Middleware =============

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============= Startup Event =============

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized")
    logger.info(f"StudentLabs {settings.APP_VERSION} started")


# ============= API Routes (NEW: app/api/ layer) =============

# TODO: Replace these imports with:
# from app.api import auth, projects, research, generate, export, jobs

# For now, we'll keep the old imports as we transition
# This ensures backwards compatibility during migration
try:
    from routes import auth, research, generate, export, projects, jobs
    logger.info("Using legacy route structure (transitioning...)")
except ImportError:
    from app.api import auth, projects, research, generate, export, jobs
    logger.info("Using new app/api route structure")

# Include routers
app.include_router(auth.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["Auth"])
app.include_router(auth.users_router, prefix=f"{settings.API_V1_PREFIX}/users", tags=["Users"])
app.include_router(projects.router, prefix=f"{settings.API_V1_PREFIX}/projects", tags=["Projects"])
app.include_router(research.router, prefix=f"{settings.API_V1_PREFIX}/research", tags=["Research"])
app.include_router(generate.router, prefix=f"{settings.API_V1_PREFIX}/generate", tags=["Generate"])
app.include_router(export.router, prefix=f"{settings.API_V1_PREFIX}/export", tags=["Export"])
app.include_router(jobs.router, prefix=f"{settings.API_V1_PREFIX}/jobs", tags=["Jobs"])

logger.info(f"Registered {len(app.routes)} routes")

# ============= Static Files & Frontend =============

root_path = Path(__file__).parent.parent
frontend_path = root_path / "frontend"
assets_path = root_path / "assets"

# Mount static directories
if assets_path.exists():
    app.mount("/assets", StaticFiles(directory=str(assets_path)), name="assets")
    logger.info("Mounted /assets")

if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")
    logger.info("Mounted /static")

# ============= Root Endpoints =============

@app.get("/")
async def serve_landing_page():
    """Serve the landing page at root"""
    try:
        return FileResponse(str(root_path / "index.html"))
    except FileNotFoundError:
        return {"message": "StudentLabs API is running"}

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }

# ============= Dashboard & App Routes =============

@app.get("/app")
async def serve_dashboard():
    """Serve the dashboard application"""
    try:
        return FileResponse(str(frontend_path / "index.html"))
    except FileNotFoundError:
        return {"error": "Frontend not found"}

# ============= Run Command =============

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
