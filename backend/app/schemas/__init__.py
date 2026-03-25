"""
Pydantic schemas for request/response validation.
Organized by domain - one schema file per entity type.
"""

from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List, Any
from enum import Enum


# ============= Enums =============

class PlanEnum(str, Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class ProjectStatusEnum(str, Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class FileTypeEnum(str, Enum):
    PDF = "pdf"
    PPTX = "pptx"


# ============= User Schemas =============

class UserCreate(BaseModel):
    """Schema for creating a new user"""
    email: EmailStr
    name: str
    password: str


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user response"""
    id: int
    email: str
    name: str
    plan: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserDetailResponse(UserResponse):
    """Extended user response with additional info"""
    projects_count: Optional[int] = 0


# ============= Project Schemas =============

class ProjectCreate(BaseModel):
    """Schema for creating a project"""
    title: str
    topic: str


class ProjectUpdate(BaseModel):
    """Schema for updating a project"""
    title: Optional[str] = None
    topic: Optional[str] = None
    status: Optional[str] = None


class ProjectResponse(BaseModel):
    """Schema for project response"""
    id: int
    title: str
    topic: str
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProjectDetailResponse(ProjectResponse):
    """Extended project response with counts"""
    papers_count: int = 0
    has_assignment: bool = False
    has_presentation: bool = False
    exports_count: int = 0


# ============= Paper Schemas =============

class PaperCreate(BaseModel):
    """Schema for adding a paper to project"""
    project_id: int
    paper_id: str
    title: str
    abstract: str
    authors: str
    year: int
    url: Optional[str] = None


class PaperResponse(BaseModel):
    """Schema for paper response"""
    id: int
    paper_id: str
    title: str
    abstract: str
    authors: str
    year: int
    summary: Optional[str] = None
    url: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============= Assignment Schemas =============

class AssignmentCreate(BaseModel):
    """Schema for creating an assignment"""
    title: str
    content: str
    citations: Optional[dict] = None


class AssignmentResponse(BaseModel):
    """Schema for assignment response"""
    id: int
    title: str
    content: str
    citations: Optional[dict] = None
    word_count: Optional[int] = None
    rag_used: bool = False
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============= Presentation Schemas =============

class PresentationResponse(BaseModel):
    """Schema for presentation response"""
    id: int
    slides_json: dict
    slide_count: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============= Export Schemas =============

class ExportCreate(BaseModel):
    """Schema for creating an export"""
    project_id: int
    file_type: FileTypeEnum


class ExportResponse(BaseModel):
    """Schema for export response"""
    id: int
    file_type: str
    file_path: str
    file_url: Optional[str] = None
    file_size: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============= Research Schemas =============

class ResearchQuery(BaseModel):
    """Schema for research paper search"""
    topic: str
    max_results: int = 5
    project_id: Optional[int] = None


class ResearchResponse(BaseModel):
    """Schema for research papers response"""
    papers: List[dict]
    count: int
    status: str


# ============= Job Schemas =============

class JobStatusResponse(BaseModel):
    """Schema for async job status"""
    job_id: str
    status: str  # pending, started, success, failure
    result: Optional[Any] = None
    error: Optional[str] = None


# ============= Auth Schemas =============

class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str


class TokenResponse(BaseModel):
    """Schema for auth response"""
    access_token: str
    token_type: str
    user: UserResponse
