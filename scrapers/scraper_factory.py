"""Factory for managing multiple job scrapers and automatic embedding."""

from typing import List, Dict, Optional
from datetime import datetime
from scrapers.welcome_scraper import WelcomeToJungleScraper
from scrapers.adzuna_client import AdzunaClient
from database.db_manager import db_manager
from ai_generation.embeddings.vector_store import vector_store


class ScraperFactory:
    """Factory to manage multiple scrapers and coordinate job collection."""

    def __init__(self):
        """Initialize scraper factory."""
        self.scrapers = {
            'welcome_to_jungle': WelcomeToJungleScraper(),
            'adzuna': AdzunaClient()
        }
        self.all_jobs = []
        self.duplicates_removed = 0

    def scrape_all_sources(
        self,
        keywords: List[str],
        location: Optional[str] = None,
        job_type: Optional[str] = None,
        max_results_per_source: int = 25,
        max_age_days: int = 7,
        sources: Optional[List[str]] = None,
        auto_embed: bool = True,
        auto_save_db: bool = True
    ) -> List[Dict]:
        """Scrape jobs from all specified sources.

        Args:
            keywords: List of keywords to search for
            location: Location filter
            job_type: Type of job filter
            max_results_per_source: Maximum results per source
            max_age_days: Maximum age of postings in days
            sources: List of source names to use (None = all)
            auto_embed: Automatically generate embeddings
            auto_save_db: Automatically save to database

        Returns:
            List of all scraped jobs (deduplicated)
        """
        print("\n" + "=" * 70)
        print("JOB SCRAPING PIPELINE")
        print("=" * 70)
        print(f"Keywords: {', '.join(keywords)}")
        print(f"Sources: {sources or 'All available'}")
        print(f"Max per source: {max_results_per_source}")
        print(f"Auto-embed: {auto_embed}")
        print(f"Auto-save: {auto_save_db}")

        # Determine which scrapers to use
        sources_to_use = sources or list(self.scrapers.keys())
        all_jobs = []

        # Scrape from each source
        for source_name in sources_to_use:
            if source_name not in self.scrapers:
                print(f"\n[WARNING] Unknown source: {source_name}")
                continue

            scraper = self.scrapers[source_name]

            print(f"\n--- Source: {source_name.upper()} ---")

            try:
                jobs = scraper.scrape(
                    keywords=keywords,
                    location=location,
                    job_type=job_type,
                    max_results=max_results_per_source,
                    max_age_days=max_age_days
                )

                all_jobs.extend(jobs)
                print(f"✓ {len(jobs)} jobs from {source_name}")

            except Exception as e:
                print(f"✗ Error with {source_name}: {e}")
                continue

        print(f"\n--- COLLECTED {len(all_jobs)} TOTAL JOBS ---")

        # Deduplicate
        print("\n[DEDUP] Removing duplicates...")
        deduplicated_jobs = self._deduplicate_jobs(all_jobs)
        self.duplicates_removed = len(all_jobs) - len(deduplicated_jobs)
        print(f"  Removed {self.duplicates_removed} duplicates")
        print(f"  Final count: {len(deduplicated_jobs)} unique jobs")

        self.all_jobs = deduplicated_jobs

        # Auto-save to database
        if auto_save_db and deduplicated_jobs:
            print("\n[DB] Saving jobs to database...")
            saved_count = self._save_jobs_to_db(deduplicated_jobs)
            print(f"  Saved {saved_count} jobs to database")

        # Auto-embed jobs
        if auto_embed and deduplicated_jobs:
            print("\n[EMBED] Generating embeddings...")
            embedded_count = self._embed_jobs(deduplicated_jobs)
            print(f"  Embedded {embedded_count} jobs in vector store")

        print("\n" + "=" * 70)
        print(f"PIPELINE COMPLETE: {len(deduplicated_jobs)} jobs ready")
        print("=" * 70)

        return deduplicated_jobs

    def _deduplicate_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """Remove duplicate jobs based on title and company.

        Args:
            jobs: List of jobs to deduplicate

        Returns:
            Deduplicated list of jobs
        """
        seen = set()
        unique_jobs = []

        for job in jobs:
            # Create a key from normalized title and company
            key = (
                job['job_title'].lower().strip(),
                job['company_name'].lower().strip()
            )

            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)

        return unique_jobs

    def _save_jobs_to_db(self, jobs: List[Dict]) -> int:
        """Save jobs to PostgreSQL database.

        Args:
            jobs: List of jobs to save

        Returns:
            Number of jobs saved
        """
        saved_count = 0

        try:
            db_manager.initialize()

            for job in jobs:
                try:
                    job_id = db_manager.create_job(job)
                    if job_id:
                        # Add the database ID to the job dict
                        job['id'] = job_id
                        saved_count += 1
                except Exception as e:
                    print(f"    Error saving job '{job['job_title']}': {e}")
                    continue

        except Exception as e:
            print(f"  [ERROR] Database error: {e}")

        return saved_count

    def _embed_jobs(self, jobs: List[Dict]) -> int:
        """Generate embeddings for jobs and store in vector database.

        Args:
            jobs: List of jobs to embed

        Returns:
            Number of jobs embedded
        """
        embedded_count = 0

        try:
            vector_store.initialize()

            for job in jobs:
                try:
                    # Use job database ID if available, otherwise create a temp ID
                    job_id = job.get('id', f"temp_{hash(job['job_title'] + job['company_name'])}")

                    # Add to vector store
                    vector_store.add_job(str(job_id), job)
                    embedded_count += 1

                except Exception as e:
                    print(f"    Error embedding job '{job['job_title']}': {e}")
                    continue

        except Exception as e:
            print(f"  [ERROR] Embedding error: {e}")

        return embedded_count

    def get_scraper(self, source_name: str):
        """Get a specific scraper by name.

        Args:
            source_name: Name of the scraper

        Returns:
            Scraper instance or None
        """
        return self.scrapers.get(source_name)

    def get_scraping_stats(self) -> Dict:
        """Get statistics from all scrapers.

        Returns:
            Dictionary with scraping statistics
        """
        stats = {
            'total_jobs': len(self.all_jobs),
            'duplicates_removed': self.duplicates_removed,
            'by_source': {}
        }

        for name, scraper in self.scrapers.items():
            scraper_stats = scraper.get_scraping_stats()
            stats['by_source'][name] = scraper_stats

        return stats


# Global instance
scraper_factory = ScraperFactory()
