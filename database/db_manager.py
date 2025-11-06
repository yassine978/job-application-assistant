"""High-level database manager combining PostgreSQL and Chroma."""

from database.connection import db_connection
from database.vector_db_manager import vector_db
from database.models import (
    User, UserProfile, UserProject, CVPreference,
    Job, Application, Document, ProjectUsageStats
)
from typing import Dict, List, Optional
import uuid

class DatabaseManager:
    """High-level database operations manager."""
    
    def __init__(self):
        """Initialize database manager."""
        self.db = db_connection
        self.vector_db = vector_db
    
    def initialize(self):
        """Initialize both databases."""
        self.db.initialize()
        self.db.create_tables()
        self.vector_db.initialize()
        print("✅ Database manager initialized")
    
    # User operations
    def create_user(self, user_data: Dict) -> str:
        """Create a new user.
        
        Args:
            user_data: Dictionary with user information
            
        Returns:
            User ID
        """
        with self.db as session:
            user = User(
                email=user_data['email'],
                password_hash=user_data['password_hash'],
                full_name=user_data['full_name'],
                phone=user_data.get('phone'),
                linkedin_url=user_data.get('linkedin_url'),
                location_preference=user_data.get('location_preference'),
                preferences=user_data.get('preferences', {})
            )
            session.add(user)
            session.commit()
            user_id = str(user.id)
            
            print(f"✅ User created: {user.email}")
            return user_id
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email.
        
        Args:
            email: User email
            
        Returns:
            User object or None
        """
        with self.db as session:
            user = session.query(User).filter(User.email == email).first()
            return user
    
    # Profile operations
    def create_profile(self, user_id: str, profile_data: Dict) -> str:
        """Create user profile.
        
        Args:
            user_id: User ID
            profile_data: Dictionary with profile information
            
        Returns:
            Profile ID
        """
        with self.db as session:
            profile = UserProfile(
                user_id=uuid.UUID(user_id),
                skills=profile_data.get('skills', []),
                experience=profile_data.get('experience', {}),
                education=profile_data.get('education', {}),
                languages=profile_data.get('languages', [])
            )
            session.add(profile)
            session.commit()
            profile_id = str(profile.id)
            
            print(f"✅ Profile created for user: {user_id}")
            return profile_id
    
    # Project operations
    def create_project(self, user_id: str, project_data: Dict) -> str:
        """Create user project.
        
        Args:
            user_id: User ID
            project_data: Dictionary with project information
            
        Returns:
            Project ID
        """
        with self.db as session:
            project = UserProject(
                user_id=uuid.UUID(user_id),
                title=project_data['title'],
                description=project_data.get('description'),
                readme_content=project_data.get('readme_content'),
                github_url=project_data.get('github_url'),
                demo_url=project_data.get('demo_url'),
                technologies=project_data.get('technologies', []),
                highlights=project_data.get('highlights', [])
            )
            session.add(project)
            session.commit()
            project_id = str(project.id)
            
            print(f"✅ Project created: {project.title}")
            return project_id
    
    # Job operations
    def create_job(self, job_data: Dict) -> str:
        """Create job posting.
        
        Args:
            job_data: Dictionary with job information
            
        Returns:
            Job ID
        """
        with self.db as session:
            job = Job(
                source=job_data['source'],
                job_title=job_data['job_title'],
                company_name=job_data['company_name'],
                location=job_data.get('location'),
                job_type=job_data.get('job_type'),
                description=job_data.get('description'),
                required_skills=job_data.get('required_skills', []),
                posting_date=job_data.get('posting_date'),
                application_url=job_data.get('application_url'),
                salary_range=job_data.get('salary_range'),
                language=job_data.get('language')
            )
            session.add(job)
            session.commit()
            job_id = str(job.id)
            
            return job_id
    
    def get_all_jobs(self) -> List[Job]:
        """Get all jobs from database.
        
        Returns:
            List of Job objects
        """
        with self.db as session:
            jobs = session.query(Job).all()
            return jobs
    
    def get_stats(self) -> Dict:
        """Get database statistics.
        
        Returns:
            Dictionary with counts
        """
        with self.db as session:
            stats = {
                'users': session.query(User).count(),
                'profiles': session.query(UserProfile).count(),
                'projects': session.query(UserProject).count(),
                'jobs': session.query(Job).count(),
                'applications': session.query(Application).count(),
                'documents': session.query(Document).count()
            }
            return stats


# Global database manager instance
db_manager = DatabaseManager()