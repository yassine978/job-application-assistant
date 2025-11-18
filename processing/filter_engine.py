"""Filter engine for job filtering based on user preferences."""

from typing import List, Dict, Optional
from datetime import datetime, timedelta


class FilterEngine:
    """Filter jobs based on various criteria."""

    def __init__(self):
        """Initialize the filter engine."""
        pass

    def filter_jobs(
        self,
        jobs: List[Dict],
        keywords: Optional[List[str]] = None,
        location: Optional[str] = None,
        job_types: Optional[List[str]] = None,
        max_age_days: Optional[int] = None,
        min_match_score: Optional[float] = None,
        required_skills: Optional[List[str]] = None,
        excluded_companies: Optional[List[str]] = None,
        language: Optional[str] = None
    ) -> List[Dict]:
        """Filter jobs based on criteria.

        Args:
            jobs: List of job dictionaries
            keywords: Required keywords in title/description
            location: Location filter
            job_types: List of acceptable job types
            max_age_days: Maximum age in days
            min_match_score: Minimum match score (if present)
            required_skills: Must have at least one of these skills
            excluded_companies: Companies to exclude
            language: Preferred language ('en', 'fr', or None for both)

        Returns:
            Filtered list of jobs
        """
        filtered = jobs

        # Apply each filter
        if keywords:
            filtered = self._filter_by_keywords(filtered, keywords)

        if location:
            filtered = self._filter_by_location(filtered, location)

        if job_types:
            filtered = self._filter_by_job_type(filtered, job_types)

        if max_age_days is not None:
            filtered = self._filter_by_age(filtered, max_age_days)

        if min_match_score is not None:
            filtered = self._filter_by_match_score(filtered, min_match_score)

        if required_skills:
            filtered = self._filter_by_skills(filtered, required_skills)

        if excluded_companies:
            filtered = self._filter_by_excluded_companies(filtered, excluded_companies)

        if language:
            filtered = self._filter_by_language(filtered, language)

        return filtered

    def _filter_by_keywords(self, jobs: List[Dict], keywords: List[str]) -> List[Dict]:
        """Filter jobs that contain any of the keywords.

        Args:
            jobs: List of jobs
            keywords: Keywords to search for

        Returns:
            Filtered jobs
        """
        if not keywords:
            return jobs

        filtered = []
        keywords_lower = [kw.lower() for kw in keywords]

        for job in jobs:
            # Search in title and description
            text = f"{job.get('job_title', '')} {job.get('description', '')}".lower()

            # Check if any keyword is present
            if any(keyword in text for keyword in keywords_lower):
                filtered.append(job)

        return filtered

    def _filter_by_location(self, jobs: List[Dict], location: str) -> List[Dict]:
        """Filter jobs by location.

        Args:
            jobs: List of jobs
            location: Location to match

        Returns:
            Filtered jobs
        """
        if not location:
            return jobs

        filtered = []
        location_lower = location.lower()

        for job in jobs:
            job_location = job.get('location', '').lower()

            # Match exact or partial location
            if location_lower in job_location or job_location in location_lower:
                filtered.append(job)
            # Also include remote jobs
            elif 'remote' in location_lower or 'remote' in job_location:
                filtered.append(job)

        return filtered

    def _filter_by_job_type(self, jobs: List[Dict], job_types: List[str]) -> List[Dict]:
        """Filter jobs by type.

        Args:
            jobs: List of jobs
            job_types: Acceptable job types

        Returns:
            Filtered jobs
        """
        if not job_types:
            return jobs

        filtered = []
        job_types_lower = [jt.lower() for jt in job_types]

        for job in jobs:
            job_type = job.get('job_type', '').lower()

            if any(jt in job_type or job_type in jt for jt in job_types_lower):
                filtered.append(job)

        return filtered

    def _filter_by_age(self, jobs: List[Dict], max_age_days: int) -> List[Dict]:
        """Filter jobs by posting age.

        Args:
            jobs: List of jobs
            max_age_days: Maximum age in days

        Returns:
            Filtered jobs
        """
        if max_age_days is None:
            return jobs

        filtered = []
        cutoff_date = datetime.now() - timedelta(days=max_age_days)

        for job in jobs:
            posting_date = job.get('posting_date')

            if posting_date and isinstance(posting_date, datetime):
                if posting_date >= cutoff_date:
                    filtered.append(job)
            else:
                # Include if we don't know the date
                filtered.append(job)

        return filtered

    def _filter_by_match_score(self, jobs: List[Dict], min_score: float) -> List[Dict]:
        """Filter jobs by minimum match score.

        Args:
            jobs: List of jobs
            min_score: Minimum score threshold

        Returns:
            Filtered jobs
        """
        if min_score is None:
            return jobs

        filtered = []

        for job in jobs:
            match_score = job.get('match_score', 0)

            if match_score >= min_score:
                filtered.append(job)

        return filtered

    def _filter_by_skills(self, jobs: List[Dict], required_skills: List[str]) -> List[Dict]:
        """Filter jobs that have at least one required skill.

        Args:
            jobs: List of jobs
            required_skills: Required skills

        Returns:
            Filtered jobs
        """
        if not required_skills:
            return jobs

        filtered = []
        required_lower = [skill.lower() for skill in required_skills]

        for job in jobs:
            job_skills = job.get('required_skills', [])
            job_skills_lower = [skill.lower() for skill in job_skills]

            # Check if job has at least one required skill
            if any(req_skill in job_skills_lower for req_skill in required_lower):
                filtered.append(job)

        return filtered

    def _filter_by_excluded_companies(self, jobs: List[Dict], excluded: List[str]) -> List[Dict]:
        """Filter out jobs from excluded companies.

        Args:
            jobs: List of jobs
            excluded: Company names to exclude

        Returns:
            Filtered jobs
        """
        if not excluded:
            return jobs

        filtered = []
        excluded_lower = [company.lower() for company in excluded]

        for job in jobs:
            company = job.get('company_name', '').lower()

            # Exclude if company matches
            if not any(exc in company for exc in excluded_lower):
                filtered.append(job)

        return filtered

    def _filter_by_language(self, jobs: List[Dict], language: str) -> List[Dict]:
        """Filter jobs by language.

        Args:
            jobs: List of jobs
            language: Preferred language ('en' or 'fr')

        Returns:
            Filtered jobs
        """
        if not language:
            return jobs

        filtered = []

        for job in jobs:
            job_language = job.get('language', 'en')

            if job_language == language:
                filtered.append(job)

        return filtered


# Global filter engine instance
filter_engine = FilterEngine()
