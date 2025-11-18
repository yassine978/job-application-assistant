"""RAG-powered job ranking using semantic similarity and context."""

from typing import List, Dict, Optional
from ai_generation.embeddings.vector_store import vector_store
from ai_generation.embeddings.embedding_generator import embedding_generator
from database.db_manager import db_manager
from database.models import UserProfile, User
import numpy as np


class RAGRanker:
    """Rank jobs using RAG (Retrieval-Augmented Generation) approach."""

    def __init__(self):
        """Initialize RAG ranker."""
        self.vector_store = vector_store
        self.embedding_gen = embedding_generator
        self.db_manager = db_manager

    def initialize(self):
        """Initialize dependencies."""
        self.vector_store.initialize()
        self.embedding_gen.initialize()
        self.db_manager.initialize()
        print("[OK] RAG Ranker initialized")

    def rank_jobs(
        self,
        user_id: str,
        jobs: List[Dict],
        top_n: Optional[int] = None
    ) -> List[Dict]:
        """Rank jobs using RAG-enhanced scoring.

        Args:
            user_id: User ID
            jobs: List of job dictionaries
            top_n: Return only top N jobs (None = all)

        Returns:
            List of jobs with match scores, sorted by score (descending)
        """
        print(f"\n[RAG RANKER] Ranking {len(jobs)} jobs for user {user_id}")

        # Calculate match score for each job
        ranked_jobs = []

        for i, job in enumerate(jobs):
            if (i + 1) % 10 == 0:
                print(f"  Processing job {i + 1}/{len(jobs)}...")

            try:
                # Calculate comprehensive match score
                match_data = self._calculate_match_score(user_id, job)

                # Add match data to job
                job_with_score = {**job}
                job_with_score['match_score'] = match_data['total_score']
                job_with_score['match_score_breakdown'] = match_data['breakdown']

                ranked_jobs.append(job_with_score)

            except Exception as e:
                print(f"  [WARNING] Error ranking job '{job.get('job_title')}': {e}")
                # Add job with zero score
                job_with_score = {**job}
                job_with_score['match_score'] = 0.0
                job_with_score['match_score_breakdown'] = {}
                ranked_jobs.append(job_with_score)

        # Sort by match score (descending)
        ranked_jobs.sort(key=lambda x: x['match_score'], reverse=True)

        # Return top N if specified
        if top_n:
            ranked_jobs = ranked_jobs[:top_n]

        print(f"[RAG RANKER] Complete. Top score: {ranked_jobs[0]['match_score']:.1f}" if ranked_jobs else "[RAG RANKER] No jobs ranked")

        return ranked_jobs

    def _calculate_match_score(self, user_id: str, job: Dict) -> Dict:
        """Calculate comprehensive match score for a job.

        Args:
            user_id: User ID
            job: Job dictionary

        Returns:
            Dictionary with total score and breakdown
        """
        # Get user profile
        user_profile = self._get_user_profile(user_id)

        if not user_profile:
            return {
                'total_score': 0.0,
                'breakdown': {'error': 'User profile not found'}
            }

        # Component scores
        semantic_score = self._calculate_semantic_similarity(user_profile, job)
        skill_score = self._calculate_skill_match(user_profile, job)
        location_score = self._calculate_location_match(user_profile, job)
        job_type_score = self._calculate_job_type_match(user_profile, job)
        language_score = self._calculate_language_match(user_profile, job)
        freshness_score = self._calculate_freshness_score(job)
        past_success_boost = self._calculate_past_success_boost(user_id, job)

        # Weighted total score (as per spec)
        total_score = (
            semantic_score * 30 +
            skill_score * 30 +
            location_score * 15 +
            job_type_score * 15 +
            language_score * 5 +
            freshness_score * 5 +
            past_success_boost  # Flat boost, not weighted
        )

        breakdown = {
            'semantic_similarity': round(semantic_score, 2),
            'skill_match': round(skill_score, 2),
            'location_match': round(location_score, 2),
            'job_type_match': round(job_type_score, 2),
            'language_match': round(language_score, 2),
            'freshness': round(freshness_score, 2),
            'past_success_boost': round(past_success_boost, 2),
            'total': round(total_score, 2)
        }

        return {
            'total_score': total_score,
            'breakdown': breakdown
        }

    def _get_user_profile(self, user_id: str) -> Optional[Dict]:
        """Get user profile from database.

        Args:
            user_id: User ID

        Returns:
            User profile dictionary or None
        """
        try:
            with self.db_manager.db as session:
                user = session.query(User).filter(User.id == user_id).first()
                profile = session.query(UserProfile).filter(
                    UserProfile.user_id == user_id
                ).first()

                if not user or not profile:
                    return None

                return {
                    'user_id': str(user.id),
                    'full_name': user.full_name,
                    'location_preference': user.location_preference,
                    'preferences': user.preferences or {},
                    'skills': profile.skills or [],
                    'experience': profile.experience or [],
                    'education': profile.education or [],
                    'languages': profile.languages or []
                }

        except Exception as e:
            print(f"  [ERROR] Getting user profile: {e}")
            return None

    def _calculate_semantic_similarity(self, user_profile: Dict, job: Dict) -> float:
        """Calculate semantic similarity using embeddings.

        Args:
            user_profile: User profile dictionary
            job: Job dictionary

        Returns:
            Similarity score (0-1)
        """
        try:
            # Get user profile embedding from vector store
            user_id = user_profile['user_id']
            profile_results = self.vector_store.vector_db.collections["user_profiles"].get(
                ids=[user_id],
                include=["embeddings"]
            )

            if not profile_results['ids'] or not profile_results['embeddings']:
                return 0.0

            profile_embedding = profile_results['embeddings'][0]

            # Generate job embedding
            job_embedding = self.embedding_gen.embed_job(job)

            # Calculate cosine similarity
            similarity = self.embedding_gen.calculate_similarity(
                profile_embedding,
                job_embedding
            )

            return similarity

        except Exception as e:
            print(f"  [WARNING] Semantic similarity error: {e}")
            return 0.0

    def _calculate_skill_match(self, user_profile: Dict, job: Dict) -> float:
        """Calculate skill overlap score using TF-IDF-like approach.

        Args:
            user_profile: User profile dictionary
            job: Job dictionary

        Returns:
            Skill match score (0-1)
        """
        user_skills = set(skill.lower() for skill in user_profile.get('skills', []))
        job_skills = set(skill.lower() for skill in job.get('required_skills', []))

        if not job_skills:
            return 0.5  # Neutral if no skills listed

        # Calculate overlap
        overlap = user_skills & job_skills
        overlap_ratio = len(overlap) / len(job_skills) if job_skills else 0

        return overlap_ratio

    def _calculate_location_match(self, user_profile: Dict, job: Dict) -> float:
        """Calculate location match score.

        Args:
            user_profile: User profile dictionary
            job: Job dictionary

        Returns:
            Location match score (0-1)
        """
        user_location = user_profile.get('location_preference', '').lower()
        job_location = job.get('location', '').lower()

        if not user_location or not job_location:
            return 0.5  # Neutral if missing

        # Remote jobs get high score
        if 'remote' in job_location:
            return 1.0

        # Exact match
        if user_location in job_location or job_location in user_location:
            return 1.0

        # Partial match (same city/region)
        user_parts = set(user_location.split())
        job_parts = set(job_location.split())

        if user_parts & job_parts:
            return 0.7

        return 0.0

    def _calculate_job_type_match(self, user_profile: Dict, job: Dict) -> float:
        """Calculate job type match score.

        Args:
            user_profile: User profile dictionary
            job: Job dictionary

        Returns:
            Job type match score (0-1)
        """
        preferences = user_profile.get('preferences', {})
        preferred_types = preferences.get('preferred_job_types', [])

        if not preferred_types:
            return 0.5  # Neutral if no preference

        job_type = job.get('job_type', '').lower()
        preferred_types_lower = [jt.lower() for jt in preferred_types]

        # Check if job type matches any preference
        for pref_type in preferred_types_lower:
            if pref_type in job_type or job_type in pref_type:
                return 1.0

        return 0.0

    def _calculate_language_match(self, user_profile: Dict, job: Dict) -> float:
        """Calculate language match score.

        Args:
            user_profile: User profile dictionary
            job: Job dictionary

        Returns:
            Language match score (0-1)
        """
        user_languages = [lang.lower() for lang in user_profile.get('languages', [])]
        job_language = job.get('language', 'en').lower()

        # Check if user speaks the job language
        if 'english' in user_languages or 'anglais' in user_languages:
            if job_language == 'en':
                return 1.0

        if 'french' in user_languages or 'français' in user_languages or 'francais' in user_languages:
            if job_language == 'fr':
                return 1.0

        # Default to partial match
        return 0.5

    def _calculate_freshness_score(self, job: Dict) -> float:
        """Calculate freshness score based on posting age.

        Args:
            job: Job dictionary

        Returns:
            Freshness score (0-1)
        """
        from datetime import datetime, timedelta

        posting_date = job.get('posting_date')

        if not posting_date or not isinstance(posting_date, datetime):
            return 0.5  # Neutral if unknown

        age_days = (datetime.now() - posting_date).days

        # Scoring: newer = better
        if age_days <= 1:
            return 1.0
        elif age_days <= 3:
            return 0.9
        elif age_days <= 7:
            return 0.8
        elif age_days <= 14:
            return 0.6
        elif age_days <= 30:
            return 0.4
        else:
            return 0.2

    def _calculate_past_success_boost(self, user_id: str, job: Dict) -> float:
        """Calculate boost based on past successful applications.

        Args:
            user_id: User ID
            job: Job dictionary

        Returns:
            Boost score (0-10)
        """
        try:
            # Query for similar successful jobs from vector store
            job_embedding = self.embedding_gen.embed_job(job)

            # Check if there are similar successful applications
            # (This would require tracking successful applications)
            # For now, return 0 - implement when we have application tracking

            return 0.0

        except Exception as e:
            return 0.0


# Global ranker instance
rag_ranker = RAGRanker()
