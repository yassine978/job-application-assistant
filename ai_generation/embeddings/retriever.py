"""Retrieval interface for RAG (Retrieval-Augmented Generation)."""

from typing import List, Dict, Optional
from ai_generation.embeddings.vector_store import vector_store
from database.db_manager import db_manager

class Retriever:
    """Retrieve relevant context for RAG pipeline."""
    
    def __init__(self):
        """Initialize retriever."""
        self.vector_store = vector_store
        self.db_manager = db_manager
    
    def initialize(self):
        """Initialize dependencies."""
        self.vector_store.initialize()
        self.db_manager.initialize()
        print("[OK] Retriever initialized")
    
    def get_profile_context(self, user_id: str) -> str:
        """Get user profile as formatted text.
        
        Args:
            user_id: User ID
            
        Returns:
            Formatted profile text
        """
        # Get profile from database
        with self.db_manager.db as session:
            from database.models import UserProfile, User
            
            user = session.query(User).filter(User.id == user_id).first()
            profile = session.query(UserProfile).filter(
                UserProfile.user_id == user_id
            ).first()
            
            if not user or not profile:
                return ""
            
            # Format profile
            context = f"""
User Profile:
Name: {user.full_name}
Location: {user.location_preference or 'Not specified'}
Skills: {', '.join(profile.skills) if profile.skills else 'None'}
Languages: {', '.join(profile.languages) if profile.languages else 'None'}
"""
            
            # Add experience
            if profile.experience:
                context += "\nExperience:\n"
                exp = profile.experience
                if isinstance(exp, list):
                    for role in exp:
                        context += f"- {role.get('title', '')} at {role.get('company', '')}\n"
                elif isinstance(exp, dict) and exp.get('roles'):
                    for role in exp['roles']:
                        context += f"- {role.get('title', '')} at {role.get('company', '')}\n"
            
            # Add education
            if profile.education:
                context += "\nEducation:\n"
                edu = profile.education
                if isinstance(edu, list):
                    for degree in edu:
                        context += f"- {degree.get('degree', '')} in {degree.get('field', '')}\n"
                elif isinstance(edu, dict):
                    context += f"- {edu.get('degree', '')} in {edu.get('field', '')}\n"
            
            return context.strip()
    
    def get_relevant_projects_context(
        self, 
        user_id: str,
        job_id: str,
        max_projects: int = 3
    ) -> str:
        """Get relevant projects as formatted text.
        
        Args:
            user_id: User ID
            job_id: Job ID
            max_projects: Maximum number of projects
            
        Returns:
            Formatted projects text
        """
        # Find relevant projects
        projects = self.vector_store.find_relevant_projects(
            job_id=job_id,
            user_id=user_id,
            n_results=max_projects
        )
        
        if not projects:
            return ""
        
        # Get full project details from database
        context = "\nRelevant Projects:\n"
        
        with self.db_manager.db as session:
            from database.models import UserProject
            
            for proj_data in projects:
                project = session.query(UserProject).filter(
                    UserProject.id == proj_data['project_id']
                ).first()
                
                if project:
                    context += f"\nProject: {project.title}\n"
                    context += f"Relevance Score: {proj_data['relevance']:.2f}\n"
                    if project.description:
                        context += f"Description: {project.description}\n"
                    if project.technologies:
                        context += f"Technologies: {', '.join(project.technologies)}\n"
                    if project.highlights:
                        context += f"Highlights: {', '.join(project.highlights[:2])}\n"
        
        return context.strip()
    
    def get_job_context(self, job_id: str) -> str:
        """Get job details as formatted text.
        
        Args:
            job_id: Job ID
            
        Returns:
            Formatted job text
        """
        with self.db_manager.db as session:
            from database.models import Job
            
            job = session.query(Job).filter(Job.id == job_id).first()
            
            if not job:
                return ""
            
            context = f"""
Job Details:
Title: {job.job_title}
Company: {job.company_name}
Location: {job.location or 'Not specified'}
Type: {job.job_type or 'Not specified'}
Required Skills: {', '.join(job.required_skills) if job.required_skills else 'None'}
"""
            
            if job.description:
                # Truncate long descriptions
                desc = job.description[:500]
                context += f"\nDescription: {desc}...\n"
            
            return context.strip()
    
    def get_full_context(
        self, 
        user_id: str, 
        job_id: str,
        include_projects: bool = True,
        max_projects: int = 3
    ) -> Dict[str, str]:
        """Get all relevant context for CV/cover letter generation.
        
        Args:
            user_id: User ID
            job_id: Job ID
            include_projects: Whether to include projects
            max_projects: Maximum number of projects
            
        Returns:
            Dictionary with all context sections
        """
        context = {
            'profile': self.get_profile_context(user_id),
            'job': self.get_job_context(job_id),
            'projects': ''
        }
        
        if include_projects:
            context['projects'] = self.get_relevant_projects_context(
                user_id=user_id,
                job_id=job_id,
                max_projects=max_projects
            )
        
        return context


# Global retriever instance
retriever = Retriever()