"""Client for Adzuna Job Search API."""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from scrapers.base_scraper import BaseScraper
import requests
import os
from dotenv import load_dotenv

load_dotenv()


class AdzunaClient(BaseScraper):
    """Client for Adzuna API (free tier: 5,000 calls/month)."""

    BASE_URL = "https://api.adzuna.com/v1/api/jobs"

    def __init__(self, app_id: Optional[str] = None, api_key: Optional[str] = None):
        """Initialize Adzuna client.

        Args:
            app_id: Adzuna App ID (from env if not provided)
            api_key: Adzuna API key (from env if not provided)
        """
        super().__init__('adzuna')
        self.app_id = app_id or os.getenv('ADZUNA_APP_ID')
        self.api_key = api_key or os.getenv('ADZUNA_API_KEY')
        self.calls_made = 0
        self.monthly_limit = 5000

    def scrape(
        self,
        keywords: List[str],
        location: Optional[str] = None,
        job_type: Optional[str] = None,
        max_results: int = 50,
        max_age_days: int = 7,
        country: str = 'fr'  # Default to France
    ) -> List[Dict]:
        """Fetch jobs from Adzuna API.

        Args:
            keywords: List of keywords to search for
            location: Location filter
            job_type: Type of job filter
            max_results: Maximum number of results
            max_age_days: Maximum age of postings in days
            country: Country code (fr, us, uk, etc.)

        Returns:
            List of standardized job dictionaries
        """
        self.reset()
        self.start_time = datetime.now()

        print(f"\n[API] Starting Adzuna API fetch")
        print(f"  Keywords: {', '.join(keywords)}")
        print(f"  Location: {location or 'Any'}")
        print(f"  Country: {country}")
        print(f"  Max Results: {max_results}")

        if not self.app_id or not self.api_key:
            error_msg = "Adzuna credentials not found. Set ADZUNA_APP_ID and ADZUNA_API_KEY in .env"
            print(f"  [ERROR] {error_msg}")
            self._add_error(error_msg)
            return []

        try:
            # Build search query
            search_query = ' '.join(keywords)

            # Calculate number of pages needed (Adzuna returns max 50 per page)
            results_per_page = min(50, max_results)
            num_pages = (max_results + results_per_page - 1) // results_per_page

            all_jobs = []

            for page in range(1, num_pages + 1):
                if len(all_jobs) >= max_results:
                    break

                print(f"  Fetching page {page}...")

                jobs_page = self._fetch_page(
                    query=search_query,
                    location=location,
                    country=country,
                    page=page,
                    results_per_page=results_per_page,
                    max_age_days=max_age_days
                )

                if not jobs_page:
                    break  # No more results

                all_jobs.extend(jobs_page)
                self._delay(0.5)  # Small delay between API calls

                # Stop if we got fewer results than requested (last page)
                if len(jobs_page) < results_per_page:
                    break

            print(f"  Fetched {len(all_jobs)} jobs from Adzuna")

        except Exception as e:
            error_msg = f"Error during API fetch: {str(e)}"
            print(f"  [ERROR] {error_msg}")
            self._add_error(error_msg)

        self.end_time = datetime.now()
        stats = self.get_scraping_stats()
        print(f"\n[API] Complete: {stats['jobs_scraped']} jobs in {stats['duration_seconds']:.1f}s")
        print(f"  API Calls Made: {self.calls_made}/{self.monthly_limit}")

        return self.scraped_jobs

    def _fetch_page(
        self,
        query: str,
        location: Optional[str],
        country: str,
        page: int,
        results_per_page: int,
        max_age_days: int
    ) -> List[Dict]:
        """Fetch a single page of results from Adzuna.

        Args:
            query: Search query
            location: Location filter
            country: Country code
            page: Page number (1-indexed)
            results_per_page: Number of results per page
            max_age_days: Maximum age of postings

        Returns:
            List of jobs from this page
        """
        jobs = []

        try:
            # Build API URL
            url = f"{self.BASE_URL}/{country}/search/{page}"

            # Build parameters
            params = {
                'app_id': self.app_id,
                'app_key': self.api_key,
                'what': query,
                'results_per_page': results_per_page,
                'content-type': 'application/json'
            }

            # Add location if provided
            if location:
                params['where'] = location

            # Add max age filter
            if max_age_days:
                params['max_days_old'] = max_age_days

            # Make request
            response = requests.get(url, params=params, timeout=10)
            self.calls_made += 1

            if response.status_code == 200:
                data = response.json()
                raw_jobs = data.get('results', [])

                for raw_job in raw_jobs:
                    job = self._parse_job(raw_job)
                    if job:
                        jobs.append(job)
                        self.scraped_jobs.append(job)

            elif response.status_code == 429:
                self._add_error("API rate limit exceeded")
            else:
                self._add_error(f"API error: {response.status_code}", {'response': response.text[:200]})

        except requests.Timeout:
            self._add_error("API request timeout")
        except Exception as e:
            self._add_error(f"Error fetching page {page}: {str(e)}")

        return jobs

    def _parse_job(self, raw_job: Dict) -> Optional[Dict]:
        """Parse raw Adzuna job data into standardized format.

        Args:
            raw_job: Raw job dictionary from Adzuna API

        Returns:
            Standardized job dictionary or None
        """
        try:
            # Extract basic fields
            title = raw_job.get('title', '').strip()
            company = raw_job.get('company', {}).get('display_name', '').strip()

            if not title or not company:
                return None

            # Extract location
            location_data = raw_job.get('location', {})
            location_parts = []
            if location_data.get('area'):
                location_parts.append(location_data['area'][0] if isinstance(location_data['area'], list) else location_data['area'])
            if location_data.get('display_name'):
                location_parts.append(location_data['display_name'])

            location = ', '.join(location_parts) if location_parts else None

            # Extract description
            description = raw_job.get('description', '').strip()

            # Extract skills from description
            required_skills = self._extract_skills_from_text(description)

            # Extract contract type
            contract_type = raw_job.get('contract_type')
            contract_time = raw_job.get('contract_time')
            job_type = self._determine_job_type(contract_type, contract_time)

            # Extract posting date
            created_date = raw_job.get('created')
            posting_date = None
            if created_date:
                try:
                    posting_date = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
                except:
                    posting_date = None

            # Extract URL
            application_url = raw_job.get('redirect_url')

            # Extract salary
            salary_min = raw_job.get('salary_min')
            salary_max = raw_job.get('salary_max')
            salary_range = None
            if salary_min and salary_max:
                salary_range = f"€{salary_min:,.0f} - €{salary_max:,.0f}"
            elif salary_min:
                salary_range = f"€{salary_min:,.0f}+"

            # Detect language (basic heuristic)
            language = self._detect_language(description, title)

            # Create standardized job
            job = self._standardize_job(
                title=title,
                company=company,
                location=location,
                job_type=job_type,
                description=description,
                required_skills=required_skills,
                posting_date=posting_date or datetime.now(),
                application_url=application_url,
                salary_range=salary_range,
                language=language
            )

            return job

        except Exception as e:
            self._add_error(f"Error parsing Adzuna job: {str(e)}", {'job_id': raw_job.get('id')})
            return None

    def _determine_job_type(
        self,
        contract_type: Optional[str],
        contract_time: Optional[str]
    ) -> Optional[str]:
        """Determine standardized job type from Adzuna contract fields.

        Args:
            contract_type: Contract type from Adzuna
            contract_time: Contract time from Adzuna

        Returns:
            Standardized job type
        """
        if not contract_type and not contract_time:
            return None

        combined = f"{contract_type or ''} {contract_time or ''}".lower()

        if 'permanent' in combined or 'full' in combined:
            return 'Full-time'
        elif 'part' in combined:
            return 'Part-time'
        elif 'contract' in combined:
            return 'Contract'
        elif 'intern' in combined:
            return 'Internship'
        else:
            return contract_type or contract_time

    def _detect_language(self, description: str, title: str) -> str:
        """Detect job posting language (simple heuristic).

        Args:
            description: Job description
            title: Job title

        Returns:
            Language code ('fr' or 'en')
        """
        text = f"{title} {description}".lower()

        # French indicators
        french_words = ['le ', 'la ', 'les ', 'des ', 'une ', 'nous ', 'vous ', 'sont', 'être']
        french_count = sum(1 for word in french_words if word in text)

        # English indicators
        english_words = ['the ', 'and ', 'are ', 'is ', 'we ', 'you ', 'our ', 'have']
        english_count = sum(1 for word in english_words if word in text)

        return 'fr' if french_count > english_count else 'en'

    def get_api_usage(self) -> Dict:
        """Get API usage statistics.

        Returns:
            Dictionary with usage info
        """
        return {
            'calls_made': self.calls_made,
            'monthly_limit': self.monthly_limit,
            'remaining': self.monthly_limit - self.calls_made,
            'usage_percentage': (self.calls_made / self.monthly_limit) * 100
        }


# Global instance
adzuna_client = AdzunaClient()
