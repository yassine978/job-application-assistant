"""Parser for job data normalization and cleaning."""

from typing import Dict, List, Optional
from datetime import datetime
import re


class JobParser:
    """Parse and normalize job data from various sources."""

    def __init__(self):
        """Initialize the job parser."""
        pass

    def parse_job(self, raw_job: Dict) -> Dict:
        """Parse and normalize a job posting.

        Args:
            raw_job: Raw job dictionary from scraper

        Returns:
            Normalized job dictionary
        """
        parsed = {
            'source': self._clean_text(raw_job.get('source', '')),
            'job_title': self._clean_text(raw_job.get('job_title', '')),
            'company_name': self._clean_text(raw_job.get('company_name', '')),
            'location': self._normalize_location(raw_job.get('location')),
            'job_type': self._normalize_job_type(raw_job.get('job_type')),
            'description': self._clean_description(raw_job.get('description', '')),
            'required_skills': self._normalize_skills(raw_job.get('required_skills', [])),
            'posting_date': self._parse_date(raw_job.get('posting_date')),
            'application_url': raw_job.get('application_url'),
            'salary_range': raw_job.get('salary_range'),
            'language': raw_job.get('language', 'en'),
            'scraped_at': raw_job.get('scraped_at', datetime.now())
        }

        return parsed

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text.

        Args:
            text: Text to clean

        Returns:
            Cleaned text
        """
        if not text:
            return ''

        # Remove extra whitespace
        text = ' '.join(text.split())

        # Remove special characters (keep basic punctuation)
        text = re.sub(r'[^\w\s\-.,!?()&/]', '', text)

        return text.strip()

    def _clean_description(self, description: str) -> str:
        """Clean job description.

        Args:
            description: Job description text

        Returns:
            Cleaned description
        """
        if not description:
            return ''

        # Remove HTML tags
        description = re.sub(r'<[^>]+>', '', description)

        # Remove extra whitespace
        description = ' '.join(description.split())

        # Remove URLs
        description = re.sub(r'http[s]?://\S+', '', description)

        # Limit length (keep first 2000 characters)
        if len(description) > 2000:
            description = description[:2000] + '...'

        return description.strip()

    def _normalize_location(self, location: Optional[str]) -> Optional[str]:
        """Normalize location string.

        Args:
            location: Location string

        Returns:
            Normalized location
        """
        if not location:
            return None

        # Clean and normalize
        location = self._clean_text(location)

        # Common location mappings
        location_map = {
            'ile-de-france': 'Paris',
            'idf': 'Paris',
            'remote': 'Remote',
            'télétravail': 'Remote',
            'full remote': 'Remote',
            '100% remote': 'Remote'
        }

        location_lower = location.lower()
        for key, value in location_map.items():
            if key in location_lower:
                return value

        return location

    def _normalize_job_type(self, job_type: Optional[str]) -> Optional[str]:
        """Normalize job type to standard values.

        Args:
            job_type: Raw job type

        Returns:
            Normalized job type
        """
        if not job_type:
            return None

        job_type_lower = job_type.lower()

        # Map to standard types
        if any(term in job_type_lower for term in ['full', 'cdi', 'permanent', 'temps plein']):
            return 'Full-time'
        elif any(term in job_type_lower for term in ['part', 'temps partiel']):
            return 'Part-time'
        elif any(term in job_type_lower for term in ['intern', 'stage', 'stagiaire']):
            return 'Internship'
        elif any(term in job_type_lower for term in ['contract', 'cdd', 'fixed', 'freelance']):
            return 'Contract'
        elif any(term in job_type_lower for term in ['apprentice', 'alternance', 'apprentissage']):
            return 'Apprenticeship'
        else:
            return job_type

    def _normalize_skills(self, skills: List[str]) -> List[str]:
        """Normalize and deduplicate skills list.

        Args:
            skills: List of skills

        Returns:
            Normalized skills list
        """
        if not skills:
            return []

        normalized = []
        seen = set()

        for skill in skills:
            # Clean the skill
            skill = self._clean_text(skill)
            if not skill:
                continue

            # Normalize case (title case for most, special cases)
            skill_lower = skill.lower()

            # Special case mappings
            special_cases = {
                'javascript': 'JavaScript',
                'typescript': 'TypeScript',
                'nodejs': 'Node.js',
                'nextjs': 'Next.js',
                'vuejs': 'Vue.js',
                'reactjs': 'React',
                'postgresql': 'PostgreSQL',
                'mongodb': 'MongoDB',
                'mysql': 'MySQL',
                'aws': 'AWS',
                'gcp': 'GCP',
                'tensorflow': 'TensorFlow',
                'pytorch': 'PyTorch',
                'scikit-learn': 'scikit-learn',
                'c++': 'C++',
                'c#': 'C#',
                'html': 'HTML',
                'css': 'CSS',
                'sql': 'SQL',
                'nosql': 'NoSQL',
                'rest': 'REST',
                'api': 'API',
                'graphql': 'GraphQL',
                'docker': 'Docker',
                'kubernetes': 'Kubernetes',
                'ci/cd': 'CI/CD',
                'ml': 'Machine Learning',
                'ai': 'AI'
            }

            normalized_skill = special_cases.get(skill_lower, skill.title())

            # Avoid duplicates (case-insensitive)
            if normalized_skill.lower() not in seen:
                normalized.append(normalized_skill)
                seen.add(normalized_skill.lower())

        return sorted(normalized)

    def _parse_date(self, date_value) -> Optional[datetime]:
        """Parse date from various formats.

        Args:
            date_value: Date value (string, datetime, etc.)

        Returns:
            Parsed datetime or None
        """
        if isinstance(date_value, datetime):
            return date_value

        if isinstance(date_value, str):
            # Try common date formats
            formats = [
                '%Y-%m-%d',
                '%Y-%m-%d %H:%M:%S',
                '%d/%m/%Y',
                '%m/%d/%Y'
            ]

            for fmt in formats:
                try:
                    return datetime.strptime(date_value, fmt)
                except ValueError:
                    continue

        # Return current time if parsing fails
        return datetime.now()


# Global parser instance
job_parser = JobParser()
