# StudentLabs - Complete System Architecture

## Project Overview

**Purpose**: StudentLabs is an AI-powered engine that transforms research topics into fully researched academic assignments and presentations by leveraging academic papers from sources like arXiv and Semantic Scholar.

**Key Workflow**: Topic → Search Papers → Generate Assignment → Generate Presentation → Export (PDF/PPTX)

---

## 1. TECHNOLOGY STACK

### Backend
- **Framework**: FastAPI (Python web framework)
- **Web Server**: Uvicorn (ASGI server)
- **Database**: SQLite (development) / PostgreSQL ready
- **ORM**: SQLAlchemy
- **Authentication**: JWT (python-jose, passlib with bcrypt)
- **Task Queue**: Celery (async job processing)
- **Message Broker**: Redis
- **Document Generation**: 
  - ReportLab (PDF generation)
  - python-pptx (PowerPoint generation)
- **API Integration**: httpx (HTTP client)
- **Optional**: OpenAI (for advanced AI features)

### Frontend
- **Framework**: Vanilla JavaScript (no framework)
- **Architecture**: MVC-style with state management
- **API Communication**: Fetch API with custom APIService class
- **Styling**: Custom CSS
- **Storage**: LocalStorage for authentication tokens

### Infrastructure
- **Database**: SQLite (`studentlabs.db`)
- **Cache/Message Broker**: Redis (localhost:6379)
- **API Port**: 8000
- **Static Files**: Frontend served from `/frontend` and `/static`

---

## 2. DATABASE SCHEMA

### Entity Relationship Diagram

```
User (1)
  ├── (1:N) Project
  │     ├── (1:N) Paper
  │     ├── (1:1) Summary
  │     ├── (1:1) Assignment
  │     ├── (1:1) Presentation
  │     └── (1:N) Export
```

### Database Models (SQLAlchemy)

#### **User** Table
| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| `id` | Integer | PK, AutoIncrement | Unique user identifier |
| `email` | String | Unique, Indexed | User email (login credential) |
| `name` | String | - | User display name |
| `password_hash` | String | - | Bcrypt hashed password |
| `plan` | String | Default: "free" | Subscription tier (free, pro, enterprise) |
| `created_at` | DateTime | Default: now() | Account creation timestamp |

**File**: [backend/models.py](backend/models.py#L1)

#### **Project** Table
| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| `id` | Integer | PK, AutoIncrement | Project identifier |
| `user_id` | Integer | FK (users.id), Indexed | Owner of project |
| `title` | String | Indexed | Project name |
| `topic` | String | - | Research topic |
| `status` | String | Default: "draft" | draft, in_progress, completed |
| `created_at` | DateTime | Default: now() | Creation timestamp |
| `updated_at` | DateTime | Default & Update: now() | Last modification timestamp |

**Relationships**: 
- One User → Many Projects
- One Project → Many Papers, One Summary, One Assignment, One Presentation, Many Exports

#### **Paper** Table
| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| `id` | Integer | PK, AutoIncrement | Paper identifier |
| `project_id` | Integer | FK (projects.id), Indexed | Associated project |
| `paper_id` | String | - | External ID (arXiv, Semantic Scholar) |
| `title` | String | - | Paper title |
| `abstract` | Text | - | Paper abstract |
| `authors` | String | - | Comma-separated authors |
| `year` | Integer | - | Publication year |
| `summary` | Text | Nullable | KLM summary (optional) |
| `url` | String | Nullable | Link to paper |
| `created_at` | DateTime | Default: now() | Addition timestamp |

#### **Summary** Table
| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| `id` | Integer | PK, AutoIncrement | Summary identifier |
| `project_id` | Integer | FK (projects.id), Unique | Associated project (1:1) |
| `content` | Text | - | Synthesized summary of all papers |
| `created_at` | DateTime | Default: now() | Creation timestamp |

#### **Assignment** Table
| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| `id` | Integer | PK, AutoIncrement | Assignment identifier |
| `project_id` | Integer | FK (projects.id), Unique | Associated project (1:1) |
| `title` | String | - | Assignment title |
| `content` | Text | - | Full assignment content (markdown) |
| `citations` | JSON | - | Formatted citations from papers |
| `created_at` | DateTime | Default: now() | Creation timestamp |

**Citations Structure**:
```json
{
  "papers": [
    {
      "id": "arxiv:1234.5678",
      "title": "Paper Title",
      "authors": "Author Names",
      "year": 2024,
      "citation": "Author Names (2024). Paper Title.",
      "url": "https://..."
    }
  ],
  "count": 3
}
```

#### **Presentation** Table
| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| `id` | Integer | PK, AutoIncrement | Presentation identifier |
| `project_id` | Integer | FK (projects.id), Unique | Associated project (1:1) |
| `slides_json` | JSON | - | Array of slide objects |
| `created_at` | DateTime | Default: now() | Creation timestamp |

**Slides Structure**:
```json
[
  {
    "slide_number": 1,
    "title": "Topic Name",
    "layout": "title",
    "content": "Introduction and Overview",
    "speaker_notes": "Welcome to this presentation..."
  }
]
```

#### **Export** Table
| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| `id` | Integer | PK, AutoIncrement | Export identifier |
| `project_id` | Integer | FK (projects.id), Indexed | Associated project |
| `file_type` | String | - | pdf, pptx |
| `file_path` | String | - | Local file system path |
| `file_url` | String | Nullable | S3 or CDN URL |
| `created_at` | DateTime | Default: now() | Export timestamp |

---

## 3. BACKEND FILE STRUCTURE

```
backend/
├── main.py                  # FastAPI app setup, CORS, routing
├── models.py               # SQLAlchemy ORM models (User, Project, Paper, etc.)
├── database.py             # Database connection, session management
├── auth_utils.py           # JWT token, password hashing utilities
├── celery_app.py           # Celery configuration, Redis connection
├── run.py                  # Application entry point
├── test_app.py             # Application tests
├── test_imports.py         # Import verification tests
├── requirements.txt        # Python dependencies
├── requirements_updated.txt # Updated dependency versions
│
├── routes/                 # API route handlers (routers)
│   ├── __init__.py
│   ├── auth.py             # /api/v1/auth/* endpoints
│   ├── projects.py         # /api/v1/projects/* endpoints
│   ├── research.py         # /api/v1/research/* endpoints
│   ├── generate.py         # /api/v1/generate/* endpoints
│   ├── export.py           # /api/v1/export/* endpoints
│   └── jobs.py             # /api/v1/jobs/* endpoints (job status tracking)
│
├── tasks/                  # Celery async task definitions
│   ├── __init__.py
│   ├── generation_tasks.py # Assignment/Presentation generation tasks
│   └── export_tasks.py     # PDF/PPTX export tasks
│
└── __pycache__/           # Python bytecode cache
```

---

## 4. API ENDPOINTS

### Base URL: `http://localhost:8000/api/v1`

### 4.1 Authentication Routes (`/api/v1/auth`, `/api/v1/users`)

#### `POST /auth/signup`
**Purpose**: Register a new user
**Authentication**: None
**Request Body**:
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "secure_password"
}
```
**Response**: `UserResponse` (201 Created)
```json
{
  "id": 1,
  "email": "john@example.com",
  "name": "John Doe",
  "plan": "free",
  "created_at": "2024-01-15T10:30:00"
}
```
**Validations**:
- Email format validation (must contain @)
- Password minimum 8 characters
- Email must be unique

**File**: [backend/routes/auth.py](backend/routes/auth.py)

#### `POST /auth/login`
**Purpose**: Authenticate user and return JWT token
**Authentication**: None
**Request Body**:
```json
{
  "email": "john@example.com",
  "password": "secure_password"
}
```
**Response**: `TokenResponse` (200 OK)
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "john@example.com",
    "name": "John Doe",
    "plan": "free"
  }
}
```
**Token Expiration**: 30 minutes (configurable in `auth_utils.py`)

#### `GET /users/me`
**Purpose**: Get current authenticated user profile
**Authentication**: Bearer token
**Request Headers**:
```
Authorization: Bearer <token>
```
**Response**: (200 OK)
```json
{
  "id": 1,
  "email": "john@example.com",
  "name": "John Doe",
  "plan": "free",
  "created_at": "2024-01-15T10:30:00",
  "projects_count": 5
}
```

**File**: [backend/routes/auth.py#L93](backend/routes/auth.py#L93)

---

### 4.2 Projects Routes (`/api/v1/projects`)

#### `POST /projects`
**Purpose**: Create a new project
**Authentication**: Bearer token
**Request Body**:
```json
{
  "title": "AI Ethics in Healthcare",
  "topic": "Ethical considerations of AI in medical applications"
}
```
**Response**: `ProjectResponse` (201 Created)
```json
{
  "id": 1,
  "title": "AI Ethics in Healthcare",
  "topic": "Ethical considerations...",
  "status": "draft",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

**File**: [backend/routes/projects.py#L24](backend/routes/projects.py)

#### `GET /projects`
**Purpose**: List all projects for current user
**Authentication**: Bearer token
**Response**: Array of `ProjectResponse[]` (200 OK)

#### `GET /projects/{project_id}`
**Purpose**: Get detailed project information
**Authentication**: Bearer token
**Response**: `ProjectDetailResponse` (200 OK)
```json
{
  "id": 1,
  "title": "AI Ethics in Healthcare",
  "topic": "Ethical considerations...",
  "status": "in_progress",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00",
  "papers_count": 5,
  "has_assignment": true,
  "has_presentation": false,
  "exports_count": 0
}
```

#### `PUT /projects/{project_id}`
**Purpose**: Update project details
**Authentication**: Bearer token
**Request Body** (all optional):
```json
{
  "title": "New Title",
  "topic": "New Topic",
  "status": "in_progress"
}
```
**Response**: `ProjectResponse` (200 OK)

#### `DELETE /projects/{project_id}`
**Purpose**: Delete a project (cascades to papers, assignments, presentations, exports)
**Authentication**: Bearer token
**Response**: (200 OK)
```json
{
  "message": "Project deleted successfully"
}
```

#### `GET /projects/{project_id}/papers`
**Purpose**: Get all papers in a project
**Authentication**: Bearer token
**Response**: Array of paper objects
```json
[
  {
    "id": 1,
    "paper_id": "arxiv:1234.5678",
    "title": "Paper Title",
    "authors": "Author 1, Author 2",
    "year": 2024,
    "url": "https://arxiv.org/abs/1234.5678"
  }
]
```

**File**: [backend/routes/projects.py](backend/routes/projects.py)

---

### 4.3 Research Routes (`/api/v1/research`)

#### `POST /research/search`
**Purpose**: Search for academic papers and optionally add to project
**Authentication**: None (can be used without auth)
**Request Body**:
```json
{
  "topic": "Machine Learning",
  "project_id": 1  // Optional
}
```
**Response**: Array of `SearchResult[]`
```json
[
  {
    "paper_id": "arxiv:1234.5678",
    "title": "Recent Advances in Machine Learning",
    "abstract": "This paper discusses core methodologies...",
    "authors": ["John Doe", "Jane Smith"],
    "year": 2024,
    "url": "https://arxiv.org/abs/1234.5678"
  }
]
```
**Notes**: 
- Returns 3 mock papers (placeholder for real API integration)
- If `project_id` is provided, papers are automatically added to the project
- Uses mock data; ready for Semantic Scholar/arXiv API integration

#### `POST /research/{project_id}/papers/add`
**Purpose**: Manually add papers to an existing project
**Authentication**: Bearer token
**Request Body**:
```json
[
  {
    "paper_id": "arxiv:1234.5678",
    "title": "Paper Title",
    "abstract": "Abstract text...",
    "authors": ["Author 1", "Author 2"],
    "year": 2024,
    "url": "https://arxiv.org/abs/1234.5678"
  }
]
```
**Response**: (200 OK)
```json
{
  "status": "success",
  "papers_added": 1,
  "papers": [...]
}
```

#### `POST /research/summarize`
**Purpose**: Get a summary of a specific paper
**Authentication**: None
**Request Body**:
```json
{
  "paper_id": "arxiv:1234.5678"
}
```
**Response**: (200 OK)
```json
{
  "paper_id": "arxiv:1234.5678",
  "summary": "The methodology involves a novel approach yielding 20% improvement..."
}
```
**Notes**: Mock implementation placeholder for advanced NLP summarization

**File**: [backend/routes/research.py](backend/routes/research.py)

---

### 4.4 Generation Routes (`/api/v1/generate`)

#### `POST /generate/{project_id}/assignment`
**Purpose**: Generate high-quality academic assignment from project papers
**Authentication**: Bearer token
**Request Body**:
```json
{
  "paper_ids": ["arxiv:1234.5678", "arxiv:9876.5432"]  // Optional, uses all if omitted
}
```
**Response**: (200 OK)
```json
{
  "status": "success",
  "project_id": 1,
  "title": "Comprehensive Analysis: AI Ethics in Healthcare",
  "preview": "# Comprehensive Analysis...",
  "citations_count": 5,
  "word_count": 2847,
  "message": "High-quality assignment generated successfully"
}
```
**Generated Content Structure**:
- Executive Summary
- Introduction
- Literature Review (paper analysis)
- Methodology Synthesis
- Key Findings
- Critical Analysis (Strengths & Limitations)
- Implications and Recommendations
- Future Directions
- References (formatted citations)

**Features**:
- Dynamic topic-based content generation
- Automatic citation formatting
- Integration of all selected paper abstracts
- Academic structure with proper sections

**File**: [backend/routes/generate.py#L34](backend/routes/generate.py)

#### `PUT /generate/{project_id}/assignment`
**Purpose**: Update or edit assignment content manually
**Authentication**: Bearer token
**Request Body**:
```json
{
  "title": "Updated Title",
  "content": "Updated markdown content...",
  "citations": { /* citation object */ }  // Optional
}
```
**Response**: (200 OK)
```json
{
  "status": "success",
  "message": "Assignment updated"
}
```

#### `POST /generate/{project_id}/ppt`
**Purpose**: Generate PowerPoint presentation from project data
**Authentication**: Bearer token
**Request Body**:
```json
{
  "assignment_id": 1  // Optional
}
```
**Response**: (200 OK)
```json
{
  "status": "success",
  "project_id": 1,
  "slides": [
    {
      "slide_number": 1,
      "title": "Topic Name",
      "layout": "title",
      "content": "Introduction and Overview",
      "speaker_notes": "Welcome to this presentation..."
    }
  ]
}
```
**Generated Slides**:
1. Title slide (topic)
2. Key Concepts
3. Literature Review (with paper count)
4. Key Findings
5. Conclusion & Future Directions

**File**: [backend/routes/generate.py#L131](backend/routes/generate.py)

**Note**: There's a bug in line 160 - uses `user_id` instead of `current_user.id`

#### `PUT /generate/{project_id}/ppt`
**Purpose**: Update presentation slides
**Authentication**: Bearer token
**Request Body**:
```json
{
  "slides": [
    {
      "title": "Slide Title",
      "content": "Slide content",
      "speaker_notes": "Notes for speaker"
    }
  ]
}
```
**Response**: (200 OK)

---

### 4.5 Export Routes (`/api/v1/export`)

#### `POST /export/pdf`
**Purpose**: Queue async PDF export of assignment (uses Celery)
**Authentication**: Bearer token
**Request Body**:
```json
{
  "project_id": 1,
  "assignment_id": 1
}
```
**Response**: (200 OK)
```json
{
  "status": "queued",
  "job_id": "a7f4e6c1-2b3d-4e5f-6a7b-8c9d0e1f2a3b",
  "message": "PDF export job queued successfully",
  "poll_url": "/api/v1/jobs/a7f4e6c1-2b3d-4e5f-6a7b-8c9d0e1f2a3b"
}
```
**Flow**:
1. Validates project and assignment ownership
2. Queues `export_assignment_pdf` Celery task
3. Returns immediately with job ID
4. Client polls `/jobs/{job_id}` for status

#### `POST /export/pptx`
**Purpose**: Queue async PowerPoint export (uses Celery)
**Authentication**: Bearer token
**Request Body**:
```json
{
  "project_id": 1,
  "presentation_id": 1
}
```
**Response**: Similar to PDF export

#### `GET /export/{project_id}/downloads`
**Purpose**: Get all exports for a project
**Authentication**: Bearer token
**Response**: (200 OK)
```json
{
  "project_id": 1,
  "exports_count": 2,
  "exports": [
    {
      "id": 1,
      "file_type": "pdf",
      "file_path": "/generated/assignment_1_1.pdf",
      "file_url": "http://localhost:8000/downloads/assignment_1_1.pdf",
      "created_at": "2024-01-15T10:30:00"
    }
  ]
}
```

**File**: [backend/routes/export.py](backend/routes/export.py)

---

### 4.6 Jobs Routes (`/api/v1/jobs`)

These endpoints track async Celery jobs for long-running operations.

#### `GET /jobs/{job_id}`
**Purpose**: Get status of a background job
**Authentication**: None
**Response**: (200 OK)

Different states returned based on task status:

**Pending**:
```json
{
  "job_id": "a7f4e6c1-2b3d-4e5f-6a7b-8c9d0e1f2a3b",
  "status": "pending",
  "message": "Task is waiting to be executed"
}
```

**Processing**:
```json
{
  "job_id": "a7f4e6c1-2b3d-4e5f-6a7b-8c9d0e1f2a3b",
  "status": "processing",
  "message": "Task is being processed",
  "progress": 50,
  "total": 100
}
```

**Completed**:
```json
{
  "job_id": "a7f4e6c1-2b3d-4e5f-6a7b-8c9d0e1f2a3b",
  "status": "completed",
  "message": "Task completed successfully",
  "result": { /* result data */ }
}
```

**Failed**:
```json
{
  "job_id": "a7f4e6c1-2b3d-4e5f-6a7b-8c9d0e1f2a3b",
  "status": "failed",
  "message": "Task failed",
  "error": "Error message description"
}
```

#### `GET /jobs/{job_id}/result`
**Purpose**: Get result of completed job
**Authentication**: None
**Response on Success**: (200 OK)
```json
{
  "job_id": "a7f4e6c1...",
  "status": "completed",
  "result": { /* task result */ }
}
```
**Response if Still Processing**: (202 Accepted)
**Response if Failed**: (400 Bad Request)

#### `DELETE /jobs/{job_id}`
**Purpose**: Cancel a queued or running job
**Authentication**: None
**Response**: (200 OK)
```json
{
  "job_id": "a7f4e6c1...",
  "status": "cancelled",
  "message": "Job cancelled successfully"
}
```

**File**: [backend/routes/jobs.py](backend/routes/jobs.py)

---

## 5. FRONTEND FILE STRUCTURE

```
frontend/
├── index.html       # Main dashboard HTML (structure and modals)
├── app.js           # Main application logic and event handlers
├── api.js           # API service layer (centralized HTTP calls)
├── app-old.js       # Previous version (backup)
├── styles.css       # All styling (responsive design)
└── (deployed to /static mount point in FastAPI)
```

---

## 6. FRONTEND ARCHITECTURE

### 6.1 Global State Management

Located in [frontend/app.js](frontend/app.js) - top-level variables:

```javascript
let currentUser = null;              // { id, email, name, plan, created_at }
let projects = [];                   // Array of Project objects
let currentProject = null;           // Currently viewed Project
let currentAssignment = null;        // Assignment for current project
let currentPresentation = null;      // Presentation for current project
let researchPapers = [];            // Search results from research API
let selectedPapers = [];            // Indices of checked papers
let jobPolling = {};                // Active polling jobs: { jobId: intervalId }
```

### 6.2 APIService Class

**File**: [frontend/api.js](frontend/api.js)

**Purpose**: Centralized HTTP client with token management

**Key Methods**:
- `request(endpoint, options)` - Base method, handles auth headers and errors
- `register(name, email, password)` - User signup
- `login(email, password)` - User authentication
- `logout()` - Clear token
- `getCurrentUser()` - Fetch user profile
- `getProjects()` - List user projects
- `getProject(projectId)` - Get single project
- `createProject(title, topic)` - Create new project
- `deleteProject(projectId)` - Delete project
- `getProjectPapers(projectId)` - Get papers in project
- `searchResearchPapers(topic, projectId)` - Search papers
- `addPapersToProject(projectId, papers)` - Add papers to project
- `generateAssignment(projectId, paperIds)` - Generate assignment
- `generatePresentation(projectId, assignmentId)` - Generate presentation
- `exportToPDF(projectId, assignmentId)` - Queue PDF export
- `exportToPPTX(projectId, presentationId)` - Queue PPTX export
- `getJobStatus(jobId)` - Poll job status

**Token Storage**: LocalStorage key `auth_token`

### 6.3 Screens & Pages

#### Authentication Screens
- **Login**: Email/password form
- **Register**: Name/email/password form with validation
- Toggle between screens with `switchAuth(screen)`

#### Dashboard Pages (after login)
1. **Dashboard** - Overview with stats and recent projects
2. **Projects** - List all projects with CRUD operations
3. **Project Detail** - Workflow view (research → assignment → presentation → export)
4. **Research** - Paper search (integrated in project detail)
5. **Generate** - Content generation (integrated in project detail)
6. **Export** - Download options (integrated in project detail)

### 6.4 Key Components

#### Workflow Steps (in Project Detail)
```
Research Step (🔍)
  ├── Search for papers
  ├── Display results
  ├── Select and add papers
  └── Show count: "X papers added"

Assignment Step (📝)
  ├── Generate assignment from papers
  ├── Display preview
  └── Show status: "Ready" or "Not started"

Presentation Step (🎨)
  ├── Generate slides from assignment
  ├── Edit slides
  └── Show status: "Ready" or "Not started"

Export Step (📥)
  ├── Export to PDF
  ├── Export to PowerPoint
  └── Show count: "X exports"
```

### 6.5 Modals

1. **Project Modal** - Create new project
2. **Research Modal** - Search and add papers
3. **Export Modal** - Choose export type

### 6.6 UI Utilities

**Loading Indicator**: `showLoading(boolean)` - Shows/hides spinner
**Toast Notifications**: `showToast(message, type)` - Types: info, success, error
**Sidebar Toggle**: `toggleSidebar()` - Mobile responsive menu
**Page Navigation**: `showPage(pageName)` - Switch pages

---

## 7. AUTHENTICATION SYSTEM

### 7.1 Technology Stack
- **Token Type**: JWT (JSON Web Token)
- **Algorithm**: HS256 (HMAC with SHA-256)
- **Secret Key**: Environment variable `SECRET_KEY` (dev default: "your-secret-key-change-in-production")
- **Password Hashing**: bcrypt via passlib

### 7.2 Token Structure

**JWT Payload**:
```json
{
  "sub": 1,                              // User ID
  "email": "john@example.com",           // User email
  "exp": 1705318200                      // Expiration timestamp (30 min from login)
}
```

### 7.3 Auth Flow

1. **Registration**:
   ```
   POST /auth/signup
   → Hash password with bcrypt
   → Store user in database
   → Respond with UserResponse
   ```

2. **Login**:
   ```
   POST /auth/login
   → Lookup user by email
   → Verify password against hash
   → Generate JWT token (30 min expiry)
   → Return token + user info
   ```

3. **API Requests**:
   ```
   Include: Authorization: Bearer <token>
   → Middleware extracts token
   → Verify JWT signature and expiration
   → On success: Attach user to request context
   → On failure: Return 401 Unauthorized
   ```

4. **Token Refresh**:
   - Currently NOT implemented
   - Users need to re-login after 30 minutes

### 7.4 Helper Functions

**File**: [backend/auth_utils.py](backend/auth_utils.py)

```python
hash_password(password: str) -> str
  → Bcrypt hash; returns hashed string

verify_password(plain_password: str, hashed_password: str) -> bool
  → Compare plain password against hash

create_access_token(data: dict, expires_delta: Optional[timedelta]) -> str
  → Create signed JWT token

verify_access_token(token: str) -> Optional[TokenData]
  → Verify and decode JWT; return TokenData(user_id, email)

extract_token_from_header(authorization: Optional[str]) -> Optional[str]
  → Parse "Bearer <token>" from header
```

### 7.5 Dependency Injection

**File**: [backend/routes/auth.py#L38](backend/routes/auth.py)

```python
def get_current_user(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
) -> User:
    # Used as: Depends(get_current_user) in route signatures
    # Returns authenticated User object or raises 401
```

---

## 8. ASYNC JOB HANDLING (CELERY)

### 8.1 Architecture

**File**: [backend/celery_app.py](backend/celery_app.py)

**Components**:
- **Broker**: Redis (localhost:6379/0) - Message queue
- **Backend**: Redis (localhost:6379/0) - Result storage
- **Workers**: Execute tasks from queue

**Configuration**:
- Task serializer: JSON
- Result expiration: 1 hour
- Soft time limit: 25 minutes
- Hard time limit: 30 minutes
- Max retries: 3 (for specific tasks)

### 8.2 Task Definitions

#### Generation Tasks

**File**: [backend/tasks/generation_tasks.py](backend/tasks/generation_tasks.py)

**Task 1: `generate_assignment_async(project_id)`**
- **Trigger**: User clicks "Generate Assignment"
- **Process**:
  1. Query project and papers from database
  2. Create assignment with formatted content
  3. Build citations JSON from papers
  4. Save or update Assignment record
  5. Return success response
- **Retries**: 3 (60-second delay between attempts)
- **Return Value**:
  ```json
  {
    "status": "completed",
    "project_id": 1,
    "title": "Comprehensive Analysis: ...",
    "word_count": 2847,
    "citations_count": 5
  }
  ```

**Task 2: `generate_presentation_async(project_id)`**
- **Trigger**: User clicks "Generate Slides"
- **Process**:
  1. Query project and papers
  2. Generate slide JSON array
  3. Save or update Presentation record
- **Retries**: 3
- **Return Value**:
  ```json
  {
    "status": "completed",
    "project_id": 1,
    "slides_count": 5
  }
  ```

**Task 3: `check_pending_tasks()`**
- **Trigger**: Periodic (every 5 minutes via Beat schedule)
- **Purpose**: Monitor and process pending tasks
- **Return Value**: Timestamp of last check

#### Export Tasks

**File**: [backend/tasks/export_tasks.py](backend/tasks/export_tasks.py)

**Task 1: `export_assignment_pdf(project_id, assignment_id)`**
- **Trigger**: User clicks "Export to PDF"
- **Process**:
  1. Query assignment from database
  2. Generate PDF file (ReportLab placeholder)
  3. Save Export record
  4. Optionally upload to S3
- **Retries**: 3
- **Return Value**:
  ```json
  {
    "status": "completed",
    "project_id": 1,
    "file_type": "pdf",
    "file_path": "/generated/assignment_1_1.pdf"
  }
  ```

**Task 2: `export_presentation_pptx(project_id, presentation_id)`**
- **Trigger**: User clicks "Export to PowerPoint"
- **Process**:
  1. Query presentation from database
  2. Generate PPTX file (python-pptx placeholder)
  3. Save Export record
  4. Optionally upload to S3
- **Retries**: 3
- **Return Value**: Similar to PDF export

### 8.3 Polling Pattern

**Frontend** (client-side):

1. User triggers action (export, generate)
2. API returns `{ job_id, status: "queued" }`
3. JavaScript sets polling interval:
   ```javascript
   pollInterval = setInterval(
     () => api.getJobStatus(jobId),
     2000  // Poll every 2 seconds
   )
   ```
4. When status = "completed", show result, clear interval

---

## 9. FILE GENERATION CAPABILITIES

### 9.1 PDF Export

**Library**: ReportLab (pure Python PDF generation)
**Status**: Placeholder implementation (mock file path generation)
**Location**: [backend/tasks/export_tasks.py#L6](backend/tasks/export_tasks.py)

**Flow**:
1. Query Assignment record
2. Create file path: `/generated/assignment_{project_id}_{assignment_id}.pdf`
3. Save Export record with file info
4. Return file location

**Future Enhancement**: Implement actual PDF generation with:
- Professional formatting
- Headers/footers with project info
- Pagination
- Embedded citations and links

### 9.2 PowerPoint Export

**Library**: python-pptx (PowerPoint file manipulation)
**Status**: Placeholder implementation
**Location**: [backend/tasks/export_tasks.py#L45](backend/tasks/export_tasks.py)

**Flow**:
1. Query Presentation record
2. Create file path: `/generated/presentation_{project_id}_{presentation_id}.pptx`
3. Save Export record
4. Return file location

**Future Enhancement**: Implement with:
- Slide templates and formatting
- Speaker notes insertion
- Image/chart integration
- Custom themes

### 9.3 Current Implementation Status

**PDF Generation**: Mock (file path only, no actual PDF created)
**PPTX Generation**: Mock (file path only, no actual PowerPoint created)

**Next Steps to Production**:
1. Implement ReportLab PDF generation (backend/tasks/export_tasks.py)
2. Implement python-pptx generation (backend/tasks/export_tasks.py)
3. Add file storage (local filesystem or S3)
4. Add download endpoint with proper MIME types

---

## 10. KEY FEATURES & WORKFLOWS

### 10.1 Complete User Journey

```
1. REGISTRATION & LOGIN
   User registers → Email verified → Receives JWT token

2. PROJECT CREATION
   User creates project → Name + Topic → Stored in database

3. RESEARCH PHASE
   User searches papers → Results from mock API → Select papers → Add to project

4. ASSIGNMENT GENERATION
   Celery task starts → Extract papers → Build rich content → Citations → DB save

5. PRESENTATION GENERATION
   Celery task starts → Create slide structure → JSON storage

6. EXPORT
   User exports → Celery task queues → File generation → Recorded in Export table

7. DOWNLOAD
   User polls job status → Retrieves download link
```

### 10.2 Feature Breakdown

| Feature | Status | Files |
|---------|--------|-------|
| User Auth (JWT) | Complete | auth.py, auth_utils.py |
| Project CRUD | Complete | projects.py |
| Paper Search | Mock Data | research.py |
| Assignment Gen | Complete (sync) | generate.py |
| Presentation Gen | Complete (sync) | generate.py |
| PDF Export | Mock | export_tasks.py |
| PPTX Export | Mock | export_tasks.py |
| Async Jobs | Complete | celery_app.py, jobs.py |
| Data Persistence | Complete | models.py, database.py |
| Frontend UI | Complete | app.js, api.js, styles.css |

---

## 11. COMPONENT RELATIONSHIPS & DATA FLOW

### 11.1 Request/Response Flow Example: Generate Assignment

```
FRONTEND                     BACKEND                    DATABASE
────────                     ───────                    ────────

User clicks
"Generate" ──────────────────→ POST /generate/{pid}/assignment
                              │
                              ├─ Verify project ownership
                              ├─ Query Project + Papers
                              │
                              └─────────→ Database
                                         Query: projects, papers
                                         ←─────── Data
                              │
                              ├─ Create Assignment object
                              ├─ Enqueue Celery task
                              │
                              └──→ Celery Worker
                                  (Redis queue)
                                  │
                                  ├─ Dequeue task
                                  ├─ Execute generation logic
                                  ├─ Save Assignment
                                  │
                                  └─────→ Database
                                          UPDATE: assignments table
                                          ←─────── Confirm
                              │
                         Return: {job_id, status}
←────────────────────────
Display loading...

Poll every 2s
──────────────────────→ GET /jobs/{job_id}
                        │
                        ├─ Check Celery task status
                        ├─ Redis lookup
                        │
                   Return: {status: "completed", result}
←────────────────────────
Show success + preview
```

### 11.2 Data Model Relationships

```
User (1)
  ├─ Project (1:N)
  │   ├─ Paper (1:N) - Many research papers
  │   ├─ Assignment (1:1) - One assignment per project
  │   │   └─ citations: JSON array of {id, title, authors, year, url}
  │   ├─ Presentation (1:1) - One presentation per project
  │   │   └─ slides_json: Array of slide objects
  │   └─ Export (1:N) - Multiple exports (PDF, PPTX, etc.)
```

### 11.3 API Integration Points

1. **Frontend ← → Backend API**
   - All URLs start with `/api/v1`
   - Authentication via Bearer token in header
   - JSON request/response format

2. **Backend ← → Database**
   - SQLAlchemy ORM mapping
   - Automatic session management via FastAPI `Depends()`

3. **Backend ← → Celery Queue**
   - Task registration via `@celery_app.task` decorator
   - Asynchronous method calls: `task.delay(args)`
   - Status retrieval via task ID

4. **Backend ← → Redis**
   - Message broker for Celery
   - Result backend for task states
   - Connection: `redis://localhost:6379/0`

---

## 12. ENVIRONMENT CONFIGURATION

### 12.1 Environment Variables

The system recognizes these environment variables (from code):

| Variable | Purpose | Default | File |
|----------|---------|---------|------|
| `SECRET_KEY` | JWT signing secret | "your-secret-key-change-in-production" | auth_utils.py |
| `REDIS_URL` | Celery broker/backend | "redis://localhost:6379/0" | celery_app.py |
| `DATABASE_URL` | SQLAlchemy connection | "sqlite:///./studentlabs.db" | database.py |

### 12.2 Running the Application

**Backend Start**:
```bash
cd backend
pip install -r requirements.txt
python run.py
# Server runs on http://localhost:8000
```

**Celery Worker Start**:
```bash
cd backend
celery -A celery_app worker --loglevel=info
```

**Celery Beat (Scheduler) Start**:
```bash
cd backend
celery -A celery_app beat --loglevel=info
```

**Redis Start**:
```bash
redis-server
# Or use: redis-cli to connect
```

---

## 13. KNOWN ISSUES & LIMITATIONS

### Bugs
1. **Line 160 in generate.py**: Uses undefined `user_id` instead of `current_user.id`
   - Location: [backend/routes/generate.py#L160](backend/routes/generate.py)
   - Affects: Presentation generation endpoint

### Limitations
1. **Research Papers**: Mock data only - not connected to real academic APIs
2. **PDF/PPTX Generation**: File paths only - actual content generation not implemented
3. **Token Refresh**: 30-minute token expiry with no refresh mechanism
4. **Database**: SQLite for development - not production-ready
5. **Concurrency**: No built-in rate limiting or quota management
6. **Error Handling**: Limited retry logic for failed exports
7. **Validation**: Minimal input validation (especially for assignment content)

### Scalability Considerations
- Redis connection pooling needed for production
- Database needs connection pooling for high concurrency
- Celery workers should be horizontally scaled
- Static file serving should use CDN
- PDF/PPTX generation will be I/O intensive at scale

---

## 14. QUICK REFERENCE

### Key File Purposes

| File | Purpose |
|------|---------|
| [main.py](backend/main.py) | FastAPI app setup, CORS, router mounting, static file serving |
| [models.py](backend/models.py) | Database schema definitions (User, Project, Paper, etc.) |
| [database.py](backend/database.py) | SQLAlchemy setup, session factory |
| [auth_utils.py](backend/auth_utils.py) | JWT and password utilities |
| [celery_app.py](backend/celery_app.py) | Celery configuration and Beat schedule |
| [routes/auth.py](backend/routes/auth.py) | Authentication endpoints (signup, login) |
| [routes/projects.py](backend/routes/projects.py) | Project CRUD operations |
| [routes/research.py](backend/routes/research.py) | Paper search and management |
| [routes/generate.py](backend/routes/generate.py) | Assignment and presentation generation |
| [routes/export.py](backend/routes/export.py) | PDF/PPTX export endpoints |
| [routes/jobs.py](backend/routes/jobs.py) | Async job status tracking |
| [tasks/generation_tasks.py](backend/tasks/generation_tasks.py) | Celery tasks for content generation |
| [tasks/export_tasks.py](backend/tasks/export_tasks.py) | Celery tasks for file export |
| [app.js](frontend/app.js) | Frontend application logic, event handlers |
| [api.js](frontend/api.js) | Centralized API service client |
| [index.html](frontend/index.html) | Dashboard HTML structure and modals |

---

## 15. DEPLOYMENT CHECKLIST

### Before Production
- [ ] Change `SECRET_KEY` in auth_utils.py
- [ ] Add `.env` file for secrets management
- [ ] Implement actual PDF generation (ReportLab)
- [ ] Implement actual PPTX generation (python-pptx)
- [ ] Migrate to PostgreSQL database
- [ ] Add token refresh mechanism
- [ ] Implement rate limiting
- [ ] Add comprehensive error logging
- [ ] Set up monitoring for Celery workers
- [ ] Configure CORS for actual frontend domain
- [ ] Add SSL/TLS certificates
- [ ] Set up automated backups
- [ ] Implement user quotas/limits
- [ ] Add payment integration (if needed)
- [ ] Security: SQL injection, CSRF, XSS prevention review

---

## 16. FUTURE ENHANCEMENTS

1. **Real Paper APIs**: Integrate Semantic Scholar, arXiv, CrossRef APIs
2. **AI-Powered Content**: OpenAI integration for smarter summaries and suggestions
3. **Collaborative Features**: Share projects, real-time collaboration
4. **Advanced Export**: Custom templates, styling options, multi-format
5. **Analytics**: Usage stats, content quality metrics, time tracking
6. **Mobile App**: React Native or Flutter app
7. **Browser Extension**: Quick paper capture from web
8. **Social Features**: Paper recommendations, community insights
9. **Premium Tiers**: Advanced AI features, storage, API access
10. **Audit Trail**: Track all changes to assignments and presentations

---

## Summary

**StudentLabs** is a comprehensive web application for automating academic research workflows. It combines a robust FastAPI backend with SQLAlchemy ORM, Redis/Celery for async processing, and a vanilla JavaScript frontend. The system enables users to search for academic papers, synthesize research into high-quality assignments, generate presentation slides, and export to PDF/PowerPoint formats. The architecture supports scalability through async task processing and is designed for easy integration with real academic APIs and AI services.
