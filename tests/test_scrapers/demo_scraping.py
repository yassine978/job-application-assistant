"""Demo script for job scraping pipeline."""

from scrapers.scraper_factory import scraper_factory
from scrapers.adzuna_client import adzuna_client
import os


def demo_basic_scraping():
    """Demo: Basic job scraping from Adzuna."""
    print("\n" + "=" * 70)
    print("DEMO: Basic Job Scraping")
    print("=" * 70)

    # Check for API keys
    if not os.getenv('ADZUNA_APP_ID'):
        print("\n[INFO] To use Adzuna API:")
        print("  1. Sign up at https://developer.adzuna.com/")
        print("  2. Get your App ID and API Key")
        print("  3. Add to .env file:")
        print("     ADZUNA_APP_ID=your_app_id")
        print("     ADZUNA_API_KEY=your_api_key")
        return

    # Simple scraping example
    print("\nScraping Python jobs in Paris...")

    jobs = adzuna_client.scrape(
        keywords=['Python', 'Developer'],
        location='Paris',
        max_results=5,
        max_age_days=7,
        country='fr'
    )

    print(f"\nFound {len(jobs)} jobs:")
    for i, job in enumerate(jobs, 1):
        print(f"\n{i}. {job['job_title']}")
        print(f"   Company: {job['company_name']}")
        print(f"   Location: {job['location']}")
        print(f"   Type: {job['job_type']}")
        print(f"   Skills: {', '.join(job['required_skills'][:5])}")
        if job['salary_range']:
            print(f"   Salary: {job['salary_range']}")


def demo_multi_source_pipeline():
    """Demo: Multi-source scraping with deduplication."""
    print("\n" + "=" * 70)
    print("DEMO: Multi-Source Pipeline")
    print("=" * 70)

    if not os.getenv('ADZUNA_APP_ID'):
        print("\n[SKIP] Adzuna API keys required")
        return

    # Scrape from multiple sources
    print("\nScraping Machine Learning jobs...")

    jobs = scraper_factory.scrape_all_sources(
        keywords=['Machine Learning', 'AI'],
        location='Paris',
        max_results_per_source=5,
        max_age_days=14,
        sources=['adzuna'],  # Can add 'welcome_to_jungle' when ready
        auto_embed=False,
        auto_save_db=False
    )

    # Show statistics
    stats = scraper_factory.get_scraping_stats()

    print(f"\n" + "-" * 70)
    print("Pipeline Statistics:")
    print(f"  Total jobs collected: {stats['total_jobs']}")
    print(f"  Duplicates removed: {stats['duplicates_removed']}")

    for source, source_stats in stats['by_source'].items():
        print(f"\n  {source}:")
        print(f"    Jobs: {source_stats['jobs_scraped']}")
        print(f"    Errors: {source_stats['errors']}")
        if source_stats['duration_seconds']:
            print(f"    Duration: {source_stats['duration_seconds']:.1f}s")


def demo_full_pipeline():
    """Demo: Full pipeline with database and embeddings."""
    print("\n" + "=" * 70)
    print("DEMO: Full Pipeline (DB + Embeddings)")
    print("=" * 70)

    if not os.getenv('ADZUNA_APP_ID'):
        print("\n[SKIP] Adzuna API keys required")
        return

    print("\nRunning full pipeline...")
    print("  - Scraping jobs")
    print("  - Saving to PostgreSQL")
    print("  - Generating embeddings")
    print("  - Storing in Chroma vector DB")

    jobs = scraper_factory.scrape_all_sources(
        keywords=['Python', 'Backend'],
        location='Paris',
        max_results_per_source=3,
        max_age_days=7,
        sources=['adzuna'],
        auto_embed=True,  # Generate embeddings
        auto_save_db=True  # Save to database
    )

    print(f"\n[SUCCESS] Processed {len(jobs)} jobs")
    print("\nJobs are now:")
    print("  - Stored in PostgreSQL database")
    print("  - Embedded in Chroma vector store")
    print("  - Ready for RAG-powered matching!")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("JOB SCRAPING DEMOS")
    print("=" * 70)
    print("\nThese demos show how to use the job scraping pipeline.")
    print("\nNote: Adzuna API keys required (free tier: 5000 calls/month)")

    # Run demos
    demo_basic_scraping()
    demo_multi_source_pipeline()
    demo_full_pipeline()

    print("\n" + "=" * 70)
    print("DEMOS COMPLETE")
    print("=" * 70)
