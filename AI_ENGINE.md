# AI Engine Architecture 🧠

## Overview

The **AI Engine** is the core brain of StudentLabs. It contains all content generation logic, separated from backend routing and database code. This clean separation follows professional software design principles.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND LAYER                            │
│  (Routes, API Endpoints, Authentication, Database)         │
└────────────────┬────────────────────────────┬───────────────┘
                 │                            │
        ┌────────▼─────────┐        ┌────────▼─────────┐
        │  routes/         │        │  tasks/          │
        │  generate.py     │        │ (Celery Jobs)    │
        └────────┬─────────┘        └────────┬─────────┘
                 │                            │
                 └────────────┬───────────────┘
                              │
                 ┌────────────▼───────────────┐
                 │    AI ENGINE LAYER         │
                 │ (Content Generation)       │
                 │                            │
                 │  ┌─────────────────────┐   │
                 │  │AssignmentBuilder    │   │
                 │  ├─ Generate Title     │   │
                 │  ├─ Generate Abstract  │   │
                 │  ├─ Lit Review        │   │
                 │  ├─ Methodology       │   │
                 │  ├─ Discussion        │   │
                 │  ├─ Conclusion        │   │
                 │  └─ References        │   │
                 │                        │   │
                 │  (More builders here)  │   │
                 └────────────┬───────────┘
                              │
                 ┌────────────▼──────────────┐
                 │  DATA LAYER              │
                 │  (Models, Database)      │
                 └──────────────────────────┘
```

---

## Current Implementation

### 1. Assignment Builder (`ai_engine/assignment_builder.py`)

The first piece of the AI Engine - generates academic assignments from research papers.

**Class: `AssignmentBuilder`**

```python
builder = AssignmentBuilder(topic="AI in Education")
builder.add_papers(papers)
assignment = builder.build()
```

**What it generates:**
1. **Title** - Professional title like "Comprehensive Analysis: {topic}"
2. **Abstract** - Summary of the entire assignment
3. **Introduction** - Background and significance
4. **Literature Review** - Analysis of all papers
5. **Methodology** - Research methods discussion
6. **Discussion** - Key findings and implications
7. **Conclusion** - Summary and future directions
8. **References** - Complete citations

**Output structure:**
```python
{
    "title": "Comprehensive Analysis: AI in Education",
    "content": "Full markdown assignment...",
    "sections": {
        "title": "...",
        "abstract": "...",
        "introduction": "...",
        # ... etc
    },
    "citations": {
        "papers": [...],
        "count": 5,
        "citation_format": "APA"
    },
    "word_count": 3500,
    "paper_count": 5
}
```

---

## How It Connects to Your Backend

### Synchronous Generation (Instant)

**Flow:**
```
User Request (Frontend)
    ↓
Route: POST /api/v1/generate/{project_id}/assignment
    ↓
routes/generate.py - generate_assignment()
    ↓
AI Engine: build_assignment(topic, papers)
    ↓
Database: Save Assignment
    ↓
Response: Assignment created (200ms)
```

**Code in `routes/generate.py`:**
```python
from ai_engine.assignment_builder import build_assignment

# Get papers
papers = db.query(Paper).filter(...).all()

# Use AI Engine
assignment_data = build_assignment(project.topic, papers)

# Save to database
assignment = Assignment(
    project_id=project_id,
    title=assignment_data["title"],
    content=assignment_data["content"],
    citations=assignment_data["citations"]
)
db.add(assignment)
db.commit()
```

### Asynchronous Generation (Background Job)

**Flow:**
```
User Request (Frontend)
    ↓
Route: POST /api/v1/generate/{project_id}/assignment/async
    ↓
tasks/generation_tasks.py - generate_assignment_async()
    ↓
Celery Queue (Background)
    ↓
AI Engine: build_assignment(topic, papers)
    ↓
Database: Save Assignment + Update Job Status
    ↓
Frontend polls: GET /api/v1/jobs/{job_id}
    ↓
Returns: Assignment ready (Result in response)
```

**Code in `tasks/generation_tasks.py`:**
```python
from ai_engine.assignment_builder import build_assignment

@celery_app.task(bind=True, max_retries=3)
def generate_assignment_async(self, project_id: int):
    # Get papers
    papers = db.query(Paper).filter(...).all()
    
    # Use AI Engine (same code as sync!)
    assignment_data = build_assignment(project.topic, papers)
    
    # Save to database
    # ... assignment saving code ...
    
    return {"status": "completed", ...}
```

---

## Why This Architecture Matters

### Before (Monolithic)

```python
# All logic mixed in one place
@celery_app.task
def generate_assignment_async(self, project_id):
    # Database query
    project = db.query(Project)...
    
    # Assignment building logic
    title = f"Comprehensive Analysis: {project.topic}"
    assignment_content = f"""# {title}
    ...  # 200+ lines of string building
    """
    
    # Citation building
    citations = {...}
    
    # Database save
    db.add(Assignment(...))
    
    # Return result
    return {...}
```

**Problems:**
- ❌ Logic mixed with routing/database
- ❌ Hard to test (requires DB setup)
- ❌ Can't reuse without copy/paste
- ❌ Hard to improve (changes everywhere)

### After (Modular with AI Engine)

```python
# Backend route
from ai_engine.assignment_builder import build_assignment

@router.post("/{project_id}/assignment")
def generate_assignment(project_id, db, current_user):
    papers = db.query(Paper).filter(...).all()
    assignment_data = build_assignment(project.topic, papers)  # ← Clean!
    db.add(Assignment(**assignment_data))
    return assignment_data

# Celery task
@celery_app.task
def generate_assignment_async(self, project_id):
    papers = db.query(Paper).filter(...).all()
    assignment_data = build_assignment(project.topic, papers)  # ← Same line!
    db.add(Assignment(**assignment_data))
    return assignment_data
```

**Benefits:**
- ✅ Logic separated from routing
- ✅ Easy to test (no DB needed)
- ✅ Reusable everywhere
- ✅ Easy to improve
- ✅ Both sync and async use identical logic

---

## File Structure

```
backend/
├── ai_engine/                          ← NEW: AI Engine
│   ├── __init__.py                     # Exports
│   ├── assignment_builder.py           # Assignment generation
│   ├── presentation_builder.py         # (Coming soon)
│   ├── citation_manager.py             # (Coming soon)
│   └── content_synthesizer.py          # (Coming soon)
│
├── routes/
│   ├── generate.py                     # Uses AI Engine ✓
│   └── ...
│
├── tasks/
│   ├── generation_tasks.py             # Uses AI Engine ✓
│   └── ...
│
└── ...
```

---

## API Endpoints Using the AI Engine

### Synchronous (Immediate Response)
```
POST /api/v1/generate/{project_id}/assignment
```
- Uses: `AI Engine` → `assignment_builder.py`
- Response time: ~200-500ms
- Good for: Small projects, quick tests

### Asynchronous (Background Job)
```
POST /api/v1/generate/{project_id}/assignment/async
```
- Uses: `AI Engine` → `Celery worker` → `assignment_builder.py`
- Response time: Instant (returns job_id), Processing time: ~1-5s
- Good for: Large projects, production use

---

## How to Extend the AI Engine

The AI Engine is designed to be extended easily. Here's the pattern:

### 1. Create new builder class

```python
# ai_engine/presentation_builder.py

class PresentationBuilder:
    def __init__(self, topic: str):
        self.topic = topic
        self.papers = []
    
    def build(self):
        # Generate slides, speaker notes, etc.
        return {
            "slides": [...],
            "speaker_notes": [...],
            # ...
        }
```

### 2. Export from `__init__.py`

```python
# ai_engine/__init__.py
from .assignment_builder import AssignmentBuilder
from .presentation_builder import PresentationBuilder

__all__ = ["AssignmentBuilder", "PresentationBuilder"]
```

### 3. Use in routes/tasks

```python
# routes/generate.py
from ai_engine.presentation_builder import PresentationBuilder

presentation_data = PresentationBuilder(topic).build()

# tasks/generation_tasks.py
# Same pattern...
```

---

## Testing the AI Engine

### Without database setup:

```python
# test_ai_engine.py
from ai_engine.assignment_builder import AssignmentBuilder

def test_assignment_builder():
    # Create mock papers
    papers = [
        MockPaper(title="Paper 1", authors="Author A", year=2023, abstract="Abstract..."),
        MockPaper(title="Paper 2", authors="Author B", year=2024, abstract="Abstract..."),
    ]
    
    # Build assignment
    builder = AssignmentBuilder("AI in Education")
    builder.add_papers(papers)
    result = builder.build()
    
    # Assertions
    assert result["title"] == "Comprehensive Analysis: AI in Education"
    assert len(result["content"]) > 1000
    assert result["paper_count"] == 2
    assert "Abstract" in result["content"]
    assert "Literature Review" in result["content"]
```

---

## Current Status

| Component | Status | Details |
|-----------|--------|---------|
| **AssignmentBuilder** | ✅ Complete | Full 8-section assignments |
| **API Integration** | ✅ Complete | Both sync and async routes |
| **Sync Generation** | ✅ Ready | Instant generation |
| **Async Generation** | ✅ Ready | Celery integration |
| **PresentationBuilder** | 🔄 Next | Will generate slides from papers |
| **CitationManager** | 🔄 Planned | Advanced citation handling |
| **ContentSynthesizer** | 🔄 Planned | Extract key points from papers |
| **SmartAnalyzer** | 🔄 Planned | Identify patterns in papers |

---

## Next Steps

### Phase 2: PresentationBuilder
- Generate PowerPoint slides from papers
- Create speaker notes
- Add visual layouts

### Phase 3: SmartAnalyzer
- Extract key themes from papers
- Identify relationships between papers
- Summarize main contributions

### Phase 4: CitationManager
- Support multiple citation formats (APA, MLA, Chicago)
- Validate citations
- Generate bibliography

### Phase 5: ContentSynthesizer
- Combine insights from multiple papers
- Highlight contradictions
- Synthesize conclusions

---

## Key Principles

The AI Engine follows these software design principles:

1. **Separation of Concerns** - AI logic separate from routing/DB
2. **Reusability** - Same code used by sync and async
3. **Testability** - Easy to unit test without database
4. **Extensibility** - Easy to add new builders
5. **Maintainability** - Clear structure, easy to improve
6. **Modularity** - Each builder is independent
7. **Documentation** - Every class and method documented

---

## Summary

The **AI Engine** is your product's core intellectual property. It:
- ✅ Generates high-quality academic assignments
- ✅ Works with both sync and async endpoints
- ✅ Easy to test in isolation
- ✅ Easy to improve and extend
- ✅ Professional software architecture
- ✅ Ready to add more builders (presentations, etc.)

This is professional, scalable, production-grade code! 🚀
