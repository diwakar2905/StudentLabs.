# StudentLabs - Detailed API Reference

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication
All endpoints except `/auth/signup`, `/auth/login`, and `/research/search` require:
```
Header: Authorization: Bearer <jwt_token>
X: Content-Type: application/json
```

---

## 1. AUTHENTICATION API

### 1.1 POST /auth/signup - Register New User

**File**: [backend/routes/auth.py#L82](backend/routes/auth.py)

**Request**:
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "SecurePass123"
}
```

**Success Response** (201 Created):
```json
{
  "id": 1,
  "email": "john@example.com",
  "name": "John Doe",
  "plan": "free",
  "created_at": "2024-01-15T10:30:00"
}
```

**Error Responses**:
- 400 Bad Request - Email already exists
  ```json
  { "detail": "Email already registered" }
  ```
- 400 Bad Request - Invalid email format
  ```json
  { "detail": "Invalid email format" }
  ```
- 400 Bad Request - Weak password
  ```json
  { "detail": "Password must be at least 8 characters" }
  ```

**Validations**:
- Email: Must contain "@"
- Password: Minimum 8 characters
- Email: Must be unique in database

---

### 1.2 POST /auth/login - Authenticate User

**File**: [backend/routes/auth.py#L120](backend/routes/auth.py)

**Request**:
```json
{
  "email": "john@example.com",
  "password": "SecurePass123"
}
```

**Success Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsImVtYWlsIjoiam9obkBleGFtcGxlLmNvbSIsImV4cCI6MTcwNTMxODIwMH0.xyz123",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "john@example.com",
    "name": "John Doe",
    "plan": "free"
  }
}
```

**Error Responses**:
- 401 Unauthorized - Invalid credentials
  ```json
  { "detail": "Invalid email or password" }
  ```

**Token Details**:
- Type: JWT (JSON Web Token)
- Algorithm: HS256
- Expiration: 30 minutes from now
- Payload: `{ sub: user_id, email: user_email, exp: timestamp }`

---

### 1.3 GET /users/me - Get Current User Profile

**File**: [backend/routes/auth.py#L145](backend/routes/auth.py)

**Request**:
```
GET /users/me
Authorization: Bearer {token}
```

**Success Response** (200 OK):
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

**Error Responses**:
- 401 Unauthorized - Missing/invalid token
  ```json
  { "detail": "Invalid or expired token" }
  ```

---

## 2. PROJECTS API

### 2.1 POST /projects - Create Project

**File**: [backend/routes/projects.py#L24](backend/routes/projects.py)

**Request**:
```json
{
  "title": "AI Ethics in Healthcare",
  "topic": "Ethical considerations of AI in medical applications"
}
```

**Success Response** (201 Created):
```json
{
  "id": 1,
  "title": "AI Ethics in Healthcare",
  "topic": "Ethical considerations of AI in medical applications",
  "status": "draft",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

**Fields**:
- `title`: Project name (required)
- `topic`: Research topic (required)
- `status`: Defaults to "draft" (can be: draft, in_progress, completed)
- `user_id`: Automatically set to current user
- `created_at`, `updated_at`: Server-generated timestamps

---

### 2.2 GET /projects - List All Projects for User

**File**: [backend/routes/projects.py#L38](backend/routes/projects.py)

**Request**:
```
GET /projects
Authorization: Bearer {token}
```

**Success Response** (200 OK):
```json
[
  {
    "id": 1,
    "title": "AI Ethics in Healthcare",
    "topic": "Ethical considerations...",
    "status": "in_progress",
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:35:00"
  },
  {
    "id": 2,
    "title": "Machine Learning Basics",
    "topic": "Fundamentals of ML",
    "status": "draft",
    "created_at": "2024-01-14T14:20:00",
    "updated_at": "2024-01-14T14:20:00"
  }
]
```

**Note**: Returns only projects owned by current user

---

### 2.3 GET /projects/{project_id} - Get Project Details

**File**: [backend/routes/projects.py#L48](backend/routes/projects.py)

**Request**:
```
GET /projects/1
Authorization: Bearer {token}
```

**Success Response** (200 OK):
```json
{
  "id": 1,
  "title": "AI Ethics in Healthcare",
  "topic": "Ethical considerations...",
  "status": "in_progress",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:35:00",
  "papers_count": 5,
  "has_assignment": true,
  "has_presentation": false,
  "exports_count": 0
}
```

**Error Responses**:
- 404 Not Found - Project doesn't exist or user doesn't own it
  ```json
  { "detail": "Project not found" }
  ```

---

### 2.4 PUT /projects/{project_id} - Update Project

**File**: [backend/routes/projects.py#L65](backend/routes/projects.py)

**Request**:
```json
{
  "title": "Updated Title",
  "topic": "Updated topic description",
  "status": "in_progress"
}
```

**Note**: All fields optional - only sends fields to update

**Success Response** (200 OK):
```json
{
  "id": 1,
  "title": "Updated Title",
  "topic": "Updated topic description",
  "status": "in_progress",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:40:00"
}
```

---

### 2.5 DELETE /projects/{project_id} - Delete Project

**File**: [backend/routes/projects.py#L90](backend/routes/projects.py)

**Request**:
```
DELETE /projects/1
Authorization: Bearer {token}
```

**Success Response** (200 OK):
```json
{
  "message": "Project deleted successfully"
}
```

**Cascading Deletes**:
- All Project's Papers
- Project's Assignment (if exists)
- Project's Presentation (if exists)
- Project's Exports (if exists)
- Project's Summary (if exists)

---

### 2.6 GET /projects/{project_id}/papers - Get Papers in Project

**File**: [backend/routes/projects.py#L102](backend/routes/projects.py)

**Request**:
```
GET /projects/1/papers
Authorization: Bearer {token}
```

**Success Response** (200 OK):
```json
[
  {
    "id": 1,
    "paper_id": "arxiv:1234.5678",
    "title": "Recent Advances in Machine Learning",
    "authors": "John Doe, Jane Smith",
    "year": 2024,
    "url": "https://arxiv.org/abs/1234.5678"
  },
  {
    "id": 2,
    "paper_id": "semantic:987654321",
    "title": "A Comprehensive Review of AI",
    "authors": "Alice Johnson",
    "year": 2023,
    "url": "https://semantic-scholar.org/987654321"
  }
]
```

---

## 3. RESEARCH API

### 3.1 POST /research/search - Search for Academic Papers

**File**: [backend/routes/research.py#L35](backend/routes/research.py)

**Request**:
```json
{
  "topic": "Machine Learning",
  "project_id": 1
}
```

**Fields**:
- `topic`: Search query (required)
- `project_id`: Optional - if provided, papers are auto-added to project

**Success Response** (200 OK):
```json
[
  {
    "paper_id": "arxiv:1234.5678",
    "title": "Recent Advances in Machine Learning",
    "abstract": "This paper discusses core methodologies and significant findings related to the topic. We present novel approaches and evaluate them against existing baselines, achieving a 20% improvement in performance.",
    "authors": ["John Doe", "Jane Smith"],
    "year": 2024,
    "url": "https://arxiv.org/abs/1234.5678"
  },
  {
    "paper_id": "semantic:987654321",
    "title": "A Comprehensive Review of Machine Learning",
    "abstract": "We present a thorough literature review of the subject matter, highlighting the latest trends, methodologies, and applications in the field.",
    "authors": ["Alice Johnson"],
    "year": 2023,
    "url": "https://semantic-scholar.org/987654321"
  },
  {
    "paper_id": "arxiv:2024.1111",
    "title": "Emerging Trends in Machine Learning",
    "abstract": "This research explores emerging developments and future directions in the field, including new architectural paradigms and training methodologies.",
    "authors": ["Bob Smith", "Carol Davis"],
    "year": 2024,
    "url": "https://arxiv.org/abs/2024.1111"
  }
]
```

**Note**: Currently returns 3 mock papers. Ready for real API integration (Semantic Scholar, arXiv).

---

### 3.2 POST /research/{project_id}/papers/add - Add Papers to Project

**File**: [backend/routes/research.py#L84](backend/routes/research.py)

**Request**:
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

**Success Response** (200 OK):
```json
{
  "status": "success",
  "papers_added": 1,
  "papers": [
    {
      "paper_id": "arxiv:1234.5678",
      "title": "Recent Advances in Machine Learning",
      "abstract": "This paper discusses core methodologies...",
      "authors": ["John Doe", "Jane Smith"],
      "year": 2024,
      "url": "https://arxiv.org/abs/1234.5678"
    }
  ]
}
```

**Error Responses**:
- 404 Not Found - Project not found
- 400 Bad Request - Paper already in project
  ```json
  { "detail": "Paper arxiv:1234.5678 already in project" }
  ```

---

### 3.3 POST /research/summarize - Summarize a Paper

**File**: [backend/routes/research.py#L141](backend/routes/research.py)

**Request**:
```json
{
  "paper_id": "arxiv:1234.5678"
}
```

**Success Response** (200 OK):
```json
{
  "paper_id": "arxiv:1234.5678",
  "summary": "The methodology involves a novel approach to the problem, yielding a 20% improvement in accuracy. Key findings suggest that existing frameworks can be adapted effectively."
}
```

**Note**: Mock implementation. Ready for NLP integration (summarization models).

---

## 4. GENERATION API

### 4.1 POST /generate/{project_id}/assignment - Generate Assignment

**File**: [backend/routes/generate.py#L34](backend/routes/generate.py)

**Request**:
```json
{
  "paper_ids": ["arxiv:1234.5678", "semantic:987654"]
}
```

**Fields**:
- `paper_ids`: Optional array of paper IDs to use. If omitted, uses ALL project papers.

**Success Response** (200 OK):
```json
{
  "status": "success",
  "project_id": 1,
  "title": "Comprehensive Analysis: AI Ethics in Healthcare",
  "preview": "# Comprehensive Analysis: AI Ethics in Healthcare\n\n## Executive Summary\nThis assignment synthesizes current research in \"AI Ethics in Healthcare\" through comprehensive analysis of peer-reviewed literature...",
  "citations_count": 5,
  "word_count": 2847,
  "message": "High-quality assignment generated successfully"
}
```

**Generated Content Structure**:
```
1. # Title
2. ## Executive Summary
3. ## 1. Introduction
4. ## 2. Literature Review
   - Per-paper analysis
5. ## 3. Methodology Synthesis
6. ## 4. Key Findings
7. ## 5. Critical Analysis
   - Strengths
   - Limitations
8. ## 6. Implications and Recommendations
9. ## 7. Future Directions
10. ## 8. Conclusion
11. ## References
    - Formatted citations for all papers
```

**Stored in Database**:
- **Assignment.title**: Assignment title
- **Assignment.content**: Full markdown content (all sections)
- **Assignment.citations**: JSON with papers array containing:
  ```json
  {
    "id": "arxiv:1234.5678",
    "title": "Paper title",
    "authors": "Author names",
    "year": 2024,
    "citation": "Author names (2024). Paper title.",
    "url": "https://..."
  }
  ```

**Error Responses**:
- 404 Not Found - Project not found
- 400 Bad Request - No papers in project

---

### 4.2 PUT /generate/{project_id}/assignment - Update Assignment

**File**: [backend/routes/generate.py#L117](backend/routes/generate.py)

**Request**:
```json
{
  "title": "New Assignment Title",
  "content": "Updated assignment content in markdown format...",
  "citations": { ... }
}
```

**Success Response** (200 OK):
```json
{
  "status": "success",
  "message": "Assignment updated"
}
```

---

### 4.3 POST /generate/{project_id}/ppt - Generate Presentation

**File**: [backend/routes/generate.py#L131](backend/routes/generate.py)

**Request**:
```json
{
  "assignment_id": 1
}
```

**Success Response** (200 OK):
```json
{
  "status": "success",
  "project_id": 1,
  "slides": [
    {
      "slide_number": 1,
      "title": "AI Ethics in Healthcare",
      "layout": "title",
      "content": "Introduction and Overview",
      "speaker_notes": "Welcome to this presentation on AI Ethics in Healthcare. Today we'll explore key concepts and findings."
    },
    {
      "slide_number": 2,
      "title": "Key Concepts",
      "layout": "bullet",
      "content": [
        "Definition and scope of the topic",
        "Historical context",
        "Recent developments"
      ],
      "speaker_notes": "These are the foundational concepts we need to understand."
    },
    {
      "slide_number": 3,
      "title": "Literature Review",
      "layout": "bullet",
      "content": [
        "Analysis of 5 research papers",
        "Key findings from the literature",
        "Common themes and patterns"
      ],
      "speaker_notes": "Recent research in this field has revealed important insights."
    },
    {
      "slide_number": 4,
      "title": "Key Findings",
      "layout": "bullet",
      "content": [
        "Main discovery 1",
        "Main discovery 2",
        "Main discovery 3"
      ],
      "speaker_notes": "These findings have significant implications for the field."
    },
    {
      "slide_number": 5,
      "title": "Conclusion",
      "layout": "title",
      "content": "Summary and Future Directions",
      "speaker_notes": "Thank you for your attention. Let's open the floor for questions."
    }
  ]
}
```

---

## 5. EXPORT API

### 5.1 POST /export/pdf - Queue PDF Export (Async)

**File**: [backend/routes/export.py#L13](backend/routes/export.py)

**Request**:
```json
{
  "project_id": 1,
  "assignment_id": 1
}
```

**Success Response** (200 OK):
```json
{
  "status": "queued",
  "job_id": "a7f4e6c1-2b3d-4e5f-6a7b-8c9d0e1f2a3b",
  "message": "PDF export job queued successfully",
  "poll_url": "/api/v1/jobs/a7f4e6c1-2b3d-4e5f-6a7b-8c9d0e1f2a3b"
}
```

**Flow**:
1. Validates project ownership
2. Validates assignment exists
3. Queues `export_assignment_pdf` Celery task with (project_id, assignment_id)
4. Returns immediately with job_id
5. Frontend polls `/jobs/{job_id}` for status

**Error Responses**:
- 404 Not Found - Project or assignment not found

---

### 5.2 POST /export/pptx - Queue PowerPoint Export (Async)

**File**: [backend/routes/export.py#L40](backend/routes/export.py)

**Request**:
```json
{
  "project_id": 1,
  "presentation_id": 1
}
```

**Success Response** (200 OK):
```json
{
  "status": "queued",
  "job_id": "b8g5f7d2-3c4e-5f6g-7b8c-9d0e1f2a3b4c",
  "message": "PPTX export job queued successfully",
  "poll_url": "/api/v1/jobs/b8g5f7d2-3c4e-5f6g-7b8c-9d0e1f2a3b4c"
}
```

---

### 5.3 GET /export/{project_id}/downloads - Get Project Exports

**File**: [backend/routes/export.py#L67](backend/routes/export.py)

**Request**:
```
GET /export/1/downloads
Authorization: Bearer {token}
```

**Success Response** (200 OK):
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
    },
    {
      "id": 2,
      "file_type": "pptx",
      "file_path": "/generated/presentation_1_1.pptx",
      "file_url": "http://localhost:8000/downloads/presentation_1_1.pptx",
      "created_at": "2024-01-15T10:35:00"
    }
  ]
}
```

---

## 6. JOBS API (Async Task Tracking)

### 6.1 GET /jobs/{job_id} - Get Job Status

**File**: [backend/routes/jobs.py#L5](backend/routes/jobs.py)

**Request**:
```
GET /jobs/a7f4e6c1-2b3d-4e5f-6a7b-8c9d0e1f2a3b
```

**Responses by Status**:

#### Status: PENDING
```json
{
  "job_id": "a7f4e6c1-2b3d-4e5f-6a7b-8c9d0e1f2a3b",
  "status": "pending",
  "message": "Task is waiting to be executed"
}
```

#### Status: PROGRESS
```json
{
  "job_id": "a7f4e6c1-2b3d-4e5f-6a7b-8c9d0e1f2a3b",
  "status": "processing",
  "message": "Task is being processed",
  "progress": 50,
  "total": 100
}
```

#### Status: SUCCESS
```json
{
  "job_id": "a7f4e6c1-2b3d-4e5f-6a7b-8c9d0e1f2a3b",
  "status": "completed",
  "message": "Task completed successfully",
  "result": {
    "status": "completed",
    "project_id": 1,
    "file_type": "pdf",
    "file_path": "/generated/assignment_1_1.pdf"
  }
}
```

#### Status: FAILURE
```json
{
  "job_id": "a7f4e6c1-2b3d-4e5f-6a7b-8c9d0e1f2a3b",
  "status": "failed",
  "message": "Task failed",
  "error": "Error message describing what went wrong"
}
```

#### Status: RETRY
```json
{
  "job_id": "a7f4e6c1-2b3d-4e5f-6a7b-8c9d0e1f2a3b",
  "status": "retrying",
  "message": "Task is being retried"
}
```

---

### 6.2 GET /jobs/{job_id}/result - Get Completed Job Result

**File**: [backend/routes/jobs.py#L45](backend/routes/jobs.py)

**Request**:
```
GET /jobs/a7f4e6c1-2b3d-4e5f-6a7b-8c9d0e1f2a3b/result
```

**Success Response** (200 OK) - If task completed:
```json
{
  "job_id": "a7f4e6c1-2b3d-4e5f-6a7b-8c9d0e1f2a3b",
  "status": "completed",
  "result": {
    "status": "completed",
    "project_id": 1,
    "file_type": "pdf",
    "file_path": "/generated/assignment_1_1.pdf"
  }
}
```

**Error Response** (400 Bad Request) - If task still running:
```json
{ "detail": "Task is still pending" }
```

**Error Response** (400 Bad Request) - If task failed:
```json
{ "detail": "Task failed: error message" }
```

---

### 6.3 DELETE /jobs/{job_id} - Cancel Job

**File**: [backend/routes/jobs.py#L70](backend/routes/jobs.py)

**Request**:
```
DELETE /jobs/a7f4e6c1-2b3d-4e5f-6a7b-8c9d0e1f2a3b
```

**Success Response** (200 OK):
```json
{
  "job_id": "a7f4e6c1-2b3d-4e5f-6a7b-8c9d0e1f2a3b",
  "status": "cancelled",
  "message": "Job cancelled successfully"
}
```

---

## Common HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | OK | Successful read/update |
| 201 | Created | Resource created (POST) |
| 202 | Accepted | Job accepted (async) |
| 400 | Bad Request | Invalid input data |
| 401 | Unauthorized | Missing/invalid token |
| 404 | Not Found | Resource doesn't exist |
| 500 | Server Error | Unexpected error |

---

## Error Response Format

All errors follow this format:
```json
{
  "detail": "Human-readable error message"
}
```

Example:
```json
{
  "detail": "Project not found"
}
```

---

## Authentication Header Format

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsImVtYWlsIjoiam9obkBleGFtcGxlLmNvbSIsImV4cCI6MTcwNTMxODIwMH0.xyz
```

Components:
- `Bearer` - Literal string
- Space
- `<jwt_token>` - Token from `/auth/login` response

---

## Rate Limiting & Quotas

**Currently**: None implemented

**Recommended for Production**:
- 100 requests per minute per user
- Maximum 10 projects per user
- Maximum 50 papers per project
- Maximum file size: 10 MB

---

## Pagination

**Currently**: Not implemented

**All list endpoints** return all results. For production, consider:
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 45,
    "total_pages": 3
  }
}
```

---

## Versioning

Current API version: `v1`
Future versions: Update base URL to `/api/v2`, `/api/v3`, etc.

---

## CORS Configuration

**Current**: Allows all origins (`allow_origins=["*"]`)

**For Production**, restrict to:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

---

## API Documentation

Interactive documentation available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

These are automatically generated from FastAPI route definitions.
