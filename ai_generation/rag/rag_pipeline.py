"""RAG pipeline for document generation orchestration."""

from typing import Dict, List, Optional
from ai_generation.embeddings.retriever import retriever
from ai_generation.rag.project_selector import project_selector
from ai_generation.rag.page_optimizer import page_optimizer
from database.db_manager import db_manager


class RAGPipeline:
    """Orchestrate RAG workflow for document generation."""

    def __init__(self):
        """Initialize RAG pipeline."""
        self.retriever = retriever
        self.project_selector = project_selector
        self.page_optimizer = page_optimizer
        self.db_manager = db_manager

    def initialize(self):
        """Initialize all components."""
        self.retriever.initialize()
        self.project_selector.initialize()
        self.db_manager.initialize()
        print("[OK] RAG Pipeline initialized")

    def build_context_for_cv(
        self,
        user_id: str,
        job: Dict,
        cv_preferences: Optional[Dict] = None
    ) -> Dict:
        """Build complete context for CV generation.

        Args:
            user_id: User ID
            job: Job dictionary
            cv_preferences: CV preferences (length, projects, etc.)

        Returns:
            Context dictionary with all relevant information
        """
        print(f"\n[RAG PIPELINE] Building CV context for: {job.get('job_title')}")

        # Default preferences
        if cv_preferences is None:
            cv_preferences = {
                'cv_length': 1,
                'include_projects': True,
                'max_projects_per_cv': 3,
                'project_detail_level': 'concise'
            }

        # Step 1: Retrieve profile context
        print("  [1/4] Retrieving profile context...")
        profile_context = self.retriever.get_profile_context(user_id)

        # Step 2: Retrieve job context
        print("  [2/4] Analyzing job requirements...")
        job_id = job.get('id', 'temp')
        job_context = self.retriever.get_job_context(str(job_id))

        # Step 3: Select relevant projects (if enabled)
        selected_projects = []
        projects_context = ""

        if cv_preferences.get('include_projects', False):
            print(f"  [3/4] Selecting {cv_preferences.get('max_projects_per_cv', 3)} relevant projects...")
            selected_projects = self.project_selector.select_relevant_projects(
                user_id=user_id,
                job=job,
                max_projects=cv_preferences.get('max_projects_per_cv', 3)
            )

            if selected_projects:
                projects_context = self._format_projects_context(selected_projects)

        # Step 4: Optimize for page length
        print(f"  [4/4] Optimizing content for {cv_preferences.get('cv_length', 1)} page(s)...")

        context = {
            'profile': profile_context,
            'job': job_context,
            'projects': projects_context,
            'selected_projects_data': selected_projects,
            'cv_preferences': cv_preferences,
            'job_data': job
        }

        print(f"  [OK] Context ready: {len(profile_context)} chars profile, {len(selected_projects)} projects")

        return context

    def build_context_for_cover_letter(
        self,
        user_id: str,
        job: Dict
    ) -> Dict:
        """Build context for cover letter generation.

        Args:
            user_id: User ID
            job: Job dictionary

        Returns:
            Context dictionary
        """
        print(f"\n[RAG PIPELINE] Building cover letter context for: {job.get('job_title')}")

        # Step 1: Retrieve profile
        print("  [1/3] Retrieving profile...")
        profile_context = self.retriever.get_profile_context(user_id)

        # Step 2: Retrieve job details
        print("  [2/3] Analyzing job...")
        job_id = job.get('id', 'temp')
        job_context = self.retriever.get_job_context(str(job_id))

        # Step 3: Select 1-2 key projects to mention
        print("  [3/3] Finding relevant projects to highlight...")
        selected_projects = self.project_selector.select_relevant_projects(
            user_id=user_id,
            job=job,
            max_projects=2  # Cover letters mention fewer projects
        )

        context = {
            'profile': profile_context,
            'job': job_context,
            'projects': self._format_projects_context(selected_projects) if selected_projects else '',
            'selected_projects_data': selected_projects,
            'job_data': job
        }

        print(f"  [OK] Context ready")

        return context

    def _format_projects_context(self, projects: List[Dict]) -> str:
        """Format projects for context string.

        Args:
            projects: List of selected projects with scores

        Returns:
            Formatted projects string
        """
        if not projects:
            return ""

        context = "\n=== SELECTED PROJECTS ===\n"

        for i, proj_data in enumerate(projects, 1):
            proj = proj_data['project']
            context += f"\n{i}. {proj['title']}\n"
            context += f"   Relevance Score: {proj_data['relevance_score']:.2f}\n"
            context += f"   Matching Technologies: {', '.join(proj_data['matching_techs'][:5])}\n"
            context += f"   Description: {proj['description'][:200]}\n"

            if proj.get('highlights'):
                context += f"   Highlights: {' | '.join(proj['highlights'][:2])}\n"

            if proj.get('technologies'):
                context += f"   Tech Stack: {', '.join(proj['technologies'][:5])}\n"

        return context


# Global instance
rag_pipeline = RAGPipeline()
