"""Base scraper class for job scraping."""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime
import time


class BaseScraper(ABC):
    """Abstract base class for job scrapers."""

    def __init__(self, source_name: str):
        """Initialize the scraper.

        Args:
            source_name: Name of the job source (e.g., 'welcome_to_jungle', 'adzuna')
        """
        self.source_name = source_name
        self.scraped_jobs = []
        self.errors = []
        self.start_time = None
        self.end_time = None

    @abstractmethod
    def scrape(
        self,
        keywords: List[str],
        location: Optional[str] = None,
        job_type: Optional[str] = None,
        max_results: int = 50,
        max_age_days: int = 7
    ) -> List[Dict]:
        """Scrape jobs from the source.

        Args:
            keywords: List of keywords to search for
            location: Location filter (e.g., 'Paris', 'Remote')
            job_type: Type of job (e.g., 'Internship', 'Full-time')
            max_results: Maximum number of results to return
            max_age_days: Maximum age of postings in days

        Returns:
            List of job dictionaries with standardized schema
        """
        pass

    @abstractmethod
    def _parse_job(self, raw_job: any) -> Optional[Dict]:
        """Parse a raw job posting into standardized format.

        Args:
            raw_job: Raw job data from source

        Returns:
            Standardized job dictionary or None if parsing fails
        """
        pass

    def _standardize_job(
        self,
        title: str,
        company: str,
        location: Optional[str] = None,
        job_type: Optional[str] = None,
        description: Optional[str] = None,
        required_skills: Optional[List[str]] = None,
        posting_date: Optional[datetime] = None,
        application_url: Optional[str] = None,
        salary_range: Optional[str] = None,
        language: str = 'en'
    ) -> Dict:
        """Create a standardized job dictionary.

        Args:
            title: Job title
            company: Company name
            location: Job location
            job_type: Type of job
            description: Job description
            required_skills: List of required skills
            posting_date: Date when job was posted
            application_url: URL to apply
            salary_range: Salary information
            language: Job posting language

        Returns:
            Standardized job dictionary
        """
        return {
            'source': self.source_name,
            'job_title': title,
            'company_name': company,
            'location': location,
            'job_type': job_type,
            'description': description or '',
            'required_skills': required_skills or [],
            'posting_date': posting_date or datetime.now(),
            'application_url': application_url,
            'salary_range': salary_range,
            'language': language,
            'scraped_at': datetime.now()
        }

    def _extract_skills_from_text(self, text: str) -> List[str]:
        """Extract skills from job description text.

        Args:
            text: Job description or requirements text

        Returns:
            List of detected skills
        """
        if not text:
            return []

        # Common tech skills to look for
        common_skills = [
            'Python', 'JavaScript', 'TypeScript', 'Java', 'C++', 'C#', 'Ruby', 'Go', 'Rust', 'PHP',
            'React', 'Vue', 'Angular', 'Svelte', 'Next.js', 'Nuxt',
            'Node.js', 'Express', 'Django', 'Flask', 'FastAPI', 'Spring', 'Rails', 'Laravel',
            'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'SQLite', 'Cassandra',
            'Docker', 'Kubernetes', 'AWS', 'Azure', 'GCP', 'Terraform',
            'TensorFlow', 'PyTorch', 'scikit-learn', 'Keras', 'Pandas', 'NumPy',
            'Git', 'GitHub', 'GitLab', 'CI/CD', 'Jenkins',
            'HTML', 'CSS', 'Tailwind', 'Bootstrap', 'Sass',
            'GraphQL', 'REST', 'API', 'Microservices',
            'SQL', 'NoSQL',
            'Linux', 'Unix', 'Bash',
            'Agile', 'Scrum',
            'Machine Learning', 'Deep Learning', 'AI', 'Data Science',
            'Frontend', 'Backend', 'Full Stack', 'DevOps'
        ]

        text_lower = text.lower()
        found_skills = []

        for skill in common_skills:
            # Case-insensitive search with word boundaries
            if skill.lower() in text_lower:
                found_skills.append(skill)

        return list(set(found_skills))  # Remove duplicates

    def _add_error(self, error_msg: str, context: Optional[Dict] = None):
        """Log an error during scraping.

        Args:
            error_msg: Error message
            context: Optional context information
        """
        self.errors.append({
            'timestamp': datetime.now(),
            'message': error_msg,
            'context': context or {}
        })

    def get_scraping_stats(self) -> Dict:
        """Get statistics about the scraping session.

        Returns:
            Dictionary with scraping statistics
        """
        duration = None
        if self.start_time and self.end_time:
            duration = (self.end_time - self.start_time).total_seconds()

        return {
            'source': self.source_name,
            'jobs_scraped': len(self.scraped_jobs),
            'errors': len(self.errors),
            'duration_seconds': duration,
            'start_time': self.start_time,
            'end_time': self.end_time
        }

    def reset(self):
        """Reset scraper state for a new scraping session."""
        self.scraped_jobs = []
        self.errors = []
        self.start_time = None
        self.end_time = None

    def _delay(self, seconds: float = 2.0):
        """Add a delay between requests to be respectful.

        Args:
            seconds: Number of seconds to wait
        """
        time.sleep(seconds)
