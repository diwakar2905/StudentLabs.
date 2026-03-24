from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
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

class Paper(Base):
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
    __tablename__ = "summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), index=True, unique=True)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="summary")

class Assignment(Base):
    __tablename__ = "assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), index=True, unique=True)
    title = Column(String)
    content = Column(Text)
    citations = Column(JSON)  # Store formatted citations
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="assignment")

class Presentation(Base):
    __tablename__ = "presentations"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), index=True, unique=True)
    slides_json = Column(JSON)  # Store slide structure as JSON
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="presentation")

class Export(Base):
    __tablename__ = "exports"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), index=True)
    file_type = Column(String)  # pdf, pptx
    file_path = Column(String)
    file_url = Column(String, nullable=True)  # S3 URL if uploaded
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="exports")
