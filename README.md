# StudentLabs 📚

**AI-Powered Academic Research, Assignment Generation, and Presentation Creation Platform**

Transform research papers into polished assignments and presentations with intelligent paper discovery, AI-powered content generation, and professional export capabilities.

---

## 🎯 Quick Overview

**StudentLabs** is a full-stack web application that streamlines academic work:
1. **Search** millions of academic papers
2. **Select** relevant papers for your topic
3. **Generate** comprehensive assignments automatically
4. **Create** presentation slides in seconds
5. **Export** as PDF or PowerPoint files

**Tech Stack**: FastAPI (Backend) + Vanilla JavaScript (Frontend) + SQLite (Database) + Celery (Async Jobs)

---

## 📋 Documentation Index

Start with the comprehensive documentation created for this project:

| Document | Purpose |
|----------|---------|
| **[DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)** | 🗂️ **START HERE** - Central navigation hub |
| **[SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md)** | 🏗️ Complete technical reference (16 sections, database schema, all endpoints) |
| **[API_REFERENCE.md](API_REFERENCE.md)** | 🔌 All 30 API endpoints with request/response examples |
| **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** | ⚡ Quick lookup tables and ASCII diagrams |
| **[WORKFLOWS_DIAGRAMS.md](WORKFLOWS_DIAGRAMS.md)** | 📊 Visual flowcharts for all major workflows |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Optional: Redis (for Celery task queue)

### Installation & Running

```bash
# 1. Navigate to backend
cd backend

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the server
python run.py
```

**Server starts at**: `http://localhost:8000`

| URL | Purpose |
|-----|---------|
| `http://localhost:8000/` | Landing page |
| `http://localhost:8000/dashboard` | Main application dashboard |
| `http://localhost:8000/docs` | Interactive API documentation (Swagger) |
| `http://localhost:8000/redoc` | Alternative API documentation |

---

## 📁 Project Structure

```
StudentLabs/
├── backend/                          # FastAPI application
│   ├── main.py                      # FastAPI app initialization & routing
│   ├── database.py                  # SQLAlchemy ORM setup & models
│   ├── auth_utils.py                # JWT token & password utilities
│   ├── celery_app.py                # Celery async task configuration
│   ├── run.py                       # Server startup script
│   ├── requirements.txt             # Python dependencies
│   ├── routes/                      # API endpoint routers
│   │   ├── auth.py                  # Authentication (signup, login, logout)
│   │   ├── projects.py              # Project management (CRUD)
│   │   ├── research.py              # Paper search & summarization
│   │   ├── generate.py              # Assignment & presentation generation
│   │   ├── export.py                # PDF & PowerPoint export
│   │   └── jobs.py                  # Async job status tracking
│   └── tasks/                       # Celery async tasks
│       ├── generation_tasks.py      # Assignment & presentation generation tasks
│       └── export_tasks.py          # PDF & PowerPoint export tasks
│
├── frontend/                         # Frontend application
│   ├── index.html                   # Dashboard HTML structure
│   ├── styles.css                   # Dashboard styling
│   └── scripts/
│       ├── api.js                   # API service layer (25+ methods)
│       └── app.js                   # Application logic & UI management
│
├── assets/                           # Static assets
│   ├── css/
│   │   └── style.css                # Landing page styles
│   ├── js/
│   │   └── main.js                  # Landing page scripts
│   └── img/                         # Images & icons
│
├── index.html                       # Landing page
├── DOCUMENTATION_INDEX.md           # Central documentation navigation
├── SYSTEM_ARCHITECTURE.md           # Complete technical reference
├── API_REFERENCE.md                 # All endpoints documented
├── QUICK_REFERENCE.md               # Quick lookup tables
└── WORKFLOWS_DIAGRAMS.md            # Visual flowcharts
```

---

## 🏗️ System Architecture

### High-Level Architecture

```
┌─────────────────┐
│   Browsers      │  (Users access via web)
└────────┬────────┘
         │ HTTP/HTTPS
         ▼
┌─────────────────────────────────────────┐
│    FastAPI Backend (Python)             │
│  ┌──────────────────────────────────┐   │
│  │ API Routes (30 endpoints)        │   │
│  │ - Auth (3)                       │   │
│  │ - Projects (5)                   │   │
│  │ - Research (5)                   │   │
│  │ - Generate (6)                   │   │
│  │ - Export (6)                     │   │
│  │ - Jobs (5)                       │   │
│  └──────────────────────────────────┘   │
│           ↓                              │
│  ┌──────────────────────────────────┐   │
│  │ SQLAlchemy ORM                   │   │
│  │ (7 Database Models)              │   │
│  └──────────────────────────────────┘   │
└─────────────┬───────────────────────────┘
              │
       ┌──────┴──────┐
       ▼             ▼
    ┌─────┐      ┌──────────┐
    │ DB  │      │  Celery  │
    │     │      │ Workers  │
    └─────┘      └────┬─────┘
                  (Async Jobs)
                      │
                      ▼
                  ┌──────────┐
                  │  Redis   │
                  │  Queue   │
                  └──────────┘
```

### Database Schema (7 Tables)

| Table | Purpose | Key Fields |
|-------|---------|-----------|
| **users** | User accounts | id, email, password_hash, full_name, created_at |
| **projects** | Research projects | id, user_id, title, description, created_at |
| **papers** | Academic papers | id, project_id, title, authors, abstract, url |
| **summaries** | Paper summaries | id, paper_id, summary_text, key_points |
| **assignments** | Generated assignments | id, project_id, title, content, status |
| **presentations** | Generated presentations | id, project_id, title, slides, status |
| **exports** | Exported files | id, user_id, filename, file_type, path, job_id |

### API Router Organization

| Router | Endpoints | Purpose |
|--------|-----------|---------|
| **auth.py** | 3 + 1 | User registration, login, logout, profile |
| **projects.py** | 5 | Create, read, update, delete projects |
| **research.py** | 5 | Search papers, add to project, summarize |
| **generate.py** | 6 | Assignment & presentation generation (sync & async) |
| **export.py** | 6 | PDF & PPTX export (sync & async) |
| **jobs.py** | 5 | Track async job status, get results, cancel |

---

## 🔄 Core Workflows

### User Workflow: Research → Generate → Export

```
1. User Signs Up/Logs In
   ↓
2. Creates a Project
   ↓
3. Searches Academic Papers
   ↓
4. Selects Relevant Papers
   ↓
5. Generates Assignment (AI synthesizes from papers)
   ↓
6. Generates Presentation (AI creates slides)
   ↓
7. Exports as PDF/PowerPoint
   ↓
8. Downloads Files
```

### Authentication Flow

```
Client                          Server
  │                              │
  ├── POST /auth/signup ────────>│ Hash password, create user
  │                              │
  │<───── JWT Token ─────────────┤
  │                              │
  ├── Store token in localStorage
  │                              │
  ├── Include in Authorization header: "Bearer {token}"
  │                              │
  └──> All subsequent requests are authenticated
```

### Async Job Processing (Celery)

```
Request                Queue               Worker              Database
  │                      │                   │                    │
  ├─> /generate/async ──>│ Add to queue      │                    │
  │   Returns job_id     │                   │                    │
  │                      │                   ├─ Process task      │
  │<─── job_id ──────────┤                   │   (generation)     │
  │                      │                   ├─ Store result ────>│
  │ Poll /jobs/{id}      │                   │
  │────────────────────>│ Check status      │
  │                      │<─ Status ────────── ✓ Completed
  │<─ Result ────────────┤
```

---

## 🔑 Key Features

### 1. **Authentication System**
- User registration with email validation
- Password hashing with bcrypt
- JWT tokens with 30-minute expiry
- Token refresh capability
- Profile management

### 2. **Project Management**
- Create, read, update, delete projects
- Organize papers by project
- Track project history
- Associate assignments & presentations with projects

### 3. **Research Capability**
- Search millions of academic papers (via API integration)
- View paper details (title, authors, abstract, URL)
- Add papers to projects
- Summarize paper content using PDF text extraction
- Store summaries for offline access

### 4. **Content Generation**
- **Assignment Writer**: Generated structured academic assignments from selected papers
- **Presentation Generator**: Create presentation slides with AI-generated content
- Synchronous & asynchronous processing
- Real-time status tracking

### 5. **Export System**
- Export to PDF format
- Export to PowerPoint (PPTX) format
- Async processing for large files
- File storage with access URLs
- Download management

### 6. **Async Job Management**
- Queue long-running tasks (Celery)
- Track job progress
- Get results when complete
- Cancel pending jobs
- Job status: queued → processing → completed/failed

---

## 🔌 API Endpoints Summary

### Authentication (3 endpoints)
```
POST   /api/v1/auth/signup          # Register new user
POST   /api/v1/auth/login           # Login & get JWT token
POST   /api/v1/auth/logout          # Logout (invalidate session)
GET    /api/v1/users/me             # Get current user profile
```

### Projects (5 endpoints)
```
POST   /api/v1/projects             # Create project
GET    /api/v1/projects             # List user's projects
GET    /api/v1/projects/{id}        # Get project details
PUT    /api/v1/projects/{id}        # Update project
DELETE /api/v1/projects/{id}        # Delete project
```

### Research (5 endpoints)
```
GET    /api/v1/research/search      # Search academic papers
POST   /api/v1/research/papers      # Add paper to project
GET    /api/v1/projects/{id}/papers # List papers in project
POST   /api/v1/research/summarize   # Summarize paper content
GET    /api/v1/research/summary/{id}# Get stored summary
```

### Generation (6 endpoints)
```
POST   /api/v1/generate/assignment  # Generate assignment (sync)
POST   /api/v1/generate/assignment/async  # Generate assignment (async)
GET    /api/v1/generate/assignment/{id}   # Get assignment
PUT    /api/v1/generate/assignment/{id}   # Update assignment
POST   /api/v1/generate/ppt         # Generate presentation (sync)
POST   /api/v1/generate/ppt/async   # Generate presentation (async)
```

### Export (6 endpoints)
```
POST   /api/v1/export/pdf           # Export to PDF (sync)
POST   /api/v1/export/pdf/async     # Export to PDF (async)
POST   /api/v1/export/pptx          # Export to PPTX (sync)
POST   /api/v1/export/pptx/async    # Export to PPTX (async)
GET    /api/v1/export/list          # List exported files
GET    /api/v1/export/{id}          # Download export
```

### Jobs (5 endpoints)
```
GET    /api/v1/jobs/{id}            # Get job status
GET    /api/v1/jobs/{id}/result     # Get job result
POST   /api/v1/jobs/{id}/cancel     # Cancel job
GET    /api/v1/jobs                 # List all jobs
GET    /api/v1/jobs/health          # Check Celery health
```

📖 **For complete endpoint documentation**, see [API_REFERENCE.md](API_REFERENCE.md)

---

## 💾 Database Models

### User Model
```python
- id: Integer (Primary Key)
- email: String (Unique)
- password_hash: String
- full_name: String
- created_at: DateTime
```

### Project Model
```python
- id: Integer (Primary Key)
- user_id: Integer (Foreign Key)
- title: String
- description: String
- created_at: DateTime
- updated_at: DateTime
```

### Paper Model
```python
- id: Integer (Primary Key)
- project_id: Integer (Foreign Key)
- title: String
- authors: String
- abstract: String
- url: String
- added_at: DateTime
```

### Summary Model
```python
- id: Integer (Primary Key)
- paper_id: Integer (Foreign Key)
- summary_text: String
- key_points: String (JSON)
- created_at: DateTime
```

### Assignment Model
```python
- id: Integer (Primary Key)
- project_id: Integer (Foreign Key)
- title: String
- content: String (Large text)
- status: String (draft/completed)
- created_at: DateTime
- updated_at: DateTime
```

### Presentation Model
```python
- id: Integer (Primary Key)
- project_id: Integer (Foreign Key)
- title: String
- slides: String (JSON array)
- status: String (draft/completed)
- created_at: DateTime
- updated_at: DateTime
```

### Export Model
```python
- id: Integer (Primary Key)
- user_id: Integer (Foreign Key)
- filename: String
- file_type: String (pdf/pptx)
- file_path: String
- job_id: String
- created_at: DateTime
```

---

## 🛠️ Technology Stack

### Backend
| Technology | Purpose |
|-----------|---------|
| **FastAPI** | Web framework for REST API |
| **Uvicorn** | ASGI server (async HTTP) |
| **SQLAlchemy** | ORM for database operations |
| **Pydantic** | Data validation & serialization |
| **python-jose** | JWT token creation & validation |
| **passlib** | Password hashing |
| **ReportLab** | PDF generation |
| **python-pptx** | PowerPoint file creation |
| **Celery** | Async task queue |
| **Redis** | Task queue broker |

### Frontend
| Technology | Purpose |
|-----------|---------|
| **Vanilla JavaScript** | No frameworks, pure JS |
| **Fetch API** | HTTP requests to backend |
| **LocalStorage** | JWT token persistence |
| **CSS3** | Modern styling with variables |
| **HTML5** | Semantic markup |

### Database
| Technology | Purpose |
|-----------|---------|
| **SQLite** | Development database |
| **PostgreSQL** | Production-ready (configured) |

---

## ⚙️ Configuration

### Environment Setup
Create a `.env` file in the `backend/` directory:

```env
# Database
DATABASE_URL=sqlite:///./database.db

# JWT
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=["http://localhost:8000", "http://localhost:3000"]

# File Upload
MAX_FILE_SIZE=10485760  # 10MB

# Celery/Redis (optional)
REDIS_URL=redis://localhost:6379/0
```

### Running with PostgreSQL (Production)
```python
# Update DATABASE_URL in .env or main.py:
DATABASE_URL=postgresql://user:password@localhost:5432/studentlabs_db
```

---

## 🚀 Deployment

### Running Backend in Production
```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

### Using Docker (Optional)
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Celery Worker Setup
```bash
# Terminal 1: Start Celery worker
celery -A celery_app worker --loglevel=info

# Terminal 2: Start Redis server
redis-server

# Terminal 3: Run FastAPI server
python run.py
```

---

## 📊 Data Flow Diagram

```
User Interaction Flow:

1. Signup/Login
   Browser → FastAPI → Database
   ← JWT Token

2. Create Project
   Browser → POST /projects → Database
   ← Project ID

3. Search Papers
   Browser → GET /research/search → External API
   ← Paper List

4. Add Papers
   Browser → POST /papers → Database
   ← Paper Added

5. Generate Assignment (Async)
   Browser → POST /generate/assignment/async
   ← Job ID (queued)
   Browser → GET /jobs/{id} (polling)
   ← Status: Processing → Completed

6. Export to PDF
   Browser → POST /export/pdf → Celery Worker
   ← File generated → Download Link

7. Download
   Browser → GET /export/{id}
   ← Download file
```

---

## 🔐 Security Features

- ✅ **JWT Authentication**: Secure token-based auth
- ✅ **Password Hashing**: bcrypt with salt
- ✅ **CORS Protection**: Configurable origin whitelist
- ✅ **Input Validation**: Pydantic models validate all input
- ✅ **SQL Injection Prevention**: SQLAlchemy parameterized queries
- ✅ **Token Expiry**: 30-minute expiry with refresh capability
- ✅ **Environment Variables**: Secrets not hardcoded

---

## 📈 Performance Considerations

| Optimization | Implementation |
|--------------|-----------------|
| **Async Processing** | Celery + Redis for long-running tasks |
| **Database Indexing** | Primary keys, foreign keys indexed |
| **API Caching** | LocalStorage for client-side caching |
| **Lazy Loading** | Papers loaded on-demand |
| **Connection Pooling** | SQLAlchemy connection pooling |
| **Compression** | Static file compression via FastAPI |

---

## 🧪 Testing

### Test Backend Endpoints
```bash
# Navigate to backend
cd backend

# Run tests
pytest test_app.py -v
```

### Manual API Testing
```bash
# Using curl
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"pass123","full_name":"John Doe"}'

# Using Python
import requests
response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    json={"email": "user@example.com", "password": "pass123"}
)
print(response.json())
```

---

## 🐛 Troubleshooting

### Port 8000 Already in Use
```bash
# Kill process on port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:8000 | xargs kill -9
```

### Database Connection Error
```bash
# Delete old database and reinitialize
rm database.db
python run.py
```

### Celery Tasks Not Processing
```bash
# Start Redis server:
redis-server

# In separate terminal, start Celery worker:
celery -A celery_app worker --loglevel=info
```

### Module Import Errors
```bash
# Reinstall requirements
pip install --force-reinstall -r requirements.txt
```

---

## 📚 Further Reading

- **[DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)** - Navigation hub for all docs
- **[SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md)** - Technical deep dive
- **[API_REFERENCE.md](API_REFERENCE.md)** - Complete endpoint reference
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Quick lookup tables
- **[WORKFLOWS_DIAGRAMS.md](WORKFLOWS_DIAGRAMS.md)** - Visual flowcharts

---

## 📝 Project Timeline

| Phase | Features | Status |
|-------|----------|--------|
| **Phase 1** | Backend API with 30 endpoints | ✅ Complete |
| **Phase 2** | Frontend dashboard | ✅ Complete |
| **Phase 3** | Authentication system | ✅ Complete |
| **Phase 4** | Paper search & management | ✅ Complete |
| **Phase 5** | Content generation (async) | ✅ Complete |
| **Phase 6** | File export (PDF/PPTX) | ✅ Complete |
| **Phase 7** | Landing page redesign | ✅ Complete |

---

## 🤝 Contributing

Guidelines for extending the project:

1. **Adding New Endpoints**: Create route in `routes/` folder
2. **Adding Database Models**: Update `database.py` with new model
3. **Adding Async Tasks**: Create task in `tasks/` folder
4. **Frontend Changes**: Update `frontend/app.js` and `frontend/index.html`

---

## 📞 Support

For detailed technical information:
- See [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md) for architecture
- See [API_REFERENCE.md](API_REFERENCE.md) for endpoint details
- See [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for quick lookups
- See [WORKFLOWS_DIAGRAMS.md](WORKFLOWS_DIAGRAMS.md) for visual flows

---

**StudentLabs** - Transform research into excellence 🚀
