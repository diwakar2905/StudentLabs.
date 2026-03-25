"""
Database models for the StudentLabs application.
All SQLAlchemy ORM models are defined here.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class User(Base):
    """User model - represents a student/teacher using the platform"""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    password_hash = Column(String)
    plan = Column(String, default="free")  # free, pro, enterprise
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")


class Project(Base):
    """Project model - represents a research/assignment project"""
    
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    title = Column(String, index=True)
    topic = Column(String)
    status = Column(String, default="draft")  # draft, in_progress, completed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="projects")
    papers = relationship("Paper", back_populates="project", cascade="all, delete-orphan")
    summary = relationship("Summary", back_populates="project", uselist=False, cascade="all, delete-orphan")
    assignment = relationship("Assignment", back_populates="project", uselist=False, cascade="all, delete-orphan")
    presentation = relationship("Presentation", back_populates="project", uselist=False, cascade="all, delete-orphan")
    exports = relationship("Export", back_populates="project", cascade="all, delete-orphan")
    embeddings = relationship("Embedding", back_populates="project", cascade="all, delete-orphan")


class Paper(Base):
    """Paper model - represents a research paper added to a project"""
    
    __tablename__ = "papers"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), index=True)
    paper_id = Column(String)  # External paper ID (e.g., arXiv ID)
    title = Column(String)
    abstract = Column(Text)
    authors = Column(String)
    year = Column(Integer)
    summary = Column(Text, nullable=True)
    url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="papers")


class Summary(Base):
    """Summary model - condensed information about project"""
    
    __tablename__ = "summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), index=True, unique=True)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="summary")


class Assignment(Base):
    """Assignment model - generated academic assignment"""
    
    __tablename__ = "assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), index=True, unique=True)
    title = Column(String)
    content = Column(Text)  # Markdown content
    citations = Column(JSON)  # Store formatted citations
    word_count = Column(Integer, nullable=True)
    rag_used = Column(Integer, default=0)  # Boolean: whether RAG was used
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="assignment")


class Presentation(Base):
    """Presentation model - generated PowerPoint presentation"""
    
    __tablename__ = "presentations"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), index=True, unique=True)
    slides_json = Column(JSON)  # Store slide structure as JSON
    slide_count = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="presentation")


class Export(Base):
    """Export model - tracks generated PDF/PPT files"""
    
    __tablename__ = "exports"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), index=True)
    file_type = Column(String)  # pdf, pptx
    file_path = Column(String)
    file_url = Column(String, nullable=True)  # S3 URL if uploaded
    file_size = Column(Integer, nullable=True)  # Size in bytes
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="exports")


class Embedding(Base):
    """Embedding model - stores embedding vectors for RAG retrieval"""
    
    __tablename__ = "embeddings"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), index=True)
    paper_id = Column(Integer, ForeignKey("papers.id"), index=True, nullable=True)
    vector = Column(JSON, nullable=True)  # Store as JSON list for compatibility
    embedding_data = Column(JSON, nullable=True)  # Additional metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project")
    paper = relationship("Paper")
