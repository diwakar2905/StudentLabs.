# 🏗️ Backend Architecture Quick Reference

## Layered Architecture (What Goes Where?)

```
YOUR REQUEST
    ↓
┌──────────────────────────────────────────────────────────┐
│ app/api/          [REQUEST/RESPONSE ONLY - 50-100 lines] │
│ ├─ Parse input (Pydantic schemas)                        │
│ ├─ Call service method                                   │
│ └─ Return response                                       │
└──────────────────────────────────────────────────────────┘
    ↓
┌──────────────────────────────────────────────────────────┐
│ app/services/     [BUSINESS LOGIC - Rich & Complex]      │
│ ├─ Database queries                                      │
│ ├─ Coordinate operations                                 │
│ ├─ Call AI functions                                     │
│ ├─ Logging & error handling                              │
│ └─ Return data dicts                                     │
└──────────────────────────────────────────────────────────┘
    ↓
┌──────────────────────────────────────────────────────────┐
│ app/ai/           [ML/AI ONLY - Pure Python]             │
│ ├─ No database access                                    │
│ ├─ Takes dicts, returns content                          │
│ └─ Focus on algorithm                                    │
└──────────────────────────────────────────────────────────┘
    ↓
┌──────────────────────────────────────────────────────────┐
│ app/models/       [DATABASE SCHEMA - SQLAlchemy]         │
│ └─ ORM definitions only                                  │
└──────────────────────────────────────────────────────────┘
    ↓
YOUR RESPONSE
```

---

## Quick Rule Table

| Layer | Can Use | Cannot Use | Size |
|-------|---------|-----------|------|
| **api/** | Services, schemas, core | Business logic, AI, direct DB | <100 lines |
| **services/** | Models, AI, core, db | HTTP, requests, responses | 100-300 lines |
| **ai/** | Other AI functions | Database, HTTP, models | Variable |
| **models/** | Nothing | Business logic, functions | Variable |
| **schemas/** | Nothing | Logic, database | Just definitions |
| **tasks/** | Services, models | HTTP | Variable |
| **core/** | Settings, config | Business logic | Definitions |
| **utils/** | Helper functions | Business logic | Utilities |

---

## File Structure

```
backend/
├── app/
│   ├── api/                    # HTTP routes (thin layer)
│   │   ├── auth.py            # /auth endpoints
│   │   ├── projects.py        # /projects endpoints
│   │   ├── research.py        # /research endpoints
│   │   ├── generate.py        # /generate endpoints
│   │   ├── export.py          # /export endpoints
│   │   ├── jobs.py            # /jobs endpoints
│   │   └── __init__.py
│   │
│   ├── services/               # Business logic (rich layer)
│   │   ├── user_service.py    # User CRUD logic
│   │   ├── project_service.py # Project CRUD logic
│   │   ├── research_service.py # Paper fetching logic
│   │   ├── assignment_service.py # Assignment generation
│   │   ├── export_service.py  # Export operations
│   │   └── __init__.py
│   │
│   ├── ai/                     # ML/AI functions
│   │   └── __init__.py        # Re-exports from ai_engine
│   │
│   ├── models/                 # Database ORM
│   │   └── __init__.py        # All model definitions
│   │
│   ├── schemas/                # Pydantic validation
│   │   └── __init__.py        # All request/response schemas
│   │
│   ├── tasks/                  # Celery background jobs
│   │   └── __init__.py        # Re-exports from tasks
│   │
│   ├── core/                   # Infrastructure
│   │   ├── config.py          # Settings & configuration
│   │   ├── database.py        # Database setup
│   │   └── __init__.py
│   │
│   ├── utils/                  # Helpers
│   │   ├── auth.py            # JWT, passwords
│   │   └── __init__.py
│   │
│   └── __init__.py            # Main exports
│
├── main.py                     # FastAPI entry point (uses app/)
├── celery_app.py              # Celery config (unchanged)
├── ARCHITECTURE.md            # This architecture guide
├── MIGRATION_GUIDE.md         # Step-by-step migration
└── requirements.txt
```

---

## Import Examples

### In API Routes (app/api/*)

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

# ✅ Import from core
from app.core import get_db, settings

# ✅ Import from schemas (validation)
from app.schemas import ProjectCreate, ProjectResponse

# ✅ Import from services (business logic)
from app.services import ProjectService

# ✅ Import from models (type hints)
from app.models import User

# ✅ Import from utils (helpers)
from app.utils import extract_token_from_header

# ✅ Use them
@router.post("/", response_model=ProjectResponse)
async def create_project(
    project: ProjectCreate,              # ← Schema validation
    db: Session = Depends(get_db),      # ← Core
    current_user: User = Depends(...)   # ← Model type
):
    return ProjectService.create_project(db, ...)  # ← Service

# ❌ DON'T do this:
# - No 'from models import User' (use app.models)
# - No direct db.query() (use service)
# - No business logic here (belongs in service)
# - No AI calls here (service handles it)
```

### In Services (app/services/*)

```python
# ✅ Import from models (ORM)
from app.models import Project, User, Paper

# ✅ Import from AI (generate content)
from app.ai import build_assignment, fetch_arxiv_papers

# ✅ Import from core (config, db)
from app.core import get_db

# ✅ Use them
def generate_assignment(db, project_id, user_id):
    project = db.query(Project).filter(...).first()  # ← DB query
    papers = fetch_arxiv_papers(topic)               # ← AI call
    result = build_assignment(topic, papers)         # ← Orchestrate
    return result

# ❌ DON'T do this:
# - No from fastapi import Router (belongs in api/)
# - No HTTPException (belongs in api/)
# - No request/response objects (use dicts)
# - No @app.post decorators (belongs in api/)
```

### In AI Functions (app/ai/*)

```python
# ✅ Import from other AI functions
from ai_engine.summarizer import summarize_abstract
from ai_engine.retriever import index_papers

# ✅ Use data dicts
def build_assignment(topic: str, papers: list[dict]) -> dict:
    # Papers are dicts: {title, abstract, ...}
    # Return dict: {title, content, citations, ...}
    pass

# ❌ DON'T do this:
# - No database queries
# - No from app.models import (use dicts)
# - No HTTP stuff
# - No FastAPI decorators
# - No request/response objects
```

---

## Common Patterns

### Pattern 1: Create Entity

```
API receives POST request
  ↓
Schema validates input (ProjectCreate)
  ↓
Service creates entity
  - DB query/insert
  - Returns ORM object
  ↓
API serializes response (ProjectResponse model)
  ↓
HTTP 200 OK {id, title, topic, ...}
```

### Pattern 2: Generate Assignment

```
API receives POST /generate/{id}
  ↓
Service gets project & papers from DB
  ↓
Converts to dicts (ORM → dict)
  ↓
Calls AI with dicts
  ↓
AI returns generated content dict
  ↓
Service saves to DB (dict → ORM)
  ↓
API returns AssignmentResponse
```

### Pattern 3: Async Long Operation

```
API receives POST /export/pdf
  ↓
Queue async task (Celery)
  ↓
Return immediately: {"task_id": "xyz", "status": "queued"}
  ↓
Background worker processes task
  ↓
Calls service → AI → File generation
  ↓
User polls GET /jobs/xyz
  ↓
Returns: {"status": "success", "result": {...}}
```

---

## Testing

### Test API (mock service)

```python
from unittest.mock import patch

def test_create_project():
    with patch("ProjectService.create_project") as mock:
        mock.return_value = project_obj
        response = client.post("/api/v1/projects/", json={...})
        assert response.status_code == 200
```

### Test Service (mock DB & AI)

```python
def test_assignment_service():
    mock_db = MagicMock()
    mock_papers = [{...}, {...}]
    
    result = AssignmentService.generate_assignment(mock_db, 1, 1)
    
    assert result["status"] == "success"
    assert result["assignment"]["word_count"] > 0
```

### Test AI (no mocks needed)

```python
def test_build_assignment():
    papers = [{"title": "...", "abstract": "..."}]
    result = build_assignment("topic", papers)
    
    assert result["word_count"] > 0
    assert "content" in result
```

---

## Debugging

### "Where does this error come from?"

1. **Error in API route?** → Check schema validation
2. **Error in service?** → Check model query or AI call
3. **Error in AI?** → Check data format
4. **Database error?** → Check model definition

### "Which file do I edit?"

- **New endpoint?** → `app/api/`
- **New business logic?** → `app/services/`
- **New ML feature?** → `app/ai/`
- **Configuration?** → `app/core/config.py`
- **Database field?** → `app/models/`
- **Validation?** → `app/schemas/`

---

## Migration Checklist

- [ ] Create `app/api/auth.py` (copy from routes, update imports)
- [ ] Create `app/api/projects.py` (use ProjectService)
- [ ] Create `app/api/research.py` (use ResearchService)
- [ ] Create `app/api/generate.py` (use AssignmentService)
- [ ] Create `app/api/export.py` (use ExportService)
- [ ] Create `app/api/jobs.py` (use Celery)
- [ ] Create `app/api/__init__.py`
- [ ] Update `main.py` (import from `app.api`)
- [ ] Test all endpoints
- [ ] Delete old `routes/` directory
- [ ] Delete old `models.py`, `database.py`, `auth_utils.py`

---

## Golden Rules

1. **API = Thin (50-100 lines max)**
   - Parse, validate, delegate, respond

2. **Services = Rich (100-300 lines)**
   - All orchestration, coordination, logic

3. **AI = Pure (pure Python)**
   - No database, no HTTP, no side effects

4. **Models = Schema (definitions only)**
   - No methods with logic, just fields

5. **Schemas = Validation (Pydantic)**
   - Input/output validation only

6. **One Responsibility Per Layer**
   - Don't blur the lines

---

## When You Add a Feature

### "Add PDF export"

1. **Schema** (`app/schemas/`): Add `ExportResponse`
2. **Service** (`app/services/`): Add `ExportService.create_pdf_export()`
3. **API** (`app/api/`): Add route that calls service
4. **Done!** (Already have models, tasks, AI ready)

### "Add new AI model"

1. **AI** (`app/ai/`): Add new function
2. **Service** (`app/services/`): Call it if needed
3. **API** (`app/api/`): Add endpoint if needed
4. **Done!** (No database changes needed)

### "Add new data field"

1. **Model** (`app/models/`): Add column to User/Project/etc
2. **Schema** (`app/schemas/`): Add field to response schema
3. **Service** (`app/services/`): Use it in logic
4. **Done!** (No other changes needed)

---

## Need Help?

📖 **Full Guide** → `ARCHITECTURE.md`  
🛠️ **Step by Step** → `MIGRATION_GUIDE.md`  
❓ **Questions?** → Check the examples above!

---

**This layered architecture supports growth from 1 developer to 100+!** 🚀
