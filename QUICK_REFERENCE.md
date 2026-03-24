# StudentLabs - Quick Reference Guide

## 🎯 System Overview

**StudentLabs** transforms research topics into complete academic assignments and presentations through an automated 4-step workflow.

---

## 📊 Architecture at a Glance

```
┌─────────────────────────────────────────────────────────────┐
│                    STUDENTLABS SYSTEM                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐        ┌──────────────┐                  │
│  │   FRONTEND   │        │   BACKEND    │                  │
│  │ (Vanilla JS) │───────→│  (FastAPI)   │                  │
│  └──────────────┘        └──────────────┘                  │
│                               │                             │
│                    ┌──────────┼──────────┐                  │
│                    ↓          ↓          ↓                  │
│                 AUTH      DATABASE    CELERY               │
│                (JWT)     (SQLite)    (Redis)               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 User Workflow

```
1. REGISTER/LOGIN
   ↓
2. CREATE PROJECT (topic + title)
   ↓
3. SEARCH & SELECT PAPERS (research phase)
   ↓
4. GENERATE ASSIGNMENT (from papers)
   ↓
5. GENERATE PRESENTATION (from assignment)
   ↓
6. EXPORT (PDF or PowerPoint)
   ↓
7. DOWNLOAD
```

---

## 🗂️ Project Structure

### Backend Directory Tree
```
backend/
├── main.py                    # FastAPI app entry point
├── models.py                  # Database models (7 tables)
├── database.py                # SQLAlchemy configuration
├── auth_utils.py              # JWT & password utilities
├── celery_app.py              # Celery + Redis config
│
├── routes/                    # API endpoints (6 routers)
│   ├── auth.py               # Login/Signup
│   ├── projects.py           # Project CRUD
│   ├── research.py           # Paper search
│   ├── generate.py           # Assignment/PPT generation
│   ├── export.py             # PDF/PPTX export
│   └── jobs.py               # Async job tracking
│
└── tasks/                     # Celery async tasks
    ├── generation_tasks.py    # Content generation jobs
    └── export_tasks.py        # File export jobs
```

### Frontend Directory
```
frontend/
├── index.html                 # Dashboard HTML
├── app.js                     # Main application logic
├── api.js                     # API service client
└── styles.css                 # Styling
```

---

## 💾 Database Models (7 Tables)

```sql
User
├── id (PK) | email (UNIQUE) | name | password_hash | plan | created_at

Project
├── id (PK) | user_id (FK) | title | topic | status | created_at | updated_at

Paper
├── id (PK) | project_id (FK) | paper_id | title | abstract | authors | year | url

Summary
├── id (PK) | project_id (FK, UNIQUE) | content | created_at

Assignment
├── id (PK) | project_id (FK, UNIQUE) | title | content | citations (JSON) | created_at

Presentation
├── id (PK) | project_id (FK, UNIQUE) | slides_json (JSON) | created_at

Export
├── id (PK) | project_id (FK) | file_type | file_path | file_url | created_at
```

---

## 🔌 API Endpoints (30 endpoints across 6 routers)

### Authentication (/api/v1/auth)
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/auth/signup` | Register new user |
| POST | `/auth/login` | Authenticate and get JWT |
| GET | `/auth/me` (v1/users/me) | Get current user profile |

### Projects (/api/v1/projects)
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/projects` | Create project |
| GET | `/projects` | List all user projects |
| GET | `/projects/{id}` | Get project details |
| PUT | `/projects/{id}` | Update project |
| DELETE | `/projects/{id}` | Delete project |
| GET | `/projects/{id}/papers` | Get project papers |

### Research (/api/v1/research)
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/research/search` | Search for papers |
| POST | `/research/{id}/papers/add` | Add papers to project |
| POST | `/research/summarize` | Summarize a paper |

### Generation (/api/v1/generate)
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/generate/{id}/assignment` | Generate assignment (sync) |
| PUT | `/generate/{id}/assignment` | Update assignment |
| POST | `/generate/{id}/ppt` | Generate presentation (sync) |
| PUT | `/generate/{id}/ppt` | Update presentation |

### Export (/api/v1/export)
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/export/pdf` | Queue PDF export (async) |
| POST | `/export/pptx` | Queue PowerPoint export (async) |
| GET | `/export/{id}/downloads` | Get project exports |

### Jobs (/api/v1/jobs)
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/jobs/{id}` | Get job status (polling) |
| GET | `/jobs/{id}/result` | Get completed job result |
| DELETE | `/jobs/{id}` | Cancel job |

---

## 🔐 Authentication Flow

```
USER                          BACKEND
 │                              │
 │ 1. POST /signup              │
 ├─────────────────────────────→│
 │                              ├─ Hash password (bcrypt)
 │                              ├─ Create user
 │                              │
 │ 2. POST /login               │
 ├─────────────────────────────→│
 │                              ├─ Verify credentials
 │                              ├─ Generate JWT token (30 min)
 │                   Response:{│
 │                     token,   │
 │                     user     │
 │                   }          │
 │←─────────────────────────────┤
 │                              │
 │ 3. GET /api/* with token     │
 │ Header: Authorization: Bearer │
 ├─────────────────────────────→│
 │                              ├─ Verify JWT
 │                              ├─ Attach user to request
 │                   Response:  │
 │←─────────────────────────────┤
```

---

## ⚙️ Key Functions

### Backend

#### Auth Utils (auth_utils.py)
```python
hash_password(password) → str          # Bcrypt hash
verify_password(plain, hash) → bool    # Verify bcrypt
create_access_token(data) → str        # Generate JWT
verify_access_token(token) → TokenData # Verify JWT
```

#### Database (database.py)
```python
SessionLocal()                         # Create DB session
get_db()                              # Dependency for sessions
init_db()                             # Create all tables
```

#### Celery Tasks (tasks/)
```python
@celery_app.task
generate_assignment_async(project_id)  # Async assignment generation
generate_presentation_async(project_id) # Async presentation generation
export_assignment_pdf(pid, aid)        # Queue PDF export
export_presentation_pptx(pid, pid)     # Queue PPTX export
```

### Frontend

#### API Service (api.js)
```javascript
api.register(name, email, pwd)         // User signup
api.login(email, pwd)                  // User login
api.getProjects()                      // List projects
api.createProject(title, topic)        // Create project
api.searchResearchPapers(topic)        // Search papers
api.generateAssignment(projectId)      // Start assignment generation
api.exportToPDF(projectId, assignId)   // Queue PDF export
api.getJobStatus(jobId)                // Poll job status
```

#### UI Functions (app.js)
```javascript
showPage(pageName)                     // Switch page
showToast(message, type)               // Show notification
showLoading(boolean)                   // Show/hide spinner
handleLogin(e)                         // Login form handler
handleCreateProject(e)                 // Create project handler
generateAssignment()                   // Start generation
exportProjectPDF()                     // Start PDF export
```

---

## 📝 Data Generation Example

### Assignment Generation Process
```
Input: Project with 3 papers

Process:
├─ Extract paper titles, abstracts, authors, years
├─ Build 8-section document:
│  ├─ Executive Summary
│  ├─ Introduction
│  ├─ Literature Review (includes all papers)
│  ├─ Methodology Synthesis
│  ├─ Key Findings
│  ├─ Critical Analysis
│  ├─ Implications & Recommendations
│  ├─ Conclusion
│  └─ References (formatted citations)
├─ Calculate word count (~2800+ words typical)
└─ Save to Assignment table with PDF path

Output: 
{
  "status": "success",
  "word_count": 2847,
  "citations_count": 3,
  "title": "Comprehensive Analysis: AI Ethics"
}
```

---

## 🚀 Async Job Flow

```
Frontend                    Backend                  Celery Worker         Redis
────────                    ───────                  ─────────────         ─────

Click Export ────────────→ POST /export/pdf
                           │
                           ├─ Queue celery task
                           │                 ──────→ Redis queue ────→ Worker
                           │                              │
                           ├─ Return job_id            Dequeue & run
                           │                              │
             Response   ←──┤                              ├─ Generate PDF
{job_id, status}           │                              │
   │                       │                              ├─ Save Export DB
   │                       │                              │
   └─ Poll GET /jobs/{id}──→ Check Redis status ←─────── Store result
        (every 2s)         │                           in Redis
                           └─ Return progress


Final status sequence:
pending → processing → completed
```

---

## 🔧 Configuration

### Environment Variables
```bash
SECRET_KEY="your-secret-key"           # JWT signing secret
REDIS_URL="redis://localhost:6379/0"   # Celery broker/backend
DATABASE_URL="sqlite:///./studentlabs.db" # Database connection
```

### Dependencies Summary
```
FastAPI           - Web framework
SQLAlchemy        - ORM
Celery            - Async tasks
Redis             - Message broker
ReportLab         - PDF generation
python-pptx       - PPTX generation
python-jose       - JWT tokens
passlib           - Password hashing
```

---

## ✅ Status by Component

| Feature | Status | Note |
|---------|--------|------|
| User Auth (JWT) | ✅ Complete | 30-min tokens |
| Project CRUD | ✅ Complete | Full operations |
| Paper Search | ⚠️ Mock Data | Ready for API integration |
| Assignment Gen | ✅ Complete | Sync + content generation |
| Presentation Gen | ✅ Complete | Slide JSON generation |
| PDF Export | ⚠️ Placeholder | Celery queue ready, generation pending |
| PPTX Export | ⚠️ Placeholder | Celery queue ready, generation pending |
| Async Jobs | ✅ Complete | Full Celery/Redis integration |
| Frontend UI | ✅ Complete | Dashboard + modals |

---

## 🐛 Known Issues

| Issue | Location | Severity | Fix |
|-------|----------|----------|-----|
| Bug: undefined `user_id` | generate.py:160 | High | Use `current_user.id` |
| PDF generation mock | export_tasks.py | Medium | Implement ReportLab |
| PPTX generation mock | export_tasks.py | Medium | Implement python-pptx |
| No token refresh | auth_utils.py | Medium | Add refresh token endpoint |
| SQLite in production | database.py | High | Migrate to PostgreSQL |

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Start Services
```bash
# Terminal 1: Redis
redis-server

# Terminal 2: Backend API
python run.py

# Terminal 3: Celery Worker
celery -A celery_app worker --loglevel=info

# Terminal 4: Celery Beat (optional)
celery -A celery_app beat --loglevel=info
```

### 3. Access Application
```
Frontend: http://localhost:8000
API Docs: http://localhost:8000/docs (Swagger UI)
API Redoc: http://localhost:8000/redoc
```

---

## 📊 Request/Response Examples

### Create Project
```bash
curl -X POST http://localhost:8000/api/v1/projects \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d {
    "title": "AI Ethics",
    "topic": "Ethical implications of AI"
  }
```

### Generate Assignment
```bash
curl -X POST http://localhost:8000/api/v1/generate/{project_id}/assignment \
  -H "Authorization: Bearer {token}" \
  -d {}

# Response:
{
  "status": "success",
  "project_id": 1,
  "title": "Comprehensive Analysis: AI Ethics",
  "word_count": 2847,
  "citations_count": 3
}
```

### Export to PDF (Async)
```bash
curl -X POST http://localhost:8000/api/v1/export/pdf \
  -H "Authorization: Bearer {token}" \
  -d {
    "project_id": 1,
    "assignment_id": 1
  }

# Response:
{
  "status": "queued",
  "job_id": "abc123...",
  "poll_url": "/api/v1/jobs/abc123..."
}
```

### Poll Job Status
```bash
curl http://localhost:8000/api/v1/jobs/abc123...

# Responses:
{ "status": "pending", "message": "Task waiting" }
{ "status": "processing", "progress": 50, "total": 100 }
{ "status": "completed", "result": {...} }
{ "status": "failed", "error": "..." }
```

---

## 🎓 Learning Path

1. **Understand Data Model**: Review [SYSTEM_ARCHITECTURE.md - Section 2](SYSTEM_ARCHITECTURE.md#2-database-schema)
2. **Review API Endpoints**: Check [Section 4](SYSTEM_ARCHITECTURE.md#4-api-endpoints)
3. **Study Auth Flow**: Read [Section 7](SYSTEM_ARCHITECTURE.md#7-authentication-system)
4. **Explore Backend Files**: Start with main.py, then routes/
5. **Review Frontend**: Study api.js for data flow, app.js for state management
6. **Learn Async: Read** [Section 8](SYSTEM_ARCHITECTURE.md#8-async-job-handling-celery)

---

## 📞 Support

For detailed information:
- **Backend Structure**: See SYSTEM_ARCHITECTURE.md Section 3
- **All Endpoints**: See SYSTEM_ARCHITECTURE.md Section 4
- **Data Models**: See SYSTEM_ARCHITECTURE.md Section 2
- **Workflows**: See SYSTEM_ARCHITECTURE.md Section 10
- **Issues**: See SYSTEM_ARCHITECTURE.md Section 13
