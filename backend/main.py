from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import os
from routes import auth, research, generate, export, projects, jobs
from database import init_db

# Initialize database
init_db()

app = FastAPI(
    title="StudentLabs API",
    description="Engine for turning topics into fully researched assignments and presentations.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(auth.users_router, prefix="/api/v1/users", tags=["Users"])
app.include_router(projects.router, prefix="/api/v1/projects", tags=["Projects"])
app.include_router(research.router, prefix="/api/v1/research", tags=["Research"])
app.include_router(generate.router, prefix="/api/v1/generate", tags=["Generate"])
app.include_router(export.router, prefix="/api/v1/export", tags=["Export"])
app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["Jobs"])

# Get paths for frontend files
root_path = Path(__file__).parent.parent
frontend_path = root_path / "frontend"
assets_path = root_path / "assets"

# Mount static directories
app.mount("/assets", StaticFiles(directory=str(assets_path)), name="assets")
app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

# Serve landing page at root
@app.get("/")
async def serve_landing_page():
    """Serve the landing page at root"""
    return FileResponse(str(root_path / "index.html"))

# Serve dashboard app
@app.get("/dashboard")
async def serve_dashboard():
    """Serve the dashboard app"""
    return FileResponse(str(frontend_path / "index.html"))

@app.get("/api")
def api_info():
    return {"message": "Welcome to StudentLabs API"}
