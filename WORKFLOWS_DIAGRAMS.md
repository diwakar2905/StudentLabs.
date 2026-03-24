# StudentLabs - System Workflows & Diagrams

## 1. Project Lifecycle Workflow

```
┌──────────────────────────────────────────────────────────────────┐
│                    PROJECT LIFECYCLE                             │
└──────────────────────────────────────────────────────────────────┘

User Logs In
    │
    ↓
┌─────────────────────────────────────────────────────────┐
│  CREATE PROJECT                                         │
│  - Input: Title, Topic                                 │
│  - Action: POST /projects                              │
│  - Result: Project created with status="draft"         │
└─────────────────────────────────────────────────────────┘
    │
    ↓
┌─────────────────────────────────────────────────────────┐
│  RESEARCH PHASE                                         │
│  - Search: POST /research/search → Get papers          │
│  - Select papers from results                          │
│  - Add: POST /research/{id}/papers/add                 │
│  - Result: Papers stored in Paper table                │
│  - Update: project.papers_count incremented            │
└─────────────────────────────────────────────────────────┘
    │
    ↓
┌─────────────────────────────────────────────────────────┐
│  GENERATION PHASE 1: ASSIGNMENT                         │
│  - Trigger: POST /generate/{id}/assignment             │
│  - Action: Server processes papers                     │
│  - Generation:                                         │
│    • Extract paper metadata & abstracts                │
│    • Build rich document (8 sections)                  │
│    • Format citations                                  │
│    • Calculate word count                              │
│  - Result: Assignment created, saved to DB             │
│  - Update: project.has_assignment = true               │
└─────────────────────────────────────────────────────────┘
    │
    ↓
┌─────────────────────────────────────────────────────────┐
│  GENERATION PHASE 2: PRESENTATION                       │
│  - Trigger: POST /generate/{id}/ppt                    │
│  - Action: Create slide structure                      │
│  - Slides created:                                     │
│    1. Title slide                                      │
│    2. Key Concepts                                     │
│    3. Literature Review                                │
│    4. Key Findings                                     │
│    5. Conclusion & Future Directions                   │
│  - Result: Presentation created, saved as JSON         │
│  - Update: project.has_presentation = true             │
└─────────────────────────────────────────────────────────┘
    │
    ↓
┌─────────────────────────────────────────────────────────┐
│  EXPORT PHASE                                           │
│  - Option 1: Export to PDF                             │
│    • Trigger: POST /export/pdf (async via Celery)      │
│  - Option 2: Export to PowerPoint                      │
│    • Trigger: POST /export/pptx (async via Celery)     │
│  - Frontend: Poll /jobs/{job_id} every 2 seconds       │
│  - Result: Export record created, file generated       │
│  - Update: project.exports_count incremented           │
└─────────────────────────────────────────────────────────┘
    │
    ↓
┌─────────────────────────────────────────────────────────┐
│  DOWNLOAD                                               │
│  - User retrieves file from Export.file_url            │
│  - Or queries: GET /export/{id}/downloads              │
│  - Project completed (status can be "completed")       │
└─────────────────────────────────────────────────────────┘
```

---

## 2. Authentication & Session Management

```
┌─────────────────────────────────────────────────────────────────┐
│                 AUTHENTICATION FLOW                             │
└─────────────────────────────────────────────────────────────────┘

NEW USER PATH:
───────────────

User visits: http://localhost:8000/dashboard
    │
    ↓
Frontend detects: No token in localStorage
    │
    ↓
┌──────────────────────────────┐
│   Show Auth Screen           │
│   - Login Form               │
│   - Register Form            │
└──────────────────────────────┘
    │
    ├─→ Click "Sign Up"
    │       │
    │       ↓
    │   Input: name, email, password
    │       │
    │       ↓
    │   POST /auth/signup
    │       │
    │       Backend:
    │       • Validate input
    │       • Hash password (bcrypt)
    │       • Check email uniqueness
    │       • Store in User table
    │       │
    │       ↓
    │   Response: UserResponse (201)
    │       │
    │       ↓
    │   Frontend: Show success, switch to login
    │
    │
    ├─→ Click "Login"
            │
            ↓
        Input: email, password
            │
            ↓
        POST /auth/login
            │
            Backend:
            • Lookup user by email
            • Verify password (bcrypt.verify)
            • Create JWT token (30 min expiry)
            • Return: token + user info
            │
            ↓
        Response: {token, user, token_type}
            │
            ↓
        Frontend:
        • Save token: localStorage.setItem('auth_token', token)
        • Set currentUser state
        • Show Dashboard
            │
            ↓
        ┌──────────────────────────────┐
        │   Authenticated Session      │
        │   Token included in every    │
        │   request header:            │
        │   Authorization: Bearer {token}
        └──────────────────────────────┘


SESSION CONTINUATION:
─────────────────────

User closes and reopens http://localhost:8000/dashboard
    │
    ↓
Frontend: document.addEventListener('DOMContentLoaded')
    │
    ↓
Check: const token = localStorage.getItem('auth_token')
    │
    ├─→ Token exists
    │       │
    │       ↓
    │   GET /users/me (with token in header)
    │       │
    │       Backend:
    │       • Verify JWT signature
    │       • Check expiration
    │       • Return user info
    │       │
    │       ↓
    │   ✓ Token valid → Show Dashboard
    │
    │
    ├─→ Token doesn't exist or expired
            │
            ↓
        Show Auth Screen again


TOKEN EXPIRATION (30 minutes):
──────────────────────────────

After 30 minutes of login:
    │
    ↓
Next API request
    │
    ↓
Backend: verify_access_token(token)
    │
    ├─→ exp timestamp < now()
    │       │
    │       ↓
    │   Raise: JWTError
    │       │
    │       ↓
    │   Response: 401 Unauthorized
    │       │
    │       ↓
    │   Frontend catches error
    │       │
    │       ↓
    │   Clear token: localStorage.removeItem('auth_token')
    │   Clear user state: currentUser = null
    │       │
    │       ↓
    │   Redirect to Auth Screen
    │       │
    │       ↓
    │   User must login again


LOGOUT:
───────

User clicks "Logout"
    │
    ↓
Frontend: api.logout()
    │
    ├─ localStorage.removeItem('auth_token')
    ├─ currentUser = null
    └─→ showAuthScreen()
```

---

## 3. Assignment Generation Async Flow

```
┌────────────────────────────────────────────────────────────────┐
│          ASSIGNMENT GENERATION (SYNC + CELERY)                 │
└────────────────────────────────────────────────────────────────┘

FRONTEND:
─────────
User clicks "Generate Assignment"
    │
    ↓
JavaScript: generateAssignment()
    │
    ↓
api.generateAssignment(projectId)
    │
    ↓
POST /generate/{projectId}/assignment
    │
    ├─ Headers: Authorization: Bearer {token}
    └─ Body: { paper_ids: [...] } (optional)


BACKEND - SYNCHRONOUS:
──────────────────────

Receive request at POST /generate/{projectId}/assignment
    │
    ↓
┌────────────────────────────────────────────────┐
│ Generate Assignment Route Handler              │
│ (routes/generate.py)                           │
├────────────────────────────────────────────────┤
│                                                │
│ 1. get_current_user(Authorization header)     │
│    → Verify JWT, get User object               │
│                                                │
│ 2. db.query(Project)                           │
│    → Verify project ownership                  │
│    → Status: 404 if not found/owned            │
│                                                │
│ 3. Update project.status = "in_progress"      │
│                                                │
│ 4. Get papers: db.query(Paper)                │
│    → Filter by project_id                      │
│    → Extract: title, abstract, authors, year  │
│                                                │
│ 5. Generate Assignment:                        │
│    ├─ Create title from topic                 │
│    ├─ Build literature review from papers    │
│    ├─ Add executive summary                   │
│    ├─ Add methodology, findings, analysis     │
│    ├─ Add recommendations & future directions │
│    ├─ Format APA-style citations             │
│    ├─ Build citations JSON                   │
│    └─ Calculate word count                   │
│                                                │
│ 6. Save to Database:                          │
│    ├─ Check if Assignment exists              │
│    ├─ If exists: UPDATE Assignment            │
│    ├─ If not: INSERT new Assignment           │
│    └─ db.commit()                             │
│                                                │
│ 7. Return Response (200 OK):                  │
│    {                                          │
│      "status": "success",                     │
│      "project_id": 1,                         │
│      "title": "Comprehensive Analysis...",    │
│      "preview": "first 500 chars...",         │
│      "citations_count": 5,                    │
│      "word_count": 2847                       │
│    }                                          │
│                                                │
└────────────────────────────────────────────────┘
    │
    ↓
(Alternative: Could be made async via Celery)
(Current: Synchronous, returns immediately)


FRONTEND - RESPONSE:
───────────────────

receive ← Response: {status: "success", ...}
    │
    ├─ Check response.status
    │
    ├─→ "success"
    │   │
    │   ├─ showToast("Assignment generated!")
    │   │
    │   └─ Update UI:
    │       • Set currentProject.has_assignment = true
    │       • Render preview
    │       • Enable "Generate Presentation" button
    │
    └─→ Error
        │
        └─ showToast("Error: " + error.message)


GENERATED CONTENT STRUCTURE:
────────────────────────────

Assignment.content (markdown):
│
├─ # Comprehensive Analysis: {topic}
│
├─ ## Executive Summary
│  └─ Overview of research synthesis
│
├─ ## 1. Introduction
│  └─ Context and importance
│
├─ ## 2. Literature Review
│  ├─ For each paper in project:
│  │  ├─ 1. Paper Title (Authors, Year)
│  │  └─ Brief abstract excerpt
│  └─ Analysis of themes
│
├─ ## 3. Methodology Synthesis
│  └─ Summary of methodologies used in papers
│
├─ ## 4. Key Findings
│  ├─ Finding 1
│  ├─ Finding 2
│  └─ Finding 3
│
├─ ## 5. Critical Analysis
│  ├─ Strengths of research
│  ├─ Limitations identified
│  └─ Research gaps
│
├─ ## 6. Implications and Recommendations
│  └─ Practical applications
│
├─ ## 7. Future Directions
│  └─ Emerging areas and possibilities
│
├─ ## 8. Conclusion
│  └─ Summary of key takeaways
│
└─ ## References
   └─ All papers in APA format
```

---

## 4. Export (PDF/PPTX) Async Flow with Celery

```
┌──────────────────────────────────────────────────────────────┐
│        EXPORT TO PDF - ASYNC JOB FLOW                        │
└──────────────────────────────────────────────────────────────┘

FRONTEND:
─────────
User clicks "Export as PDF"
    │
    ↓
JavaScript: exportProjectPDF()
    │
    ├─ Validate: currentProject.has_assignment
    │
    ↓
api.exportToPDF(projectId, assignmentId)
    │
    ↓
POST /export/pdf
    │
    ├─ Headers: Authorization: Bearer {token}
    └─ Body: {project_id: 1, assignment_id: 1}


BACKEND - RECEIVES REQUEST:
──────────────────────────

POST /export/pdf Handler (routes/export.py)
    │
    ├─ Verify authentication & project ownership
    │
    ├─ Validate assignment exists
    │
    ├─ Queue Celery task: export_assignment_pdf.delay(pid, aid)
    │       │
    │       └─→ Task added to Redis queue
    │
    ├─ IMMEDIATELY return:
    │  {
    │    "status": "queued",
    │    "job_id": "abc-123-def-456",
    │    "message": "PDF export job queued successfully",
    │    "poll_url": "/api/v1/jobs/abc-123-def-456"
    │  }
    │
    └─ (Does NOT wait for export to finish)


FRONTEND - RECEIVES RESPONSE:
──────────────────────────────

showToast("PDF export started!")
    │
    ├─ Save jobId = "abc-123-def-456"
    │
    ├─ Setup polling interval:
    │  pollingInterval = setInterval(() => {
    │    api.getJobStatus(jobId)
    │  }, 2000)  // Poll every 2 seconds
    │
    └─ Show loading indicator


CELERY WORKER - PROCESSES TASK (Background):
──────────────────────────────────────────────

Redis Queue
    │
    └─→ Celery Worker picks up task
           │
           ↓
        Task: export_assignment_pdf(project_id=1, assignment_id=1)
           │
           (tasks/export_tasks.py)
           │
           ├─ Create DB session
           │
           ├─ Query Assignment from DB
           │
           ├─ Generate PDF content
           │  (Currently: Mock path generation)
           │  (Future: ReportLab PDF creation)
           │
           ├─ Create file: /generated/assignment_1_1.pdf
           │
           ├─ Create Export record in database:
           │  Export(
           │    project_id=1,
           │    file_type="pdf",
           │    file_path="/generated/assignment_1_1.pdf",
           │    file_url="http://localhost:8000/...",
           │    created_at=now()
           │  )
           │
           ├─ db.commit()
           │
           └─ Return {
                "status": "completed",
                "project_id": 1,
                "file_type": "pdf",
                "file_path": "/generated/assignment_1_1.pdf"
              }


REDIS RESULT STORAGE:
────────────────────

Task State Transitions in Redis:
    │
    ├─ First: PENDING (added to queue, not started)
    │
    ├─ Then: PROGRESS (worker executing)
    │
    ├─ Finally: SUCCESS (deleted after 1 hour) or FAILURE
    │
    └─ Result stored in Redis for 1 hour


FRONTEND - POLLING:
───────────────────

Interval function (every 2s):
    │
    ├─→ GET /jobs/abc-123-def-456
    │
    ├─ Backend queries Redis for job status
    │
    ├─ Response depends on status:
    │
    ├─→ If PENDING:
    │   {
    │     "status": "pending",
    │     "message": "Task is waiting to be executed"
    │   }
    │   → UI: Show "Waiting..."
    │
    ├─→ If PROGRESS:
    │   {
    │     "status": "processing",
    │     "progress": 50,
    │     "total": 100
    │   }
    │   → UI: Show progress bar (50%)
    │
    ├─→ If SUCCESS:
    │   {
    │     "status": "completed",
    │     "result": {
    │       "file_path": "/generated/...",
    │       "file_url": "http://..."
    │     }
    │   }
    │   → UI: Show "Complete!", disable loading
    │   → clearInterval(pollingInterval)
    │   → Reload project detail (shows export in list)
    │   → Show download button
    │
    └─→ If FAILURE:
        {
          "status": "failed",
          "error": "Error message"
        }
        → UI: Show error message
        → clearInterval(pollingInterval)


DOWNLOAD:
─────────

User clicks download link
    │
    ├─ File served from: file_url
    │  OR queried from: GET /export/{project_id}/downloads
    │
    └─ Browser downloads PDF file

```

---

## 5. Data Flow: API Request -> Database -> Response

```
┌────────────────────────────────────────────────────────────────┐
│         SINGLE REQUEST LIFECYCLE (Search Papers)               │
└────────────────────────────────────────────────────────────────┘

CLIENT (Frontend/JavaScript):
───────────────────────────

1. User enters search term: "Machine Learning"
2. User enters project ID: 1

             ↓

3. JavaScript calls:
   api.searchResearchPapers(topic, projectId)

             ↓

4. Internal: APIService.request('/research/search', {
     method: 'POST',
     body: JSON.stringify({
       topic: "Machine Learning",
       project_id: 1
     }),
     headers: {
       'Authorization': 'Bearer {token}',
       'Content-Type': 'application/json'
     }
   })

             ↓

5. fetch() sends HTTP request


NETWORK:
────────

POST http://localhost:8000/api/v1/research/search
Headers:
  - Authorization: Bearer eyJhbGc...
  - Content-Type: application/json
Body:
  - {"topic": "Machine Learning", "project_id": 1}

             ↓


SERVER (FastAPI Backend):
─────────────────────────

1. FastAPI routing: Match to POST /research/search
   (routes/research.py: @router.post("/search"))

             ↓

2. Request parsing & validation:
   - Parse JSON body → SearchQuery schema
   - topic = "Machine Learning"
   - project_id = 1
   - Pydantic validates fields

             ↓

3. Dependency injection (if needed):
   db: Session = Depends(get_db)
   current_user: User = Depends(get_current_user)
   
   (For this endpoint: no auth needed, no db needed)

             ↓

4. Handler function executes:
   async def search_papers(query: SearchQuery):

             ↓

5. Business logic:
   a) If project_id provided:
      - db.query(Project).filter(id=project_id)
      - Check: Is project in database?
   
   b) Generate mock papers:
      mock_papers = [
        {paper_id, title, abstract, authors, year, url},
        {paper_id, title, abstract, authors, year, url},
        {paper_id, title, abstract, authors, year, url}
      ]
      
      (NOTE: Currently mock data)
      (TODO: Integrate Semantic Scholar/arXiv API)
   
   c) If project_id provided, add papers to project:
      for paper in mock_papers:
        new_paper = Paper(...)
        db.add(new_paper)
      db.commit()

             ↓

6. Return response:
   return mock_papers
   
   (FastAPI auto-converts to JSON)


DATABASE:
─────────

If project_id was provided:

Transaction:
  1. INSERT INTO papers (...) VALUES (...)  [Paper 1]
  2. INSERT INTO papers (...) VALUES (...)  [Paper 2]
  3. INSERT INTO papers (...) VALUES (...)  [Paper 3]
  COMMIT

Tables updated:
  - papers table: 3 new rows inserted
  - Each row has: project_id=1, paper_id, title, authors, etc.


RESPONSE (FastAPI):
───────────────────

HTTP 200 OK

Headers:
  - Content-Type: application/json

Body:
[
  {
    "paper_id": "arxiv:1234.5678",
    "title": "Recent Advances in Machine Learning",
    "abstract": "This paper discusses...",
    "authors": ["John Doe", "Jane Smith"],
    "year": 2024,
    "url": "https://arxiv.org/abs/1234.5678"
  },
  {
    "paper_id": "semantic:987654321",
    "title": "A Comprehensive Review of Machine Learning",
    "abstract": "We present a thorough...",
    "authors": ["Alice Johnson"],
    "year": 2023,
    "url": "https://semantic-scholar.org/987654321"
  },
  {
    "paper_id": "arxiv:2024.1111",
    "title": "Emerging Trends in Machine Learning",
    "abstract": "This research explores...",
    "authors": ["Bob Smith", "Carol Davis"],
    "year": 2024,
    "url": "https://arxiv.org/abs/2024.1111"
  }
]

             ↓

NETWORK:
────────

(HTTP response travels back)

             ↓

CLIENT (Frontend):
──────────────────

1. fetch() response received
2. .json() parsed → JavaScript array
3. researchPapers = array
4. render papers in UI:
   - For each paper:
     - Show checkbox
     - Show title, authors, year
     - Show abstract excerpt
     - Show "View" link
5. User can now:
   - Check papers
   - Click "Add Papers" button

```

---

## 6. Database Relationships Visual

```
┌─────────────────────────────────────────────────────────────┐
│           DATABASE ENTITY RELATIONSHIPS                     │
└─────────────────────────────────────────────────────────────┘

USER (1)
│
├─ id: 1              (Primary Key)
├─ email: john@ex...  (Unique)
├─ name: John Doe
├─ password_hash: ...
├─ plan: free
└─ created_at: 2024-01-15

    │
    │ 1:N Relationship
    ↓

PROJECT (1:N relation to User)
├─ id: 1              (Primary Key)
├─ user_id: 1         (Foreign Key → User.id)
├─ title: AI Ethics
├─ topic: Ethical considerations...
├─ status: in_progress
├─ created_at: 2024-01-15
└─ updated_at: 2024-01-15

    │
    ├─ 1:N ──→ PAPER (1:N relation to Project)
    │         ├─ id: 1 (PK)
    │         ├─ project_id: 1 (FK)
    │         ├─ paper_id: arxiv:123
    │         ├─ title: Recent Advances...
    │         ├─ abstract: ...
    │         ├─ authors: John, Jane
    │         ├─ year: 2024
    │         └─ url: https://...
    │
    │         ├─ id: 2 (PK)
    │         ├─ project_id: 1 (FK)
    │         ├─ paper_id: semantic:456
    │         └─ ...
    │
    │         └─ id: 3
    │            project_id: 1
    │            ... (more papers)
    │
    │
    ├─ 1:1 ──→ SUMMARY (1:1 relation to Project)
    │         ├─ id: 1 (PK)
    │         ├─ project_id: 1 (FK, UNIQUE)
    │         ├─ content: Synthesized summary...
    │         └─ created_at: 2024-01-15
    │
    │
    ├─ 1:1 ──→ ASSIGNMENT (1:1 relation to Project)
    │         ├─ id: 1 (PK)
    │         ├─ project_id: 1 (FK, UNIQUE)
    │         ├─ title: Comprehensive Analysis...
    │         ├─ content: # Full markdown...
    │         ├─ citations: JSON {papers: [...]}
    │         └─ created_at: 2024-01-15
    │
    │
    ├─ 1:1 ──→ PRESENTATION (1:1 relation to Project)
    │         ├─ id: 1 (PK)
    │         ├─ project_id: 1 (FK, UNIQUE)
    │         ├─ slides_json: [{slide_number: 1, ...}]
    │         └─ created_at: 2024-01-15
    │
    │
    └─ 1:N ──→ EXPORT (1:N relation to Project)
              ├─ id: 1 (PK)
              ├─ project_id: 1 (FK)
              ├─ file_type: pdf
              ├─ file_path: /generated/assign_1_1.pdf
              ├─ file_url: http://localhost:8000/...
              └─ created_at: 2024-01-15

              ├─ id: 2
              ├─ project_id: 1
              ├─ file_type: pptx
              ├─ file_path: /generated/pres_1_1.pptx
              └─ ...

              └─ id: 3
                 project_id: 1
                 ... (more exports)
```

---

## 7. Component Integration Map

```
┌────────────────────────────────────────────────────────────────┐
│         ALL SYSTEM COMPONENTS & INTEGRATION POINTS             │
└────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                      FRONTEND                               │
│    (Vanilla JavaScript, HTML, CSS)                          │
│                                                             │
│  index.html ──→ app.js ──→ api.js                          │
│    (UI)         (Logic)     (HTTP)                         │
│                                                             │
│  State:                                                    │
│  - currentUser, projects, currentProject                  │
│  - researchPapers, selectedPapers, jobPolling            │
│                                                             │
│  Components:                                               │
│  - Auth screens (login/register)                          │
│  - Dashboard with stats                                    │
│  - Projects list/detail                                    │
│  - Research modal                                          │
│  - Export modal                                            │
└─────────────────────────────────────────────────────────────┘
         │
         │ HTTP/Fetch
         │ JSON payload
         │
         ↓
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                           │
│                  (main.py entry point)                      │
│                                                             │
│  ├─ CORS Middleware (allow all origins)                    │
│  ├─ Static files: /assets, /static                         │
│  └─ Routes:                                                │
│     ├─ /api/v1/auth (auth.py)                             │
│     ├─ /api/v1/users (auth.py)                            │
│     ├─ /api/v1/projects (projects.py)                     │
│     ├─ /api/v1/research (research.py)                     │
│     ├─ /api/v1/generate (generate.py)                     │
│     ├─ /api/v1/export (export.py)                         │
│     └─ /api/v1/jobs (jobs.py)                             │
│                                                             │
│  Utilities:                                                │
│  - auth_utils.py (JWT, hashing)                           │
│  - database.py (SQLAlchemy setup)                         │
│  - models.py (ORM definitions)                            │
└─────────────────────────────────────────────────────────────┘
         │
         ├─ DB Query/Insert
         │
         ├─ Queue task
         │
         └─ Check Redis
         
         ↓        ↓        ↓
         
    ┌────────────────────────────────────────────┬──────────────────┐
    │                                            │                  │
    ↓                                            ↓                  ↓
┌────────────────────────┐            ┌────────────────────┐   ┌─────────┐
│    SQLite Database     │            │  Celery + Redis    │   │ Storage │
│                        │            │                    │   │ (Local) │
│ Tables:                │            │ Queue:             │   │         │
│ - users                │            │ - export_pdf       │   │ /gener- │
│ - projects             │            │ - export_pptx      │   │ ated/   │
│ - papers               │            │ - generate_assign  │   │ ├─ PDF  │
│ - assignments          │            │ - generate_pres    │   │ └─ PPTX │
│ - presentations        │            │                    │   │         │
│ - exports              │            │ Workers:           │   │ (Future:│
│ - summaries            │            │ - Task executors   │   │  S3)    │
│                        │            │                    │   │         │
│ (studentlabs.db)       │            │ Result backend:    │   │         │
│                        │            │ - Job status       │   │         │
│                        │            │ - Result storage   │   │         │
└────────────────────────┘            │ (1 hour TTL)       │   └─────────┘
                                      │                    │
                                      │ Connection:        │
                                      │ redis://localhost: │
                                      │ 6379/0             │
                                      └────────────────────┘


TASK DEFINITIONS:
─────────────────

tasks/
├─ generation_tasks.py
│  ├─ generate_assignment_async(project_id)
│  ├─ generate_presentation_async(project_id)
│  └─ check_pending_tasks()  [Beat schedule]
│
└─ export_tasks.py
   ├─ export_assignment_pdf(project_id, assignment_id)
   └─ export_presentation_pptx(project_id, presentation_id)


EXTERNAL INTEGRATIONS (Planned):
────────────────────────────────

- Semantic Scholar API (paper search)
- arXiv API (paper search)
- CrossRef API (citations)
- OpenAI API (AI content generation)
- AWS S3 (file storage)
```

---

## 8. Request Response Cycle Example: Generate Assignment

```
┌────────────────────────────────────────────────────────────────┐
│          COMPLETE REQUEST/RESPONSE CYCLE                       │
│          USER CLICKS "GENERATE ASSIGNMENT"                     │
└────────────────────────────────────────────────────────────────┘

STEP 1: FRONTEND - USER ACTION
────────────────────────────────
Time: T+0ms

User clicks: "Generate Assignment"
    ↓
JavaScript: generateAssignment()
    ├─ Validate: currentProject exists
    ├─ Check: currentProject.papers_count > 0
    └─ Call: api.generateAssignment(projectId)


STEP 2: FRONTEND - API CALL
────────────────────────────
Time: T+10ms

APIService.generateAssignment(projectId=1)
    ├─ token = localStorage.getItem('auth_token')
    ├─ Construct URL: /api/v1/generate/1/assignment
    ├─ Method: POST
    ├─ Headers:
    │  ├ Authorization: Bearer {token}
    │  └ Content-Type: application/json
    ├─ Body: {"paper_ids": null}  [use all papers]
    └─ fetch(url, options)


STEP 3: NETWORK - REQUEST TRANSMISSION
───────────────────────────────────────
Time: T+15ms

POST http://localhost:8000/api/v1/generate/1/assignment HTTP/1.1
Host: localhost:8000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{"paper_ids": null}


STEP 4: BACKEND - REQUEST RECEIVED & ROUTED
─────────────────────────────────────────────
Time: T+25ms

FastAPI receives request
    ├─ Routing: Match to @router.post("/{project_id}/assignment")
    ├─ File: routes/generate.py, function: generate_assignment()
    └─ Parse request body: AssignmentRequest schema


STEP 5: BACKEND - DEPENDENCY INJECTION
────────────────────────────────────────
Time: T+30ms

Dependencies resolve:
    ├─ db: Session = Depends(get_db)
    │  └─ SessionLocal() → Database connection
    │
    └─ current_user: User = Depends(get_current_user)
       ├─ Extract Authorization header
       ├─ verify_access_token(token)
       │  ├─ jwt.decode(token, SECRET_KEY, HS256)
       │  ├─ Check exp timestamp
       │  └─ Extract user_id
       ├─ db.query(User).filter(User.id == token.sub)
       └─ Return User object (or raise 401)


STEP 6: BACKEND - BUSINESS LOGIC
─────────────────────────────────
Time: T+40ms

Handler: generate_assignment(1, AssignmentRequest, db, current_user)
    │
    ├─ VERIFY OWNERSHIP:
    │  db.query(Project).filter(
    │    Project.id == 1 AND
    │    Project.user_id == current_user.id
    │  )
    │  ├─ Found: Continue
    │  └─ Not found: raise HTTPException(404)
    │
    ├─ GET PAPERS:
    │  db.query(Paper).filter(Paper.project_id == 1)
    │  └─ Result: [Paper1{...}, Paper2{...}, Paper3{...}]
    │
    ├─ VALIDATE PAPERS:
    │  ├─ len(papers) > 0? Yes
    │  └─ No: raise HTTPException(400, "No papers found")
    │
    ├─ GENERATE CONTENT:
    │  ├─ title = f"Comprehensive Analysis: {project.topic}"
    │  │  → "Comprehensive Analysis: AI Ethics"
    │  │
    │  ├─ Build Literature Review:
    │  │  for i, paper in enumerate(papers, 1):
    │  │    literature_review += f"\n{i}. {paper.title}"
    │  │    literature_review += f"\n   - {paper.abstract[:150]}..."
    │  │
    │  ├─ Build full assignment_content:
    │  │  ├─ Add executive summary (template)
    │  │  ├─ Add introduction
    │  │  ├─ Insert literature_review
    │  │  ├─ Add methodology, findings, analysis
    │  │  ├─ Add recommendations
    │  │  ├─ Add conclusion
    │  │  ├─ Add references
    │  │  │  for paper in papers:
    │  │  │    citation = f"{authors} ({year}). {title}."
    │  │  │    assignment_content += "\n" + citation
    │  │  └─ Result: Full markdown (~2800 words)
    │  │
    │  └─ Build citations JSON:
    │     citations = {
    │       "papers": [
    │         {"id": p.paper_id, "title": p.title, ...},
    │         ...
    │       ],
    │       "count": 3
    │     }
    │
    ├─ SAVE TO DATABASE:
    │  ├─ Check if assignment exists:
    │  │  existing = db.query(Assignment).filter(
    │  │    Assignment.project_id == 1
    │  │  ).first()
    │  │
    │  ├─ If exists:
    │  │  existing.title = new_title
    │  │  existing.content = new_content
    │  │  existing.citations = citations
    │  │
    │  ├─ If not exists:
    │  │  new_assignment = Assignment(...)
    │  │  db.add(new_assignment)
    │  │
    │  └─ db.commit()
    │     → INSERT/UPDATE in database
    │
    └─ PREPARE RESPONSE:
       response = {
         "status": "success",
         "project_id": 1,
         "title": "Comprehensive Analysis: AI Ethics",
         "preview": assignment_content[:500] + "...",
         "citations_count": 3,
         "word_count": 2847,
         "message": "High-quality assignment generated successfully"
       }


STEP 7: BACKEND - DATABASE TRANSACTION
───────────────────────────────────────
Time: T+45ms

SQLite Database:
    ├─ UPDATE assignments
    │  SET title = 'Comprehensive Analysis...',
    │      content = '# Comprehensive Analysis...',
    │      citations = '{"papers": [...]}'
    │  WHERE project_id = 1
    │
    └─ COMMIT
       → Persistent storage


STEP 8: BACKEND - RESPONSE CONSTRUCTION
────────────────────────────────────────
Time: T+50ms

FastAPI converts Python dict to JSON:
    ├─ JSON serialization
    ├─ datetime objects → ISO format
    └─ Nested objects → JSON structure


STEP 9: NETWORK - RESPONSE TRANSMISSION
────────────────────────────────────────
Time: T+55ms

HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 543

{
  "status": "success",
  "project_id": 1,
  "title": "Comprehensive Analysis: AI Ethics",
  "preview": "# Comprehensive Analysis...",
  "citations_count": 3,
  "word_count": 2847,
  "message": "High-quality assignment generated successfully"
}


STEP 10: FRONTEND - RESPONSE RECEIVED
──────────────────────────────────────
Time: T+60ms

fetch().then(response => response.json())
    ├─ Parse JSON
    └─ Receive object


STEP 11: FRONTEND - RESPONSE HANDLING
─────────────────────────────────────
Time: T+65ms

generateAssignment() continues:
    ├─ showLoading(false)
    │  └─ Hide spinner
    │
    ├─ if response.status == "success":
    │  │
    │  ├─ showToast("Assignment generation successful!", "success")
    │  │  └─ Display green toast notification
    │  │
    │  ├─ currentProject.has_assignment = true
    │  │  └─ Update state
    │  │
    │  ├─ setTimeout(() => loadProjectDetail(), 2000)
    │  │  └─ Reload project in 2 seconds
    │  │
    │  └─ renderProjectDetail()
    │     ├─ Update status: "✓ Assignment Ready"
    │     ├─ Enable "Generate Presentation" button
    │     └─ Update UI
    │
    └─ else:
       ├─ showToast(`Error: ${error.message}`, "error")
       └─ Display red error notification


STEP 12: FRONTEND - UI UPDATE
──────────────────────────────
Time: T+70ms

Screen updates:
    ├─ Toast disappears after 4 seconds
    ├─ "Generate Assignment" button greyed out (done)
    ├─ "Generate Presentation" button enabled
    ├─ Status indicator shows: "✓ Assignment Ready"
    └─ Project detail refreshed


TOTAL TIME: ~70ms
─────────────

Network latency: ~30ms (request + response)
Backend processing: ~25ms
Frontend updates: ~15ms
```

---

This completes the comprehensive system workflow diagrams and visualizations for StudentLabs.
