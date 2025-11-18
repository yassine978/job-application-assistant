"""Demo: Complete RAG workflow from scraping to ranking."""

from scrapers.scraper_factory import scraper_factory
from processing.rag_ranker import rag_ranker
from processing.filter_engine import filter_engine
from database.db_manager import db_manager
from ai_generation.embeddings.vector_store import vector_store
import uuid
import os


def demo_complete_workflow():
    """Demonstrate complete RAG workflow."""
    print("\n" + "=" * 70)
    print("DEMO: COMPLETE RAG WORKFLOW")
    print("=" * 70)
    print("\nThis demo shows the entire pipeline:")
    print("  1. Scrape jobs from Adzuna")
    print("  2. Filter jobs by criteria")
    print("  3. Rank jobs using RAG")
    print("  4. Show top matches with explanations")

    if not os.getenv('ADZUNA_APP_ID'):
        print("\n[SKIP] Requires Adzuna API keys")
        print("  Add to .env: ADZUNA_APP_ID and ADZUNA_API_KEY")
        return

    try:
        # Step 1: Initialize systems
        print("\n" + "-" * 70)
        print("STEP 1: Initialize Systems")
        print("-" * 70)

        db_manager.initialize()
        vector_store.initialize()
        rag_ranker.initialize()
        print("[OK] All systems initialized")

        # Step 2: Create test user profile
        print("\n" + "-" * 70)
        print("STEP 2: Create User Profile")
        print("-" * 70)

        user_id = str(uuid.uuid4())
        test_email = f"demo_{user_id[:8]}@test.com"

        # Create user
        user_data = {
            'email': test_email,
            'password_hash': 'hashed',
            'full_name': 'Demo User',
            'location_preference': 'Paris',
            'preferences': {
                'preferred_job_types': ['Internship', 'Full-time']
            }
        }

        with db_manager.db as session:
            from database.models import User
            user = User(id=uuid.UUID(user_id), **user_data)
            session.add(user)
            session.commit()

        # Create profile
        profile_data = {
            'skills': ['Python', 'Machine Learning', 'TensorFlow', 'scikit-learn'],
            'experience': [{
                'title': 'ML Intern',
                'company': 'Tech Startup',
                'duration': '6 months'
            }],
            'education': {
                'degree': 'Master in AI',
                'field': 'Computer Science'
            },
            'languages': ['English', 'French']
        }

        profile_id = db_manager.create_profile(user_id, profile_data)
        vector_store.add_profile(user_id, profile_data)

        print(f"[OK] Created user: {user_data['full_name']}")
        print(f"  Location: {user_data['location_preference']}")
        print(f"  Skills: {', '.join(profile_data['skills'][:3])}...")
        print(f"  Looking for: {', '.join(user_data['preferences']['preferred_job_types'])}")

        # Step 3: Scrape jobs
        print("\n" + "-" * 70)
        print("STEP 3: Scrape Jobs")
        print("-" * 70)

        jobs = scraper_factory.scrape_all_sources(
            keywords=['Python', 'Machine Learning'],
            location='Paris',
            max_results_per_source=10,
            max_age_days=14,
            sources=['adzuna'],
            auto_embed=True,
            auto_save_db=True
        )

        print(f"[OK] Scraped {len(jobs)} jobs")

        # Step 4: Filter jobs
        print("\n" + "-" * 70)
        print("STEP 4: Filter Jobs")
        print("-" * 70)

        filtered_jobs = filter_engine.filter_jobs(
            jobs,
            job_types=['Full-time', 'Internship'],
            max_age_days=14,
            required_skills=['Python']
        )

        print(f"[OK] Filtered to {len(filtered_jobs)} jobs")
        print(f"  Criteria: Full-time or Internship, Python required, max 14 days old")

        # Step 5: Rank jobs with RAG
        print("\n" + "-" * 70)
        print("STEP 5: RAG-Enhanced Ranking")
        print("-" * 70)

        ranked_jobs = rag_ranker.rank_jobs(
            user_id=user_id,
            jobs=filtered_jobs,
            top_n=5
        )

        print(f"[OK] Ranked {len(ranked_jobs)} jobs")

        # Step 6: Display results
        print("\n" + "=" * 70)
        print("TOP 5 JOB MATCHES")
        print("=" * 70)

        for i, job in enumerate(ranked_jobs[:5], 1):
            print(f"\n{i}. {job['job_title']}")
            print(f"   Company: {job['company_name']}")
            print(f"   Location: {job['location']}")
            print(f"   Type: {job['job_type']}")
            print(f"   Match Score: {job['match_score']:.1f}/100")

            # Show breakdown
            breakdown = job['match_score_breakdown']
            print(f"   Why it matches:")
            if breakdown.get('semantic_similarity', 0) > 0.7:
                print(f"     - High semantic similarity ({breakdown['semantic_similarity']:.2f})")
            if breakdown.get('skill_match', 0) > 0.5:
                print(f"     - Good skill match ({breakdown['skill_match']:.2f})")
            if breakdown.get('location_match', 0) == 1.0:
                print(f"     - Perfect location match")
            if breakdown.get('job_type_match', 0) == 1.0:
                print(f"     - Matches preferred job type")

            print(f"   Skills: {', '.join(job['required_skills'][:5])}")
            if job.get('salary_range'):
                print(f"   Salary: {job['salary_range']}")
            print(f"   Apply: {job.get('application_url', 'N/A')}")

        print("\n" + "=" * 70)
        print("WORKFLOW COMPLETE")
        print("=" * 70)
        print(f"\n[SUCCESS] Found {len(ranked_jobs)} matching jobs")
        print(f"Top match: {ranked_jobs[0]['job_title']} (score: {ranked_jobs[0]['match_score']:.1f})")

    except Exception as e:
        print(f"\n[ERROR] Workflow failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    demo_complete_workflow()
