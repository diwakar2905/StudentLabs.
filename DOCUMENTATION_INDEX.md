# StudentLabs - Complete Project Documentation Index

## 📚 Documentation Overview

This folder contains **4 comprehensive documentation files** that provide complete system coverage of the StudentLabs project. Choose the document that matches your needs:

---

## 📖 Documentation Files

### 1. **SYSTEM_ARCHITECTURE.md** ⭐ START HERE
**Comprehensive technical documentation (16 sections)**

Best for: Understanding the entire system deeply

**Contents**:
- 1. Technology Stack (dependencies, frameworks, infrastructure)
- 2. Database Schema (7 tables, relationships, field documentation)
- 3. Backend File Structure (directory layout, key modules)
- 4. API Endpoints (30 endpoints across 6 routers)
- 5. Frontend Architecture (state, components, modals)
- 6. Authentication System (JWT flow, token management)
- 7. Async Job Handling (Celery configuration, tasks)
- 8. File Generation (PDF/PPTX capabilities)
- 9. Key Features & Workflows (user journey, feature status)
- 10. Component Relationships (system integration)
- 11. Environment Configuration
- 12. Known Issues & Limitations
- 13. Quick Reference table of files
- 14. Deployment Checklist
- 15. Future Enhancements
- 16. Summary

**Key Sections for Different Roles**:
- Backend Developer: Sections 2, 3, 4, 6, 7
- Frontend Developer: Section 5, 10
- DevOps/Infrastructure: Section 11, 12, 14
- Project Manager: Section 9, 15

---

### 2. **QUICK_REFERENCE.md** 🚀 QUICK START
**Quick reference guide with visual summaries**

Best for: Getting oriented quickly, finding specific information

**Contents**:
- System Overview (architecture diagram)
- User Workflow (4-step process)
- Project Structure (directory trees)
- Database Models (7 tables summary)
- API Endpoints (table of all 30 endpoints)
- Authentication Flow (visual diagram)
- Key Functions (function signatures)
- Data Generation Example
- Async Job Flow (with diagram)
- Status by Component (feature completion matrix)
- Known Issues table
- Quick Start instructions
- Request/Response Examples

**Best for**: 
- Onboarding new team members
- Finding an endpoint quickly
- Understanding workflow overview
- Command reference

---

### 3. **API_REFERENCE.md** 🔌 DETAILED REFERENCE
**Complete API documentation with all request/response examples**

Best for: Frontend developers, API integration, testing

**Contents by Endpoint**:
1. **Authentication API** (3 endpoints)
   - POST /auth/signup
   - POST /auth/login
   - GET /users/me

2. **Projects API** (6 endpoints)
   - POST /projects (create)
   - GET /projects (list)
   - GET /projects/{id} (details)
   - PUT /projects/{id} (update)
   - DELETE /projects/{id}
   - GET /projects/{id}/papers

3. **Research API** (3 endpoints)
   - POST /research/search
   - POST /research/{id}/papers/add
   - POST /research/summarize

4. **Generation API** (4 endpoints)
   - POST /generate/{id}/assignment
   - PUT /generate/{id}/assignment
   - POST /generate/{id}/ppt
   - PUT /generate/{id}/ppt

5. **Export API** (3 endpoints)
   - POST /export/pdf
   - POST /export/pptx
   - GET /export/{id}/downloads

6. **Jobs API** (3 endpoints)
   - GET /jobs/{id}
   - GET /jobs/{id}/result
   - DELETE /jobs/{id}

**Each Endpoint Includes**:
- Full request payload examples
- Response examples (success + errors)
- Field descriptions
- Validation rules
- Error handling

**Additional Coverage**:
- HTTP Status Codes
- Error Response Format
- Authentication Header Format
- Rate Limiting info
- Pagination info
- CORS Configuration

---

### 4. **WORKFLOWS_DIAGRAMS.md** 📊 VISUAL GUIDE
**System workflows and data flow diagrams**

Best for: Understanding processes, data flow, integration points

**Contents**:
1. **Project Lifecycle Workflow** - Complete 7-step process
2. **Authentication & Session Management** - Login/logout flow with JWT
3. **Assignment Generation** - Sync content generation process
4. **Export (PDF/PPTX) Async Flow** - Celery job queue flow
5. **Data Flow** - Single request lifecycle example
6. **Database Relationships** - Visual entity relationship
7. **Component Integration Map** - All system components
8. **Request/Response Cycle** - Detailed timeline example

**Diagrams Include**:
- ASCII art flowcharts
- Step-by-step processes
- State transitions
- Data transformations
- Timing information
- Component interactions

---

## 🎯 Quick Navigation

### I need to...

**Understand the overall system**
→ Read: QUICK_REFERENCE.md (Sections 1-2) + SYSTEM_ARCHITECTURE.md (Section 1)

**Set up development environment**
→ Read: QUICK_REFERENCE.md (Quick Start) + SYSTEM_ARCHITECTURE.md (Section 11)

**Work on backend endpoints**
→ Read: API_REFERENCE.md (for endpoint specs) + SYSTEM_ARCHITECTURE.md (Section 4)

**Work on frontend**
→ Read: SYSTEM_ARCHITECTURE.md (Section 5) + API_REFERENCE.md (each endpoint)

**Integrate with Celery/Redis**
→ Read: SYSTEM_ARCHITECTURE.md (Section 8) + WORKFLOWS_DIAGRAMS.md (Section 4)

**Understand data flow**
→ Read: WORKFLOWS_DIAGRAMS.md (Sections 5-8) + SYSTEM_ARCHITECTURE.md (Section 2)

**Set up database**
→ Read: SYSTEM_ARCHITECTURE.md (Section 2) + SYSTEM_ARCHITECTURE.md (Section 14)

**Debug authentication issues**
→ Read: SYSTEM_ARCHITECTURE.md (Section 7) + WORKFLOWS_DIAGRAMS.md (Section 2)

**Add new API endpoint**
→ Read: API_REFERENCE.md (similar endpoint) + SYSTEM_ARCHITECTURE.md (Section 4)

**Deploy to production**
→ Read: SYSTEM_ARCHITECTURE.md (Sections 11, 13, 14)

**Find a known bug**
→ Read: SYSTEM_ARCHITECTURE.md (Section 13)

---

## 🔑 Key Facts at a Glance

| Aspect | Details |
|--------|---------|
| **API Base URL** | `http://localhost:8000/api/v1` |
| **Database** | SQLite (dev), PostgreSQL ready |
| **Authentication** | JWT with 30-min expiry |
| **Async Processing** | Celery + Redis |
| **Frontend** | Vanilla JavaScript, no framework |
| **Total Endpoints** | 30 across 6 routers |
| **Database Tables** | 7 (User, Project, Paper, Summary, Assignment, Presentation, Export) |
| **Async Tasks** | 5 Celery tasks (2 generation, 2 export, 1 health check) |

---

## 📋 System Components

### Backend Files
- `main.py` - FastAPI app setup
- `models.py` - 7 ORM models
- `database.py` - SQLAlchemy config
- `auth_utils.py` - JWT & password utilities
- `celery_app.py` - Celery + Redis setup
- `routes/` - 6 API routers (30 endpoints)
- `tasks/` - 5 Celery async tasks

### Frontend Files
- `index.html` - Dashboard structure
- `app.js` - Application logic
- `api.js` - API service layer
- `styles.css` - UI styling

### Infrastructure
- SQLite database: `studentlabs.db`
- Redis: `localhost:6379/0`
- Port: `8000`

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
cd backend
pip install -r requirements.txt

# 2. Start Redis
redis-server

# 3. Start backend
python run.py

# 4. Start Celery worker (new terminal)
celery -A celery_app worker --loglevel=info

# 5. Access
# Frontend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

---

## 📊 Feature Status

| Feature | Status | Notes |
|---------|--------|-------|
| User Authentication | ✅ Complete | JWT tokens, 30-min expiry |
| Project Management | ✅ Complete | Full CRUD operations |
| Paper Search | ⚠️ Mock Data | Ready for API integration |
| Assignment Generation | ✅ Complete | 8-section rich content |
| Presentation Generation | ✅ Complete | 5-slide structure |
| PDF Export | ⚠️ Placeholder | Celery queue ready, generation pending |
| PPTX Export | ⚠️ Placeholder | Celery queue ready, generation pending |
| Async Job Tracking | ✅ Complete | Full Celery + Redis integration |
| Frontend UI | ✅ Complete | Dashboard, modals, responsive |

---

## 🐛 Known Issues

1. **Bug in generate.py:160** - Uses undefined `user_id` instead of `current_user.id`
2. **PDF Generation** - Mock implementation only
3. **PPTX Generation** - Mock implementation only
4. **Token Refresh** - Not implemented (30-min expiry only)
5. **Database** - SQLite not production-ready

See SYSTEM_ARCHITECTURE.md Section 13 for details.

---

## 🔐 Authentication

**Method**: JWT (JSON Web Tokens)
**Expiry**: 30 minutes
**Algorithm**: HS256

**Header Format**:
```
Authorization: Bearer <token>
```

**Token Payload**:
```json
{
  "sub": 1,
  "email": "user@example.com",
  "exp": 1705318200
}
```

---

## 🌐 API Endpoint Groups

### Authentication (3 endpoints)
```
POST   /auth/signup              Register
POST   /auth/login               Authenticate
GET    /users/me                 Get profile
```

### Projects (6 endpoints)
```
POST   /projects                 Create
GET    /projects                 List all
GET    /projects/{id}            Get details
PUT    /projects/{id}            Update
DELETE /projects/{id}            Delete
GET    /projects/{id}/papers     List papers
```

### Research (3 endpoints)
```
POST   /research/search                    Search papers
POST   /research/{id}/papers/add           Add papers
POST   /research/summarize                 Summarize paper
```

### Generation (4 endpoints)
```
POST   /generate/{id}/assignment          Generate
PUT    /generate/{id}/assignment          Update
POST   /generate/{id}/ppt                  Generate
PUT    /generate/{id}/ppt                  Update
```

### Export (3 endpoints)
```
POST   /export/pdf                        Queue PDF export
POST   /export/pptx                       Queue PPTX export
GET    /export/{id}/downloads             List exports
```

### Jobs (3 endpoints)
```
GET    /jobs/{id}                Poll status
GET    /jobs/{id}/result         Get result
DELETE /jobs/{id}                Cancel
```

---

## 💾 Database Schema Overview

```
User ──┬── Project ──┬── Paper
       │             ├── Summary
       │             ├── Assignment
       │             ├── Presentation
       │             └── Export
```

**Quick Schema**:
- User: id, email, name, password_hash, plan, created_at
- Project: id, user_id, title, topic, status, created_at, updated_at
- Paper: id, project_id, paper_id, title, abstract, authors, year, url
- Assignment: id, project_id, title, content, citations (JSON), created_at
- Presentation: id, project_id, slides_json (JSON), created_at
- Export: id, project_id, file_type, file_path, file_url, created_at
- Summary: id, project_id, content, created_at

---

## 🔄 Async Job Flow

```
Frontend Click
    ↓
POST /export/pdf (returns job_id immediately)
    ↓
Job queued in Redis
    ↓
Celery Worker picks up task
    ↓
Task execution (background)
    ↓
Result stored in Redis (1 hour TTL)
    ↓
Frontend polls GET /jobs/{job_id} every 2s
    ↓
Status: pending → processing → completed
    ↓
Frontend displays result
```

---

## 🛠️ Development Tips

### Adding a New Endpoint

1. Create route in `routes/your_route.py`
2. Import in `main.py`
3. Mount in `main.py`: `app.include_router(...)`
4. Document in API_REFERENCE.md
5. Test via `/docs` Swagger UI

### Debugging

```bash
# View API Docs
http://localhost:8000/docs

# View Celery tasks
celery -A celery_app inspect active

# Check Redis
redis-cli
> KEYS *
> GET key_name

# Database
sqlite3 studentlabs.db
> SELECT * FROM users;
```

### Common Errors

- **401 Unauthorized**: Missing/invalid token
- **404 Not Found**: Project doesn't exist or user doesn't own it
- **502 Bad Gateway**: Backend/Celery worker not running
- **Task timeout**: Increase time limits in celery_app.py

---

## 📞 Support & Resources

**For Detailed Information, See**:

| Topic | File | Section |
|-------|------|---------|
| Architecture | SYSTEM_ARCHITECTURE.md | All |
| APIs | API_REFERENCE.md | By endpoint |
| Workflows | WORKFLOWS_DIAGRAMS.md | By process |
| Quick Start | QUICK_REFERENCE.md | Quick Start |
| Database | SYSTEM_ARCHITECTURE.md | Section 2 |
| Auth | SYSTEM_ARCHITECTURE.md | Section 7 |
| Async | SYSTEM_ARCHITECTURE.md | Section 8 |
| Issues | SYSTEM_ARCHITECTURE.md | Section 13 |
| Deployment | SYSTEM_ARCHITECTURE.md | Section 14 |

---

## ✅ Verification Checklist

Before starting development, verify:

- [ ] Backend runs on http://localhost:8000
- [ ] Frontend loads (http://localhost:8000/dashboard)
- [ ] Can register new user (POST /auth/signup)
- [ ] Can login (POST /auth/login)
- [ ] Can create project (POST /projects)
- [ ] Can search papers (POST /research/search)
- [ ] Celery worker running and accepting tasks
- [ ] Redis running and accessible
- [ ] Database tables created (sqlite3 studentlabs.db)

---

## 📁 File Paths Quick Reference

| File | Purpose | Location |
|------|---------|----------|
| Main app | FastAPI setup | backend/main.py |
| Models | Database schemas | backend/models.py |
| DB config | SQLAlchemy setup | backend/database.py |
| JWT utils | Token management | backend/auth_utils.py |
| Celery | Async config | backend/celery_app.py |
| Auth routes | Login/signup | backend/routes/auth.py |
| Project routes | CRUD ops | backend/routes/projects.py |
| Research routes | Paper search | backend/routes/research.py |
| Generate routes | Content gen | backend/routes/generate.py |
| Export routes | File export | backend/routes/export.py |
| Jobs routes | Async tracking | backend/routes/jobs.py |
| Gen tasks | Content tasks | backend/tasks/generation_tasks.py |
| Export tasks | File tasks | backend/tasks/export_tasks.py |
| Frontend app | App logic | frontend/app.js |
| API service | HTTP client | frontend/api.js |
| HTML | Structure | frontend/index.html |
| Styling | CSS | frontend/styles.css |

---

## 🎓 Learning Progression

**Beginner** (1-2 hours):
1. Read QUICK_REFERENCE.md (Sections 1-3)
2. Run quick start
3. Try login/create project via frontend
4. View API docs at /docs

**Intermediate** (3-5 hours):
1. Read SYSTEM_ARCHITECTURE.md (Sections 1-7)
2. Study API_REFERENCE.md (pick a few endpoints)
3. Trace code from frontend HTTP call → backend handler → database
4. Run workflow: create project → add papers → generate assignment

**Advanced** (full day):
1. Deep dive: SYSTEM_ARCHITECTURE.md (all sections)
2. Study WORKFLOWS_DIAGRAMS.md
3. Set up Celery worker, test async tasks
4. Review all code files
5. Plan modifications/enhancements

---

## 🚀 Next Steps

1. **Choose your role**: Backend / Frontend / DevOps / Full-stack
2. **Read relevant documentation** (see Quick Navigation section)
3. **Run Quick Start** (see QUICK_REFERENCE.md)
4. **Pick a feature to work on** (see Section 15 in SYSTEM_ARCHITECTURE.md)
5. **Reference the API docs** (see API_REFERENCE.md)
6. **Debug using tips** (see Development Tips section above)

---

## 📝 Notes

- All documentation is current as of project snapshot
- Code examples assume Python 3.8+, modern browsers
- Production deployment requires additional steps (see Section 14 in SYSTEM_ARCHITECTURE.md)
- Future enhancements planned (see Section 15 in SYSTEM_ARCHITECTURE.md)

---

**Happy coding! 🚀**

For questions or clarifications, refer to the specific documentation file most relevant to your question.
