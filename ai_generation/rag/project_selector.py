"""Intelligent project selection for job applications."""

from typing import List, Dict, Optional
from ai_generation.embeddings.vector_store import vector_store
from ai_generation.embeddings.embedding_generator import embedding_generator
from database.db_manager import db_manager
from database.models import UserProject


class ProjectSelector:
    """Select most relevant projects for a job application."""

    def __init__(self):
        """Initialize project selector."""
        self.vector_store = vector_store
        self.embedding_gen = embedding_generator
        self.db_manager = db_manager

    def initialize(self):
        """Initialize dependencies."""
        self.vector_store.initialize()
        self.embedding_gen.initialize()
        self.db_manager.initialize()

    def select_relevant_projects(
        self,
        user_id: str,
        job: Dict,
        max_projects: int = 3
    ) -> List[Dict]:
        """Select most relevant projects for a job.

        Args:
            user_id: User ID
            job: Job dictionary
            max_projects: Maximum number of projects to select

        Returns:
            List of selected projects with relevance scores
        """
        print(f"\n[PROJECT SELECTOR] Selecting projects for: {job.get('job_title')}")

        try:
            # Get job ID (use database ID if available, otherwise create temp ID)
            job_id = job.get('id', f"temp_{hash(job['job_title'] + job['company_name'])}")

            # Query vector store for relevant projects
            relevant_projects = self.vector_store.find_relevant_projects(
                job_id=str(job_id),
                user_id=user_id,
                n_results=max_projects * 2  # Get extras for scoring
            )

            if not relevant_projects:
                print(f"  No projects found for user {user_id}")
                return []

            # Calculate comprehensive relevance scores
            scored_projects = []

            for proj_data in relevant_projects:
                project_id = proj_data['project_id']

                # Get full project details from database
                with self.db_manager.db as session:
                    project = session.query(UserProject).filter(
                        UserProject.id == project_id
                    ).first()

                    if not project:
                        continue

                    # Calculate detailed relevance
                    relevance_breakdown = self._calculate_project_relevance(
                        project, job, proj_data['relevance']
                    )

                    scored_projects.append({
                        'project': {
                            'id': str(project.id),
                            'title': project.title,
                            'description': project.description,
                            'technologies': project.technologies or [],
                            'highlights': project.highlights or [],
                            'github_url': project.github_url,
                            'demo_url': project.demo_url
                        },
                        'relevance_score': relevance_breakdown['total_score'],
                        'semantic_similarity': relevance_breakdown['semantic_score'],
                        'tech_overlap': relevance_breakdown['tech_overlap'],
                        'matching_techs': relevance_breakdown['matching_techs'],
                        'selection_reason': relevance_breakdown['reason']
                    })

            # Sort by relevance score
            scored_projects.sort(key=lambda x: x['relevance_score'], reverse=True)

            # Select top N
            selected = scored_projects[:max_projects]

            print(f"  Selected {len(selected)} projects:")
            for i, proj in enumerate(selected, 1):
                print(f"    {i}. {proj['project']['title']}")
                print(f"       Relevance: {proj['relevance_score']:.2f}")
                print(f"       Matching tech: {', '.join(proj['matching_techs'][:3])}")

            return selected

        except Exception as e:
            print(f"  [ERROR] Project selection failed: {e}")
            import traceback
            traceback.print_exc()
            return []

    def _calculate_project_relevance(
        self,
        project: UserProject,
        job: Dict,
        semantic_score: float
    ) -> Dict:
        """Calculate comprehensive project relevance.

        Args:
            project: UserProject instance
            job: Job dictionary
            semantic_score: Semantic similarity from vector search

        Returns:
            Dictionary with relevance breakdown
        """
        # Get job technologies
        job_skills = set(skill.lower() for skill in job.get('required_skills', []))
        job_title = job.get('job_title', '').lower()
        job_description = job.get('description', '').lower()

        # Extract technologies from job description if not in skills
        job_text = f"{job_title} {job_description}"
        for skill in job.get('required_skills', []):
            if skill.lower() not in job_skills:
                job_skills.add(skill.lower())

        # Get project technologies
        project_techs = set(tech.lower() for tech in (project.technologies or []))

        # Calculate technology overlap
        matching_techs = job_skills & project_techs
        tech_overlap_ratio = len(matching_techs) / len(job_skills) if job_skills else 0

        # Calculate final relevance score (semantic 60%, tech overlap 40%)
        total_score = (semantic_score * 0.6) + (tech_overlap_ratio * 0.4)

        # Generate selection reason
        reason = self._generate_selection_reason(
            project, job, semantic_score, tech_overlap_ratio, matching_techs
        )

        return {
            'total_score': total_score,
            'semantic_score': semantic_score,
            'tech_overlap': tech_overlap_ratio,
            'matching_techs': list(matching_techs),
            'reason': reason
        }

    def _generate_selection_reason(
        self,
        project: UserProject,
        job: Dict,
        semantic_score: float,
        tech_overlap: float,
        matching_techs: set
    ) -> str:
        """Generate human-readable selection reason.

        Args:
            project: Project instance
            job: Job dictionary
            semantic_score: Semantic similarity score
            tech_overlap: Technology overlap ratio
            matching_techs: Set of matching technologies

        Returns:
            Selection reason string
        """
        reasons = []

        if semantic_score > 0.8:
            reasons.append("highly relevant content")
        elif semantic_score > 0.6:
            reasons.append("relevant content")

        if tech_overlap > 0.5:
            tech_list = ', '.join(list(matching_techs)[:3])
            reasons.append(f"uses {tech_list}")
        elif tech_overlap > 0.25:
            reasons.append(f"shares {len(matching_techs)} technologies")

        if not reasons:
            reasons.append("related experience")

        return f"Selected for {' and '.join(reasons)}"


# Global instance
project_selector = ProjectSelector()
