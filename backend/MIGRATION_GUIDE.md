# Backend Refactoring Migration Guide

This guide helps you complete the transition from the old flat structure to the new layered architecture.

## Current Status

### ✅ Completed (New Structure)
- `app/core/` - Configuration, database setup
- `app/models/` - Database ORM models
- `app/schemas/` - Pydantic validation schemas
- `app/services/` - Business logic layer
  - UserService
  - ProjectService
  - ResearchService
  - AssignmentService
  - ExportService
- `app/ai/` - AI/ML wrapper layer
- `app/utils/` - Authentication utilities
- `app/tasks/` - Async tasks wrapper
- `ARCHITECTURE.md` - Complete architecture guide

### ⏳ In Progress (Need Action)
- `app/api/` - Routes (API layer) - **YOUR NEXT STEP**
- Update imports across the application
- Update main.py

### Old Files (Keep for now, delete after migration)
- `models.py` - Move to app/models
- `database.py` - Move to app/core
- `auth_utils.py` - Move to app/utils
- `routes/` - Move to app/api
- `tasks/` - Move to app/tasks
- `ai_engine/` - Move to app/ai

---

## Phase 1: Migrate API Routes to app/api/

### Step 1: Create app/api/auth.py

Copy `routes/auth.py` and update imports:

```python
# app/api/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core import get_db, settings
from app.models import User
from app.schemas import UserCreate, UserLogin, Token, TokenResponse, UserResponse
from app.services import UserService
from app.utils import extract_token_from_header, verify_access_token

router = APIRouter()
users_router = APIRouter()

# Authentication endpoints

@router.post("/signup", response_model=TokenResponse)
async def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    """User signup"""
    existing = UserService.get_user_by_email(db, user_data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = UserService.create_user(db, user_data.email, user_data.name, user_data.password)
    token, token_type = UserService.create_user_token(user)
    
    return {
        "access_token": token,
        "token_type": token_type,
        "user": UserResponse.from_orm(user)
    }

@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """User login"""
    user = UserService.authenticate_user(db, credentials.email, credentials.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token, token_type = UserService.create_user_token(user)
    
    return {
        "access_token": token,
        "token_type": token_type,
        "user": UserResponse.from_orm(user)
    }

# User profile endpoint

async def get_current_user(db: Session = Depends(get_db), authorization: str = None) -> User:
    """Dependency to get current user from JWT token"""
    token = extract_token_from_header(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="Missing token")
    
    token_data = verify_access_token(token)
    if not token_data:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = UserService.get_user_by_id(db, token_data.user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user

@users_router.get("/profile", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return UserResponse.from_orm(current_user)
```

### Step 2: Create app/api/projects.py

```python
# app/api/projects.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core import get_db
from app.models import User
from app.schemas import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectDetailResponse
from app.services import ProjectService
from app.api.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=ProjectResponse)
async def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new project"""
    db_project = ProjectService.create_project(db, current_user.id, project.title, project.topic)
    return db_project

@router.get("/", response_model=list[ProjectResponse])
async def list_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List user's projects"""
    projects = ProjectService.list_user_projects(db, current_user.id)
    return projects

@router.get("/{project_id}", response_model=ProjectDetailResponse)
async def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get project details"""
    project_detail = ProjectService.get_project_detail(db, project_id, current_user.id)
    if not project_detail:
        raise HTTPException(status_code=404, detail="Project not found")
    return project_detail

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a project"""
    updated = ProjectService.update_project(
        db, project_id, current_user.id,
        title=project_update.title,
        topic=project_update.topic,
        status=project_update.status
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Project not found")
    return updated

@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a project"""
    success = ProjectService.delete_project(db, project_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "Project deleted"}
```

### Step 3: Create app/api/research.py

```python
# app/api/research.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core import get_db
from app.models import User
from app.schemas import ResearchQuery, ResearchResponse
from app.services import ResearchService, ProjectService
from app.api.auth import get_current_user

router = APIRouter()

@router.post("/search", response_model=dict)
async def search_papers(
    query: ResearchQuery,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Search for research papers"""
    # Fetch papers from arXiv
    result = ResearchService.search_and_fetch_papers(query.topic, query.max_results)
    
    # Add to project if specified
    if query.project_id and result["papers"]:
        ProjectService.get_project_by_id(db, query.project_id, current_user.id)
        count = ResearchService.add_papers_to_project(db, query.project_id, result["papers"])
        result["added_to_project"] = count
    
    return result
```

### Step 4: Create app/api/generate.py

```python
# app/api/generate.py

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.core import get_db
from app.models import User
from app.schemas import AssignmentResponse, PresentationResponse
from app.services import AssignmentService, ProjectService
from app.api.auth import get_current_user
from app.tasks import generate_assignment_async, generate_presentation_async

router = APIRouter()

@router.post("/{project_id}/assignment", response_model=dict)
async def generate_assignment(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    background_tasks: BackgroundTasks = None
):
    """Generate assignment (can be async)"""
    project = ProjectService.get_project_by_id(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Queue async task if available
    if background_tasks and generate_assignment_async:
        task = generate_assignment_async.delay(project_id)
        return {"status": "queued", "task_id": task.id}
    
    # Otherwise generate synchronously
    result = AssignmentService.generate_assignment(db, project_id, current_user.id)
    return result

@router.post("/{project_id}/presentation", response_model=dict)
async def generate_presentation(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate presentation"""
    project = ProjectService.get_project_by_id(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check that assignment exists
    assignment = AssignmentService.get_assignment(db, project_id)
    if not assignment:
        raise HTTPException(status_code=400, detail="Assignment must exist first")
    
    # Queue async task if available
    if generate_presentation_async:
        task = generate_presentation_async.delay(project_id)
        return {"status": "queued", "task_id": task.id}
    
    return {"status": "error", "error": "Presentation generation not available"}
```

### Step 5: Create app/api/export.py

```python
# app/api/export.py

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.core import get_db
from app.models import User
from app.services import ProjectService, ExportService
from app.api.auth import get_current_user
from app.tasks import export_assignment_pdf, export_presentation_pptx

router = APIRouter()

@router.post("/{project_id}/pdf")
async def export_pdf(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export assignment as PDF"""
    project = ProjectService.get_project_by_id(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Queue export task
    if export_assignment_pdf:
        task = export_assignment_pdf.delay(project_id)
        return {"status": "queued", "task_id": task.id}
    
    return {"status": "error", "error": "PDF export not available"}

@router.post("/{project_id}/pptx")
async def export_pptx(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export presentation as PPTX"""
    project = ProjectService.get_project_by_id(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Queue export task
    if export_presentation_pptx:
        task = export_presentation_pptx.delay(project_id)
        return {"status": "queued", "task_id": task.id}
    
    return {"status": "error", "error": "PPTX export not available"}

@router.get("/exports/{project_id}")
async def list_exports(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List exports for project"""
    project = ProjectService.get_project_by_id(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    exports = ExportService.list_project_exports(db, project_id)
    return {"exports": exports}
```

### Step 6: Create app/api/jobs.py

```python
# app/api/jobs.py

from fastapi import APIRouter, Depends, HTTPException
from app.api.auth import get_current_user
from celery_app import celery_app

router = APIRouter()

@router.get("/{job_id}")
async def get_job_status(
    job_id: str,
    current_user = Depends(get_current_user)
):
    """Get async job status"""
    try:
        task = celery_app.AsyncResult(job_id)
        return {
            "job_id": job_id,
            "status": task.state,
            "result": task.result if task.ready() else None
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{job_id}")
async def cancel_job(
    job_id: str,
    current_user = Depends(get_current_user)
):
    """Cancel a job"""
    try:
        celery_app.control.revoke(job_id, terminate=True)
        return {"message": "Job cancelled"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### Step 7: Create app/api/__init__.py

```python
# app/api/__init__.py

"""
API Layer - HTTP routes and request/response handling.

This layer contains only FastAPI routes.
All business logic is delegated to the services layer.
"""

from app.api import auth, projects, research, generate, export, jobs

__all__ = [
    "auth",
    "projects",
    "research",
    "generate",
    "export",
    "jobs",
]
```

---

## Phase 2: Update main.py

Replace main.py with main_refactored.py:

```bash
# Backup old
mv main.py main_old.py

# Use new
cp main_refactored.py main.py
```

Or update manually:

```python
from app.core import settings, init_db
from app.api import auth, projects, research, generate, export, jobs

# ... rest of setup
```

---

## Phase 3: Test & Verify

### Run tests

```bash
# Test core
python -c "
from app.core import settings, get_db, init_db
print(f'✅ Core imports working')
print(f'   Database: {settings.DATABASE_URL}')
"

# Test models
python -c "
from app.models import User, Project, Paper, Assignment
print(f'✅ Models imported successfully')
"

# Test services
python -c "
from app.services import UserService, ProjectService
print(f'✅ Services imported successfully')
"

# Test schemas
python -c "
from app.schemas import ProjectCreate, ProjectResponse
print(f'✅ Schemas imported successfully')
"

# Test APIs (once implemented)
python -c "
from app.api import projects, research, auth
print(f'✅ API routes imported successfully')
"
```

### Run server

```bash
cd backend
python main.py
```

### Test endpoints

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Sign up
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","name":"Test","password":"pass123"}'

# Create project
curl -X POST http://localhost:8000/api/v1/projects/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"My Project","topic":"Machine Learning"}'
```

---

## Phase 4: Cleanup

After everything works, delete old files:

```bash
# Old files
rm models.py
rm database.py
rm auth_utils.py
rm -rf routes/
rm -rf old_tasks/
rm main_old.py
```

---

## Troubleshooting

### Import errors

If you get `ModuleNotFoundError: No module named 'app'`, run from backend directory:

```bash
cd backend
python main.py
```

### Missing dependencies

Install all requirements:

```bash
pip install -r requirements.txt
```

### Database errors

Reset database:

```bash
rm studentlabs.db
python -c "from app.core import init_db; init_db()"
```

---

## Summary

1. **Phase 1:** Create all API routes in `app/api/` (Update imports, use services)
2. **Phase 2:** Update `main.py` to import from `app.api`, `app.services`, `app.core`
3. **Phase 3:** Test everything works
4. **Phase 4:** Delete old files

**After migration:**
- ✅ Layered architecture
- ✅ Better testability
- ✅ Better scalability
- ✅ Better maintainability
- ✅ Production-ready

**Estimated time:** 2-4 hours for complete migration

**Difficulty:** Medium (straightforward but tedious)

---

## Architecture Diagrams After Migration

```
┌─────────────────────────────────────┐
│        FastAPI in main.py           │
├─────────────────────────────────────┤
│  API Layer (app/api/)               │  ← Only http routes
│  ├─ GET /projects                   │
│  ├─ POST /generate                  │
│  └─ GET /api/v1/health              │
├─────────────────────────────────────┤
│  Services Layer (app/services/)     │  ← All business logic
│  ├─ ProjectService                  │
│  ├─ AssignmentService               │
│  └─ ResearchService                 │
├─────────────────────────────────────┤
│  AI Layer (app/ai/)                 │  ← ML/LLMs
│  ├─ build_assignment()              │
│  ├─ fetch_arxiv_papers()            │
│  └─ generate_section_with_rag()     │
├─────────────────────────────────────┤
│  Database Layer (app/models/)       │  ← ORM models
│  ├─ User                            │
│  ├─ Project                         │
│  └─ Assignment                      │
└─────────────────────────────────────┘
```

---

**Questions? Check ARCHITECTURE.md for complete reference!** 📚
