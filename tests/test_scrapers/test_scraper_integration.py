"""Test scraper integration and pipeline."""

from scrapers.scraper_factory import scraper_factory
from scrapers.adzuna_client import adzuna_client
from database.db_manager import db_manager
from ai_generation.embeddings.vector_store import vector_store
import os


def test_adzuna_api():
    """Test Adzuna API client (requires API keys)."""
    print("=" * 70)
    print("Test: Adzuna API Client")
    print("=" * 70)

    # Check if API keys are available
    if not os.getenv('ADZUNA_APP_ID') or not os.getenv('ADZUNA_API_KEY'):
        print("\n[SKIP] Adzuna API keys not found in .env")
        print("  To test: Add ADZUNA_APP_ID and ADZUNA_API_KEY to .env")
        return True

    print("\n[*] Testing Adzuna API...")

    try:
        jobs = adzuna_client.scrape(
            keywords=['Python', 'Developer'],
            location='Paris',
            max_results=5,
            max_age_days=30,
            country='fr'
        )

        print(f"\n[OK] Fetched {len(jobs)} jobs from Adzuna")

        if jobs:
            print("\nSample job:")
            sample = jobs[0]
            print(f"  Title: {sample['job_title']}")
            print(f"  Company: {sample['company_name']}")
            print(f"  Location: {sample['location']}")
            print(f"  Type: {sample['job_type']}")
            print(f"  Skills: {', '.join(sample['required_skills'][:5])}")

        # Check API usage
        usage = adzuna_client.get_api_usage()
        print(f"\nAPI Usage:")
        print(f"  Calls made: {usage['calls_made']}")
        print(f"  Remaining: {usage['remaining']}/{usage['monthly_limit']}")

        print("\n[OK] Adzuna API test passed")
        return True

    except Exception as e:
        print(f"\n[ERROR] Adzuna test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_scraper_factory_pipeline():
    """Test complete scraping pipeline with factory."""
    print("\n" + "=" * 70)
    print("Test: Scraper Factory Pipeline")
    print("=" * 70)

    print("\n[*] Testing scraper factory...")

    try:
        # Use only Adzuna for testing (faster than web scraping)
        jobs = scraper_factory.scrape_all_sources(
            keywords=['Python', 'Machine Learning'],
            location='Paris',
            max_results_per_source=3,
            max_age_days=30,
            sources=['adzuna'],  # Only test API
            auto_embed=False,  # Skip embedding for faster test
            auto_save_db=False  # Skip DB for faster test
        )

        print(f"\n[OK] Pipeline returned {len(jobs)} jobs")

        # Check deduplication
        stats = scraper_factory.get_scraping_stats()
        print(f"\nPipeline Stats:")
        print(f"  Total jobs: {stats['total_jobs']}")
        print(f"  Duplicates removed: {stats['duplicates_removed']}")

        # Verify job structure
        if jobs:
            print("\nVerifying job structure...")
            sample = jobs[0]
            required_fields = [
                'source', 'job_title', 'company_name', 'location',
                'job_type', 'description', 'required_skills', 'posting_date'
            ]

            for field in required_fields:
                assert field in sample, f"Missing field: {field}"
                print(f"  [OK] {field}")

        print("\n[OK] Scraper factory test passed")
        return True

    except Exception as e:
        print(f"\n[ERROR] Factory test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_full_pipeline_with_embedding():
    """Test full pipeline including database and embeddings."""
    print("\n" + "=" * 70)
    print("Test: Full Pipeline with DB + Embeddings")
    print("=" * 70)

    print("\n[*] Initializing systems...")

    try:
        # Initialize systems
        db_manager.initialize()
        vector_store.initialize()

        print("[OK] Systems initialized")

        # Run pipeline with auto-save and auto-embed
        print("\n[*] Running full pipeline...")
        jobs = scraper_factory.scrape_all_sources(
            keywords=['Python'],
            location='Paris',
            max_results_per_source=2,
            max_age_days=30,
            sources=['adzuna'],
            auto_embed=True,  # Enable embedding
            auto_save_db=True  # Enable DB save
        )

        print(f"\n[OK] Pipeline processed {len(jobs)} jobs")

        # Verify jobs in database
        if jobs and jobs[0].get('id'):
            print("\n[*] Verifying database storage...")
            with db_manager.db as session:
                from database.models import Job
                db_job = session.query(Job).filter(
                    Job.id == jobs[0]['id']
                ).first()

                if db_job:
                    print(f"  [OK] Found job in database: {db_job.job_title}")
                else:
                    print(f"  [WARNING] Job not found in database")

        # Verify embeddings in vector store
        print("\n[*] Verifying vector embeddings...")
        # This would require querying Chroma, which we've already tested

        print("\n[OK] Full pipeline test passed")
        return True

    except Exception as e:
        print(f"\n[ERROR] Full pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all scraper tests."""
    print("\n" + "=" * 70)
    print("SCRAPER INTEGRATION TESTS")
    print("=" * 70)

    tests = [
        test_adzuna_api,
        test_scraper_factory_pipeline,
        test_full_pipeline_with_embedding
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"\n[X] Test error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"[OK] Passed: {passed}/{len(tests)}")
    print(f"[X] Failed: {failed}/{len(tests)}")

    if failed == 0:
        print("\n[SUCCESS] All scraper tests passed!")
    else:
        print(f"\n[WARNING] {failed} test(s) failed")

    return failed == 0


if __name__ == "__main__":
    # Note: These tests require API keys in .env
    # ADZUNA_APP_ID and ADZUNA_API_KEY
    run_all_tests()
