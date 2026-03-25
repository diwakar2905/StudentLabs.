# StudentLabs Backend Architecture - Layered Design

## Overview

The backend has been refactored into a professional **layered architecture** following industry best practices. This design enables:

- **Scalability** - Add features without modifying existing code
- **Testability** - Each layer can be tested independently
- **Maintainability** - Clear separation of concerns
- **Reusability** - Services and AI modules used by multiple routes
- **Team Development** - Different teams can work on different layers

---

## Architecture Layers

### 1. **API Layer** (`app/api/`)
**Purpose:** HTTP request/response handling only

Routes in this layer:
- ✅ Accept HTTP requests
- ✅ Validate input using Pydantic schemas
- ✅ Call appropriate service methods
- ✅ Return response objects
- ❌ NO business logic
- ❌ NO database queries
- ❌ NO AI operations

**Files:**
- `auth.py` - User authentication endpoints
- `projects.py` - Project CRUD endpoints
- `research.py` - Paper fetching endpoints
- `generate.py` - Assignment/presentation generation
- `export.py` - PDF/PPT export endpoints
- `jobs.py` - Celery job status endpoints

**Example:**
```python
# app/api/projects.py
@router.post("/", response_model=ProjectResponse)
async def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # ✅ ONLY call service
    project_data = ProjectService.create_project(
        db, current_user.id, project.title, project.topic
    )
    return project_data
    # ❌ NO db queries
    # ❌ NO AI calls
    # ❌ NO business logic
```

---

### 2. **Services Layer** (`app/services/`)
**Purpose:** All business logic and orchestration

Services coordinate between API, models, and AI:
- ✅ Business logic and validation
- ✅ Database operations
- ✅ Calling AI functions
- ✅ Error handling
- ✅ Logging
- ❌ NO HTTP handling
- ❌ NO request/response objects

**Services:**

| Service | Purpose | Key Methods |
|---------|---------|-------------|
| **UserService** | User management | create_user, authenticate_user, create_user_token |
| **ProjectService** | Project CRUD | create_project, get_project_by_id, update_project, list_user_projects |
| **ResearchService** | Paper management | search_and_fetch_papers, add_papers_to_project, summarize_project_papers |
| **AssignmentService** | Assignment generation | generate_assignment, get_assignment, delete_assignment |
| **ExportService** | File exports | create_export_record, list_project_exports, get_pdf_export |

**Example:**
```python
# app/services/assignment_service.py
class AssignmentService:
    @staticmethod
    def generate_assignment(db, project_id, user_id):
        # 1. Get project
        project = db.query(Project).filter(...).first()
        
        # 2. Get papers
        papers = db.query(Paper).filter(...).all()
        
        # 3. Call AI engine
        assignment_data = build_assignment(project.topic, papers)
        
        # 4. Save to database
        assignment = Assignment(...)
        db.add(assignment)
        db.commit()
        
        # 5. Return response
        return {"status": "success", ...}
```

---

### 3. **AI Layer** (`app/ai/`)
**Purpose:** All machine learning and AI operations

- ✅ Paper fetching (arXiv API)
- ✅ Text summarization (BART)
- ✅ Vector embeddings (sentence-transformers)
- ✅ Text generation (Mistral-7B)
- ✅ RAG retrieval (FAISS)
- ✅ Assignment building
- ✅ Presentation generation
- ❌ NO database operations
- ❌ NO HTTP handling

**Functions/Classes:**
```
fetch_arxiv_papers()        - Get papers from arXiv
summarize_abstract()        - Condense paper abstracts
index_papers()              - Build FAISS vector index
retrieve_relevant_content() - Semantic search (RAG)
generate_section_with_rag() - Generate text with context
build_assignment()          - Orchestrate full pipeline
build_and_export_presentation()
```

**Input:** Data dictionaries (no ORM objects)  
**Output:** Generated content (markdown, JSON, etc.)

---

### 4. **Models Layer** (`app/models/`)
**Purpose:** Database ORM definitions

SQLAlchemy models representing database tables:
- `User` - Platform users
- `Project` - Research projects
- `Paper` - Academic papers
- `Assignment` - Generated assignments
- `Presentation` - Generated presentations
- `Export` - File exports (PDF/PPT)
- `Summary` - Project summaries

**No business logic** - only schema definitions.

---

### 5. **Schemas Layer** (`app/schemas/`)
**Purpose:** Pydantic validation schemas

Request/response validation:
- `UserCreate`, `UserLogin`, `UserResponse`
- `ProjectCreate`, `ProjectResponse`, `ProjectDetailResponse`
- `PaperResponse`
- `AssignmentResponse`
- `PresentationResponse`
- `ExportResponse`
- `ResearchQuery`, `ResearchResponse`
- `Token`, `TokenResponse`

**Used in:**
- Request validation: `project: ProjectCreate = Body(...)`
- Response serialization: `response_model=ProjectResponse`

---

### 6. **Tasks Layer** (`app/tasks/`)
**Purpose:** Async background job processing with Celery

Celery tasks for long-running operations:
- `generate_assignment_async.delay(project_id)`
- `generate_presentation_async.delay(project_id)`
- `export_assignment_pdf.delay(project_id, assignment_id)`
- `export_presentation_pptx.delay(project_id, presentation_id)`

**Features:**
- Redis broker for job queue
- Automatic retries
- Result caching
- Status tracking

---

### 7. **Core Layer** (`app/core/`)
**Purpose:** Infrastructure and configuration

Files:
- `config.py` - Centralized settings (API, AI models, export params)
- `database.py` - Database engine, SessionLocal, Base
- `__init__.py` - Exports

**Single Source of Truth** for:
- Secret keys
- Database URL
- Model names
- Generation parameters
- File paths

---

### 8. **Utils Layer** (`app/utils/`)
**Purpose:** Helper functions

- `auth.py` - JWT token functions, password hashing
- Other utilities as needed

**Used by:** Services and APIs

---

## Data Flow Example

### "Generate assignment" request

```
1. API LAYER (app/api/generate.py)
   ├─ Request: POST /api/v1/generate/{id}/assignment
   ├─ Validate: project_id, user_id
   └─ Call: AssignmentService.generate_assignment()

2. SERVICES LAYER (app/services/assignment_service.py)
   ├─ Get project (db query)
   ├─ Get papers (db query)
   ├─ Convert to dicts
   └─ Call: build_assignment(topic, papers)

3. AI LAYER (app/ai/ → ai_engine/)
   ├─ Summarize papers (BART)
   ├─ Index in FAISS
   ├─ Retrieve context (semantic search)
   ├─ Generate sections (Mistral + context)
   └─ Return: {title, content, citations, word_count}

4. SERVICES LAYER (back)
   ├─ Save Assignment to DB
   ├─ Update project status
   └─ Return: {status, assignment}

5. API LAYER (back)
   ├─ Serialize to AssignmentResponse
   └─ HTTP: 200 OK {id, title, word_count, rag_used, created_at}
```

---

## Core Principles

### 1. **Thin API Layer**
Routes should be _50-100 lines max_. Just parse input, call service, return response.

```python
# GOOD ✅
@router.post("/", response_model=ProjectResponse)
async def create_project(project: ProjectCreate, db=Depends(get_db), user=Depends(get_current_user)):
    return ProjectService.create_project(db, user.id, project.title, project.topic)

# BAD ❌
@router.post("/", response_model=ProjectResponse)
async def create_project(project: ProjectCreate, db=Depends(get_db)):
    # 20 lines of business logic...
    # 15 lines of database queries...
    # 10 lines of AI calls...
```

### 2. **Rich Services**
Services contain all business logic. Easy to test, easy to reuse.

```python
# GOOD ✅ - Service layer (testable, reusable)
class ProjectService:
    @staticmethod
    def create_project(db, user_id, title, topic):
        # Validation logic
        # Database logic
        # Error handling
        # Logging
        return project

# Then in API:
project = ProjectService.create_project(db, user.id, title, topic)
```

### 3. **AI Independence**
AI functions take data dicts, return results. No database access.

```python
# GOOD ✅ - AI function (no database, no dependencies)
def build_assignment(topic: str, papers: List[Dict]) -> Dict:
    # topic: string
    # papers: list of dicts {title, abstract, ...}
    # return: {title, content, citations, ...}
    # No database queries!

# GOOD ✅ - Service calls it
papers_dict = [{"title": ..., "abstract": ...} for p in papers]
result = build_assignment(topic, papers_dict)
```

### 4. **Dependency Injection**
Routes receive dependencies, not create them.

```python
# GOOD ✅
@router.get("/{id}")
async def get(id: int, db: Session = Depends(get_db)):
    # db is injected
    return ProjectService.get(db, id)

# BAD ❌
@router.get("/{id}")
async def get(id: int):
    db = Session()  # Don't create it!
    return ProjectService.get(db, id)
```

---

## Import Patterns

### From API Routes
```python
# Get dependencies
from fastapi import Depends
from app.core import get_db
from app.utils import extract_token_from_header

# Get schemas
from app.schemas import ProjectCreate, ProjectResponse

# Get services
from app.services import ProjectService

# Get models (type hints only)
from app.models import User
```

### From Services
```python
# Import models
from app.models import Project, Paper

# Import AI functions
from app.ai import build_assignment, fetch_arxiv_papers

# Import other services
from app.services import ProjectService
```

### From Tasks
```python
# Import services
from app.services import AssignmentService

# Import models
from app.models import Assignment

# Import core
from app.core import get_db, SessionLocal
```

---

## Testing Benefits

With this architecture, testing becomes simple:

```python
# Test service in isolation (no API, no database)
def test_assignment_generation():
    mock_db = MagicMock()
    result = AssignmentService.generate_assignment(mock_db, project_id, user_id)
    assert result["status"] == "success"

# Test AI function (no database, no HTTP)
def test_rag_generation():
    papers = [{...}, {...}]
    result = build_assignment("topic", papers)
    assert result["word_count"] > 0

# Test API with mocked service
def test_create_project_endpoint():
    with patch("ProjectService.create_project") as mock:
        mock.return_value = project_obj
        response = client.post("/api/v1/projects/", json={...})
        assert response.status_code == 200
```

---

## Configuration

All settings in `app/core/config.py`:

```python
class Settings:
    # Database
    DATABASE_URL = "sqlite:///./studentlabs.db"
    
    # AI Models
    SUMMARIZER_MODEL = "facebook/bart-large-cnn"
    GENERATOR_MODEL = "mistralai/Mistral-7B-Instruct"
    
    # RAG
    TOP_K_PAPERS = 3
    
    # Generation
    MAX_TOKENS_ABSTRACT = 300
    MAX_TOKENS_INTRO = 400
    
    # File export
    EXPORT_DIR = "generated"
    PDF_MARGIN = 40
```

Access from anywhere:
```python
from app.core import settings
print(settings.GENERATOR_MODEL)
```

---

## Migration Notes

### Old Structure
```
backend/
├── main.py
├── models.py
├── database.py
├── auth_utils.py
├── routes/
├── ai_engine/
└── tasks/
```

### New Structure
```
backend/
├── app/
│   ├── api/              ← routes (thin layer)
│   ├── services/         ← business logic (rich layer)
│   ├── ai/               ← ML functions
│   ├── models/           ← ORM models
│   ├── schemas/          ← validation
│   ├── tasks/            ← async jobs
│   ├── core/             ← config & database
│   ├── utils/            ← helpers
│   └── __init__.py       ← exports
├── main.py               ← uses app
└── ...
```

### Import Changes

**Old:**
```python
from models import Project
from routes.projects import router
```

**New:**
```python
from app.models import Project
from app.api.projects import router
```

---

## Migration Checklist

- [ ] Move routes to `app/api/`
- [ ] Update route imports (database, models, auth)
- [ ] Create route tests
- [ ] Move all business logic to services
- [ ] Create service tests
- [ ] Update AI layer imports
- [ ] Update Celery task imports
- [ ] Update main.py to use new structure
- [ ] Run full test suite
- [ ] Update documentation
- [ ] Deploy new structure

---

## Success Metrics

After migration, you should have:

✅ **Thin API** - Routes <100 lines, only request/response  
✅ **Rich Services** - All business logic, testable  
✅ **Clean AI** - No database, composable functions  
✅ **Reusable Layers** - Services used by routes, tasks, CLI  
✅ **Testable** - Each layer tested independently  
✅ **Documented** - This architecture guide  
✅ **Scalable** - Easy to add features  

---

## Further Reading

- **API Layer:** Build routes that parse input and call services
- **Services Layer:** Implement business logic, call AI and database
- **AI Layer:** Use pure Python, no HTTP or database
- **Models Layer:** Define database schema clearly
- **Schemas Layer:** Validate all inputs and outputs
- **Core Layer:** One place for all configuration

---

**This architecture scales from 1 developer to 100+ developers on the same codebase.** 🚀
