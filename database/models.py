"""SQLAlchemy database models."""

from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, 
    Text, ARRAY, ForeignKey, JSON, Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid

Base = declarative_base()


class User(Base):
    """User account model."""
    __tablename__ = 'users'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(50))
    linkedin_url = Column(String(255))
    location_preference = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    preferences = Column(JSON)
    
    # Relationships
    profiles = relationship("UserProfile", back_populates="user", cascade="all, delete-orphan")
    projects = relationship("UserProject", back_populates="user", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    cv_preferences = relationship("CVPreference", back_populates="user", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(email='{self.email}', name='{self.full_name}')>"


class UserProfile(Base):
    """User profile with skills, experience, education."""
    __tablename__ = 'user_profiles'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    skills = Column(ARRAY(Text))
    experience = Column(JSON)
    education = Column(JSON)
    languages = Column(ARRAY(Text))
    chroma_id = Column(String(255))
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="profiles")
    
    def __repr__(self):
        return f"<UserProfile(user_id='{self.user_id}')>"


class UserProject(Base):
    """User projects with README content."""
    __tablename__ = 'user_projects'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    readme_content = Column(Text)
    github_url = Column(String(500))
    demo_url = Column(String(500))
    technologies = Column(ARRAY(Text))
    highlights = Column(ARRAY(Text))
    chroma_id = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="projects")
    usage_stats = relationship("ProjectUsageStats", back_populates="project", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_user_projects', 'user_id'),
        Index('idx_project_title', 'title'),
    )
    
    def __repr__(self):
        return f"<UserProject(title='{self.title}')>"


class CVPreference(Base):
    """User CV generation preferences."""
    __tablename__ = 'cv_preferences'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    cv_length = Column(Integer, default=1)
    include_projects = Column(Boolean, default=False)
    max_projects_per_cv = Column(Integer, default=3)
    project_detail_level = Column(String(20), default='concise')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="cv_preferences")
    
    def __repr__(self):
        return f"<CVPreference(user_id='{self.user_id}', cv_length={self.cv_length})>"


class Job(Base):
    """Job posting model."""
    __tablename__ = 'jobs'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source = Column(String(50), nullable=False)
    job_title = Column(String(255), nullable=False)
    company_name = Column(String(255), nullable=False)
    location = Column(String(255))
    job_type = Column(String(50))
    description = Column(Text)
    required_skills = Column(ARRAY(Text))
    posting_date = Column(DateTime)
    application_url = Column(Text)
    salary_range = Column(String(100))
    language = Column(String(10))
    chroma_id = Column(String(255))
    scraped_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    applications = relationship("Application", back_populates="job", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_company_title', 'company_name', 'job_title'),
        Index('idx_posting_date', 'posting_date'),
        Index('idx_job_type', 'job_type'),
    )
    
    def __repr__(self):
        return f"<Job(title='{self.job_title}', company='{self.company_name}')>"


class Application(Base):
    """Job application with match score."""
    __tablename__ = 'applications'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    match_score = Column(Float, nullable=False)
    match_score_breakdown = Column(JSON)
    status = Column(String(50), default='pending')
    applied_date = Column(DateTime)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    job = relationship("Job", back_populates="applications")
    user = relationship("User", back_populates="applications")
    documents = relationship("Document", back_populates="application", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_user_match', 'user_id', 'match_score'),
        Index('idx_status', 'status'),
    )
    
    def __repr__(self):
        return f"<Application(job_id='{self.job_id}', match_score={self.match_score})>"


class Document(Base):
    """Generated CV or cover letter."""
    __tablename__ = 'documents'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = Column(UUID(as_uuid=True), ForeignKey('applications.id', ondelete='CASCADE'), nullable=False)
    document_type = Column(String(20), nullable=False)  # 'cv' or 'cover_letter'
    file_path = Column(String(500), nullable=False)
    language = Column(String(10))
    cv_length = Column(Integer)
    projects_included = Column(ARRAY(UUID(as_uuid=True)))
    projects_metadata = Column(JSON)
    chroma_id = Column(String(255))
    generated_at = Column(DateTime, default=datetime.utcnow)
    generation_time_seconds = Column(Float)
    ai_model_used = Column(String(100))
    word_count = Column(Integer)
    
    # Relationships
    application = relationship("Application", back_populates="documents")
    
    __table_args__ = (
        Index('idx_application_type', 'application_id', 'document_type'),
    )
    
    def __repr__(self):
        return f"<Document(type='{self.document_type}', file='{self.file_path}')>"


class ProjectUsageStats(Base):
    """Track which projects were selected for which jobs."""
    __tablename__ = 'project_usage_stats'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey('user_projects.id', ondelete='CASCADE'), nullable=False)
    job_id = Column(UUID(as_uuid=True), ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False)
    document_id = Column(UUID(as_uuid=True), ForeignKey('documents.id', ondelete='CASCADE'))
    relevance_score = Column(Float)
    selected = Column(Boolean)
    selection_reason = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("UserProject", back_populates="usage_stats")
    
    __table_args__ = (
        Index('idx_project_usage', 'project_id'),
        Index('idx_project_selection', 'project_id', 'selected'),
    )
    
    def __repr__(self):
        return f"<ProjectUsageStats(project_id='{self.project_id}', selected={self.selected})>"


class UserSession(Base):
    """Track user sessions and activity."""
    __tablename__ = 'user_sessions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    session_start = Column(DateTime, default=datetime.utcnow)
    session_end = Column(DateTime)
    actions = Column(JSON)
    searches_performed = Column(Integer, default=0)
    applications_generated = Column(Integer, default=0)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    
    def __repr__(self):
        return f"<UserSession(user_id='{self.user_id}', start='{self.session_start}')>"


class ScrapingLog(Base):
    """Log scraping activities."""
    __tablename__ = 'scraping_logs'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source = Column(String(50), nullable=False)
    jobs_scraped = Column(Integer, default=0)
    successful = Column(Boolean, default=True)
    error_message = Column(Text)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    duration_seconds = Column(Float)
    
    def __repr__(self):
        return f"<ScrapingLog(source='{self.source}', jobs={self.jobs_scraped})>"