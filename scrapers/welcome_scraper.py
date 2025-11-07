"""Scraper for Welcome to the Jungle job postings."""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from scrapers.base_scraper import BaseScraper
import re
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import time


class WelcomeToJungleScraper(BaseScraper):
    """Scraper for Welcome to the Jungle (France-focused job board)."""

    BASE_URL = "https://www.welcometothejungle.com"
    SEARCH_URL = "https://www.welcometothejungle.com/en/jobs"

    def __init__(self):
        """Initialize Welcome to the Jungle scraper."""
        super().__init__('welcome_to_jungle')
        self.browser = None
        self.page = None

    def scrape(
        self,
        keywords: List[str],
        location: Optional[str] = None,
        job_type: Optional[str] = None,
        max_results: int = 50,
        max_age_days: int = 7
    ) -> List[Dict]:
        """Scrape jobs from Welcome to the Jungle.

        Args:
            keywords: List of keywords to search for
            location: Location filter
            job_type: Type of job filter
            max_results: Maximum number of results
            max_age_days: Maximum age of postings in days

        Returns:
            List of standardized job dictionaries
        """
        self.reset()
        self.start_time = datetime.now()

        print(f"\n[SCRAPER] Starting Welcome to the Jungle scrape")
        print(f"  Keywords: {', '.join(keywords)}")
        print(f"  Location: {location or 'Any'}")
        print(f"  Job Type: {job_type or 'Any'}")
        print(f"  Max Results: {max_results}")

        try:
            with sync_playwright() as playwright:
                # Launch browser in headless mode
                self.browser = playwright.chromium.launch(headless=True)
                self.page = self.browser.new_page()

                # Set user agent to avoid detection
                self.page.set_extra_http_headers({
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })

                # Build search query
                search_query = ' '.join(keywords)

                # Navigate to search page
                search_url = self._build_search_url(search_query, location)
                print(f"  Navigating to: {search_url}")

                self.page.goto(search_url, timeout=30000)
                self._delay(3)  # Wait for page to load

                # Extract jobs from current page
                jobs_extracted = self._extract_jobs_from_page(max_results, max_age_days)

                print(f"  Extracted {len(jobs_extracted)} jobs")

                self.browser.close()

        except Exception as e:
            error_msg = f"Error during scraping: {str(e)}"
            print(f"  [ERROR] {error_msg}")
            self._add_error(error_msg)
            if self.browser:
                self.browser.close()

        self.end_time = datetime.now()
        stats = self.get_scraping_stats()
        print(f"\n[SCRAPER] Complete: {stats['jobs_scraped']} jobs in {stats['duration_seconds']:.1f}s")

        return self.scraped_jobs

    def _build_search_url(self, query: str, location: Optional[str] = None) -> str:
        """Build the search URL for Welcome to the Jungle.

        Args:
            query: Search query
            location: Location filter

        Returns:
            Complete search URL
        """
        # Basic search URL
        url = f"{self.SEARCH_URL}?query={query.replace(' ', '+')}"

        # Add location if provided
        if location:
            # Common French cities mapping
            location_mapping = {
                'paris': 'paris',
                'lyon': 'lyon',
                'marseille': 'marseille',
                'toulouse': 'toulouse',
                'remote': 'remote',
                'france': 'france'
            }
            loc_key = location.lower()
            if loc_key in location_mapping:
                url += f"&refinementList[offices.city][]={location_mapping[loc_key]}"

        return url

    def _extract_jobs_from_page(self, max_results: int, max_age_days: int) -> List[Dict]:
        """Extract jobs from the current page.

        Args:
            max_results: Maximum number of jobs to extract
            max_age_days: Maximum age of postings in days

        Returns:
            List of extracted jobs
        """
        jobs = []

        try:
            # Wait for job cards to load
            self.page.wait_for_selector('[data-testid="jobs-search-item"]', timeout=10000)

            # Get all job card elements
            job_cards = self.page.query_selector_all('[data-testid="jobs-search-item"]')
            print(f"  Found {len(job_cards)} job cards on page")

            for i, card in enumerate(job_cards[:max_results]):
                if len(jobs) >= max_results:
                    break

                try:
                    job = self._parse_job(card)
                    if job:
                        # Check age filter
                        if self._is_within_age_limit(job['posting_date'], max_age_days):
                            jobs.append(job)
                            self.scraped_jobs.append(job)
                            print(f"    [{len(jobs)}] {job['job_title']} at {job['company_name']}")
                        else:
                            print(f"    [SKIP] Job too old: {job['job_title']}")

                    # Small delay between processing jobs
                    if i % 5 == 0:
                        self._delay(1)

                except Exception as e:
                    self._add_error(f"Error parsing job card {i}", {'error': str(e)})
                    continue

        except PlaywrightTimeout:
            self._add_error("Timeout waiting for job listings")
        except Exception as e:
            self._add_error(f"Error extracting jobs: {str(e)}")

        return jobs

    def _parse_job(self, job_card) -> Optional[Dict]:
        """Parse a job card element into standardized format.

        Args:
            job_card: Playwright element handle for job card

        Returns:
            Standardized job dictionary or None
        """
        try:
            # Extract title
            title_elem = job_card.query_selector('[data-testid="job-title"]')
            title = title_elem.inner_text().strip() if title_elem else None

            # Extract company name
            company_elem = job_card.query_selector('[data-testid="company-name"]')
            company = company_elem.inner_text().strip() if company_elem else None

            if not title or not company:
                return None

            # Extract location
            location_elem = job_card.query_selector('[data-testid="job-location"]')
            location = location_elem.inner_text().strip() if location_elem else None

            # Extract job URL
            link_elem = job_card.query_selector('a[href*="/jobs/"]')
            job_url = None
            if link_elem:
                href = link_elem.get_attribute('href')
                job_url = f"{self.BASE_URL}{href}" if href and href.startswith('/') else href

            # Extract contract type (if available)
            contract_elem = job_card.query_selector('[data-testid="contract-type"]')
            job_type = contract_elem.inner_text().strip() if contract_elem else None

            # Try to get more details by visiting job page (optional - can be slow)
            description = ""
            required_skills = []

            # For now, we'll set basic info and mark for later detail scraping
            # In production, you might want to scrape details separately

            # Create standardized job
            job = self._standardize_job(
                title=title,
                company=company,
                location=location,
                job_type=self._normalize_job_type(job_type),
                description=description,
                required_skills=required_skills,
                posting_date=datetime.now(),  # WTTJ doesn't show exact dates on cards
                application_url=job_url,
                salary_range=None,
                language='en'  # WTTJ is primarily in English/French
            )

            return job

        except Exception as e:
            self._add_error(f"Error parsing job card: {str(e)}")
            return None

    def _normalize_job_type(self, raw_type: Optional[str]) -> Optional[str]:
        """Normalize job type to standard values.

        Args:
            raw_type: Raw job type string

        Returns:
            Normalized job type
        """
        if not raw_type:
            return None

        raw_lower = raw_type.lower()

        # Map variations to standard types
        if any(term in raw_lower for term in ['intern', 'stage']):
            return 'Internship'
        elif any(term in raw_lower for term in ['full', 'cdi', 'permanent']):
            return 'Full-time'
        elif any(term in raw_lower for term in ['part', 'temps partiel']):
            return 'Part-time'
        elif any(term in raw_lower for term in ['contract', 'cdd', 'fixed']):
            return 'Contract'
        elif any(term in raw_lower for term in ['apprentice', 'alternance']):
            return 'Apprenticeship'
        else:
            return raw_type

    def _is_within_age_limit(self, posting_date: datetime, max_age_days: int) -> bool:
        """Check if job posting is within age limit.

        Args:
            posting_date: Date when job was posted
            max_age_days: Maximum age in days

        Returns:
            True if within limit, False otherwise
        """
        if not posting_date:
            return True  # Include if we don't know the date

        cutoff_date = datetime.now() - timedelta(days=max_age_days)
        return posting_date >= cutoff_date

    def scrape_job_details(self, job_url: str) -> Dict:
        """Scrape detailed information from a specific job page.

        Args:
            job_url: URL of the job posting

        Returns:
            Dictionary with detailed job information
        """
        details = {
            'description': '',
            'required_skills': [],
            'salary_range': None
        }

        try:
            if not self.page:
                return details

            self.page.goto(job_url, timeout=15000)
            self._delay(2)

            # Extract job description
            desc_elem = self.page.query_selector('[data-testid="job-description"]')
            if desc_elem:
                details['description'] = desc_elem.inner_text().strip()
                # Extract skills from description
                details['required_skills'] = self._extract_skills_from_text(details['description'])

            # Extract salary if available
            salary_elem = self.page.query_selector('[data-testid="salary-range"]')
            if salary_elem:
                details['salary_range'] = salary_elem.inner_text().strip()

        except Exception as e:
            self._add_error(f"Error scraping job details: {str(e)}", {'url': job_url})

        return details


# Global instance
welcome_scraper = WelcomeToJungleScraper()
