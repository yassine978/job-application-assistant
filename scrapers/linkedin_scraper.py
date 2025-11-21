"""Scraper for LinkedIn job postings (public listings only)."""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from scrapers.base_scraper import BaseScraper
import re
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import time


class LinkedInScraper(BaseScraper):
    """Scraper for LinkedIn public job postings (no authentication required)."""

    BASE_URL = "https://www.linkedin.com"
    JOBS_URL = "https://www.linkedin.com/jobs/search"

    def __init__(self):
        """Initialize LinkedIn scraper."""
        super().__init__('linkedin')
        self.browser = None
        self.page = None

    def scrape(
        self,
        keywords: List[str],
        location: Optional[str] = None,
        job_type: Optional[str] = None,
        max_results: int = 25,
        max_age_days: int = 7
    ) -> List[Dict]:
        """Scrape public job listings from LinkedIn.

        Note: LinkedIn limits public access to ~25 results without login.

        Args:
            keywords: List of keywords to search for
            location: Location filter
            job_type: Type of job filter
            max_results: Maximum number of results (capped at 25 for public access)
            max_age_days: Maximum age of postings in days

        Returns:
            List of standardized job dictionaries
        """
        self.reset()
        self.start_time = datetime.now()

        # LinkedIn public API limits
        max_results = min(max_results, 25)

        print(f"\n[SCRAPER] Starting LinkedIn scrape (public listings)")
        print(f"  Keywords: {', '.join(keywords)}")
        print(f"  Location: {location or 'Any'}")
        print(f"  Job Type: {job_type or 'Any'}")
        print(f"  Max Results: {max_results} (LinkedIn public limit)")

        try:
            with sync_playwright() as playwright:
                # Launch browser in headless mode
                self.browser = playwright.chromium.launch(headless=True)
                context = self.browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )
                self.page = context.new_page()

                # Build search query
                search_query = ' '.join(keywords)

                # Navigate to search page
                search_url = self._build_search_url(search_query, location, job_type)
                print(f"  Navigating to: {search_url}")

                self.page.goto(search_url, timeout=30000)
                self._delay(3)  # Wait for page to load

                # Extract jobs from page
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

    def _build_search_url(
        self,
        query: str,
        location: Optional[str] = None,
        job_type: Optional[str] = None
    ) -> str:
        """Build the search URL for LinkedIn jobs.

        Args:
            query: Search query
            location: Location filter
            job_type: Job type filter

        Returns:
            Complete search URL
        """
        # Basic search URL
        url = f"{self.JOBS_URL}?keywords={query.replace(' ', '%20')}"

        # Add location if provided
        if location:
            url += f"&location={location.replace(' ', '%20')}"

        # Add job type filter
        if job_type:
            # LinkedIn job type codes
            job_type_codes = {
                'full-time': 'F',
                'full time': 'F',
                'part-time': 'P',
                'part time': 'P',
                'internship': 'I',
                'contract': 'C',
                'temporary': 'T',
                'volunteer': 'V'
            }
            code = job_type_codes.get(job_type.lower())
            if code:
                url += f"&f_JT={code}"

        # Sort by date (most recent first)
        url += "&sortBy=DD"

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
            self.page.wait_for_selector('.jobs-search__results-list', timeout=10000)
            self._delay(2)

            # Scroll to load more jobs
            self._scroll_to_load_jobs()

            # Get all job card elements
            job_cards = self.page.query_selector_all('li.jobs-search-results__list-item')
            print(f"  Found {len(job_cards)} job cards on page")

            for i, card in enumerate(job_cards[:max_results]):
                if len(jobs) >= max_results:
                    break

                try:
                    job = self._parse_job_card(card)
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

    def _scroll_to_load_jobs(self):
        """Scroll page to trigger lazy loading of job cards."""
        try:
            for _ in range(3):
                self.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                self._delay(1)
        except Exception as e:
            print(f"  [WARNING] Scroll error: {e}")

    def _parse_job_card(self, job_card) -> Optional[Dict]:
        """Parse a job card element into standardized format.

        Args:
            job_card: Playwright element handle for job card

        Returns:
            Standardized job dictionary or None
        """
        try:
            # Extract title
            title_elem = job_card.query_selector('.job-card-list__title, .base-search-card__title')
            title = title_elem.inner_text().strip() if title_elem else None

            # Extract company name
            company_elem = job_card.query_selector('.job-card-container__company-name, .base-search-card__subtitle')
            company = company_elem.inner_text().strip() if company_elem else None

            if not title or not company:
                return None

            # Extract location
            location_elem = job_card.query_selector('.job-card-container__metadata-item, .job-search-card__location')
            location = location_elem.inner_text().strip() if location_elem else None

            # Extract job URL
            link_elem = job_card.query_selector('a.base-card__full-link')
            job_url = None
            if link_elem:
                job_url = link_elem.get_attribute('href')
                if job_url and not job_url.startswith('http'):
                    job_url = f"{self.BASE_URL}{job_url}"

            # Extract posting date
            date_elem = job_card.query_selector('time')
            posting_date = self._parse_date(date_elem.get_attribute('datetime') if date_elem else None)

            # Try to get job details by clicking and reading description
            description = ""
            required_skills = []
            salary_range = None

            # For now, we'll skip detailed scraping to avoid rate limits
            # In production, you could optionally scrape details for top matches

            # Create standardized job
            job = self._standardize_job(
                title=title,
                company=company,
                location=location,
                job_type=None,  # LinkedIn doesn't show type in card
                description=description,
                required_skills=required_skills,
                posting_date=posting_date,
                application_url=job_url,
                salary_range=salary_range,
                language='en'
            )

            return job

        except Exception as e:
            self._add_error(f"Error parsing job card: {str(e)}")
            return None

    def _parse_date(self, date_str: Optional[str]) -> datetime:
        """Parse LinkedIn date string to datetime.

        Args:
            date_str: Date string from LinkedIn (e.g., '2024-01-15')

        Returns:
            Datetime object
        """
        if not date_str:
            return datetime.now()

        try:
            # LinkedIn uses ISO format in datetime attribute
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except Exception:
            return datetime.now()

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

        Note: This method can be used for deep scraping but adds latency.

        Args:
            job_url: URL of the job posting

        Returns:
            Dictionary with detailed job information
        """
        details = {
            'description': '',
            'required_skills': [],
            'salary_range': None,
            'job_type': None
        }

        try:
            if not self.page:
                return details

            self.page.goto(job_url, timeout=15000)
            self._delay(2)

            # Extract job description
            desc_elem = self.page.query_selector('.show-more-less-html__markup, .description__text')
            if desc_elem:
                details['description'] = desc_elem.inner_text().strip()
                # Extract skills from description
                details['required_skills'] = self._extract_skills_from_text(details['description'])

            # Extract job criteria
            criteria_elems = self.page.query_selector_all('.description__job-criteria-item')
            for criterion in criteria_elems:
                try:
                    subheader = criterion.query_selector('.description__job-criteria-subheader')
                    text = criterion.query_selector('.description__job-criteria-text')

                    if subheader and text:
                        label = subheader.inner_text().strip().lower()
                        value = text.inner_text().strip()

                        if 'employment type' in label:
                            details['job_type'] = value
                        elif 'seniority' in label:
                            details['seniority'] = value

                except Exception:
                    continue

        except Exception as e:
            self._add_error(f"Error scraping job details: {str(e)}", {'url': job_url})

        return details


# Global instance
linkedin_scraper = LinkedInScraper()
