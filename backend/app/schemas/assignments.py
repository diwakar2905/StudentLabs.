"""
API Request/Response Schemas

Pydantic models for request/response validation and documentation.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class AssignmentGenerateRequest(BaseModel):
    """Request to generate an assignment"""
    user_id: int = Field(..., description="User ID (for ownership verification)")
    topic: Optional[str] = Field(None, description="Custom topic (uses project topic if not provided)")
    async_mode: bool = Field(False, description="If true, queue as background job")
    section_types: Optional[List[str]] = Field(
        None,
        description="Specific sections to generate (abstract, introduction, literature, etc)"
    )


class AssignmentCreate(BaseModel):
    """Create new assignment"""
    project_id: int
    title: str
    content: Dict[str, str]
    citations: Optional[List[str]] = None
    word_count: Optional[int] = None
    rag_used: bool = False


class AssignmentResponse(BaseModel):
    """Assignment response"""
    id: int
    title: str
    content: Dict[str, str]
    citations: Optional[List[str]] = None
    word_count: Optional[int] = None
    rag_used: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class JobStatusResponse(BaseModel):
    """Response for async job status"""
    job_id: str
    status: str  # queued, processing, completed, failed
    progress: int = Field(0, description="Progress percentage 0-100")
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
