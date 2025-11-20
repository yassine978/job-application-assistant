"""Test RAG-based job ranking."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from processing.rag_ranker import rag_ranker
from processing.filter_engine import filter_engine
from processing.parser import job_parser
from database.db_manager import db_manager
from ai_generation.embeddings.vector_store import vector_store
import uuid
from datetime import datetime, timedelta


def test_job_parser():
    """Test job parsing and normalization."""
    print("=" * 70)
    print("Test 1: Job Parser")
    print("=" * 70)

    raw_job = {
        'source': 'test',
        'job_title': '  Senior  Python   Developer  ',
        'company_name': 'Tech Corp',
        'location': 'Ile-de-France',
        'job_type': 'CDI',
        'description': '<p>Looking for Python developer</p>  Extra whitespace  ',
        'required_skills': ['python', 'JavaScript', 'react', 'PostgreSQL'],
        'posting_date': '2025-01-15',
        'application_url': 'https://example.com/apply',
        'salary_range': '€50k-70k',
        'language': 'fr'
    }

    parsed = job_parser.parse_job(raw_job)

    print("\n[*] Parsed Job:")
    print(f"  Title: {parsed['job_title']}")
    print(f"  Company: {parsed['company_name']}")
    print(f"  Location: {parsed['location']}")
    print(f"  Job Type: {parsed['job_type']}")
    print(f"  Description: {parsed['description'][:50]}...")
    print(f"  Skills: {parsed['required_skills']}")

    # Assertions
    assert parsed['job_title'] == 'Senior Python Developer', "Should clean title"
    assert parsed['location'] == 'Paris', "Should normalize Ile-de-France to Paris"
    assert parsed['job_type'] == 'Full-time', "Should normalize CDI to Full-time"
    assert 'JavaScript' in parsed['required_skills'], "Should normalize JS"
    assert 'PostgreSQL' in parsed['required_skills'], "Should normalize PostgreSQL"
    assert '<p>' not in parsed['description'], "Should remove HTML"

    print("\n[OK] Job parser test passed")
    return True


def test_filter_engine():
    """Test job filtering."""
    print("\n" + "=" * 70)
    print("Test 2: Filter Engine")
    print("=" * 70)

    # Create test jobs
    jobs = [
        {
            'job_title': 'Python Developer',
            'company_name': 'Tech Corp',
            'location': 'Paris',
            'job_type': 'Full-time',
            'required_skills': ['Python', 'Django'],
            'posting_date': datetime.now() - timedelta(days=2),
            'language': 'en'
        },
        {
            'job_title': 'Machine Learning Engineer',
            'company_name': 'AI Startup',
            'location': 'Remote',
            'job_type': 'Full-time',
            'description': 'Looking for Python and TensorFlow expertise',
            'required_skills': ['Python', 'TensorFlow'],
            'posting_date': datetime.now() - timedelta(days=15),
            'language': 'en'
        },
        {
            'job_title': 'Frontend Developer',
            'company_name': 'Design Agency',
            'location': 'Lyon',
            'job_type': 'Contract',
            'required_skills': ['React', 'JavaScript'],
            'posting_date': datetime.now() - timedelta(days=5),
            'language': 'fr'
        }
    ]

    print(f"\n[*] Starting with {len(jobs)} jobs")

    # Test 1: Filter by keywords
    filtered = filter_engine.filter_jobs(jobs, keywords=['Python'])
    print(f"  After keyword filter (Python): {len(filtered)} jobs")
    assert len(filtered) == 2, "Should find 2 Python jobs"

    # Test 2: Filter by location (includes remote jobs)
    filtered = filter_engine.filter_jobs(jobs, location='Paris')
    print(f"  After location filter (Paris): {len(filtered)} jobs")
    assert len(filtered) == 2, "Should find 1 Paris job + 1 Remote job"

    # Test 3: Filter by job type
    filtered = filter_engine.filter_jobs(jobs, job_types=['Full-time'])
    print(f"  After job type filter (Full-time): {len(filtered)} jobs")
    assert len(filtered) == 2, "Should find 2 full-time jobs"

    # Test 4: Filter by age
    filtered = filter_engine.filter_jobs(jobs, max_age_days=7)
    print(f"  After age filter (7 days): {len(filtered)} jobs")
    assert len(filtered) == 2, "Should find 2 jobs within 7 days"

    # Test 5: Filter by skills
    filtered = filter_engine.filter_jobs(jobs, required_skills=['TensorFlow'])
    print(f"  After skill filter (TensorFlow): {len(filtered)} jobs")
    assert len(filtered) == 1, "Should find 1 job with TensorFlow"

    # Test 6: Combined filters
    filtered = filter_engine.filter_jobs(
        jobs,
        keywords=['Python'],
        job_types=['Full-time'],
        max_age_days=7
    )
    print(f"  After combined filters: {len(filtered)} jobs")
    assert len(filtered) == 1, "Should find 1 job matching all criteria"

    print("\n[OK] Filter engine test passed")
    return True


def test_rag_ranking():
    """Test RAG-based ranking."""
    print("\n" + "=" * 70)
    print("Test 3: RAG Ranking")
    print("=" * 70)

    try:
        # Initialize systems
        print("\n[*] Initializing systems...")
        db_manager.initialize()
        vector_store.initialize()
        rag_ranker.initialize()

        # Create test user with unique email
        print("[*] Creating test user...")
        user_id = str(uuid.uuid4())
        test_email = f"rag_test_{user_id[:8]}@test.com"

        user_data = {
            'email': test_email,
            'password_hash': 'hashed',
            'full_name': 'Test User',
            'location_preference': 'Paris',
            'preferences': {
                'preferred_job_types': ['Full-time', 'Internship']
            }
        }

        with db_manager.db as session:
            from database.models import User
            user = User(id=uuid.UUID(user_id), **user_data)
            session.add(user)
            session.commit()

        print(f"  User created: {user_id}")

        # Create profile
        print("[*] Creating profile...")
        profile_data = {
            'skills': ['Python', 'Machine Learning', 'TensorFlow'],
            'experience': [{
                'title': 'ML Engineer',
                'company': 'AI Corp',
                'duration': '2 years'
            }],
            'education': {
                'degree': 'Master',
                'field': 'Computer Science'
            },
            'languages': ['English', 'French']
        }

        profile_id = db_manager.create_profile(user_id, profile_data)

        # Embed profile
        vector_store.add_profile(user_id, profile_data)
        print(f"  Profile embedded: {profile_id}")

        # Create test jobs
        print("[*] Creating test jobs...")
        jobs = [
            {
                'source': 'test',
                'job_title': 'Senior Machine Learning Engineer',
                'company_name': 'AI Startup',
                'location': 'Paris',
                'job_type': 'Full-time',
                'description': 'Looking for ML engineer with Python and TensorFlow experience',
                'required_skills': ['Python', 'TensorFlow', 'Machine Learning'],
                'posting_date': datetime.now() - timedelta(days=2),
                'application_url': 'https://example.com/ml',
                'language': 'en'
            },
            {
                'source': 'test',
                'job_title': 'Frontend Developer',
                'company_name': 'Design Agency',
                'location': 'Lyon',
                'job_type': 'Contract',
                'description': 'Need React developer for web app',
                'required_skills': ['React', 'JavaScript', 'CSS'],
                'posting_date': datetime.now() - timedelta(days=10),
                'application_url': 'https://example.com/frontend',
                'language': 'fr'
            },
            {
                'source': 'test',
                'job_title': 'Python Developer',
                'company_name': 'Tech Corp',
                'location': 'Remote',
                'job_type': 'Full-time',
                'description': 'Python backend developer needed',
                'required_skills': ['Python', 'Django', 'PostgreSQL'],
                'posting_date': datetime.now() - timedelta(days=5),
                'application_url': 'https://example.com/python',
                'language': 'en'
            }
        ]

        # Rank jobs
        print(f"[*] Ranking {len(jobs)} jobs...")
        ranked_jobs = rag_ranker.rank_jobs(user_id, jobs)

        print(f"\n[*] Ranked Jobs:")
        for i, job in enumerate(ranked_jobs, 1):
            score = job['match_score']
            breakdown = job['match_score_breakdown']
            print(f"\n  {i}. {job['job_title']} at {job['company_name']}")
            print(f"     Match Score: {score:.1f}")
            print(f"     Breakdown:")
            for key, value in breakdown.items():
                if key != 'total':
                    print(f"       - {key}: {value}")

        # Assertions
        assert len(ranked_jobs) == 3, "Should rank all jobs"
        assert ranked_jobs[0]['match_score'] > 0, "Top job should have positive score"
        assert ranked_jobs[0]['match_score'] >= ranked_jobs[1]['match_score'], "Should be sorted by score"

        # The ML job should rank highest (best match to profile)
        top_job = ranked_jobs[0]
        assert 'Machine Learning' in top_job['job_title'], "ML job should rank first"

        print("\n[OK] RAG ranking test passed")
        return True

    except Exception as e:
        print(f"\n[ERROR] RAG ranking test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all processing tests."""
    print("\n" + "=" * 70)
    print("RAG RANKING TEST SUITE")
    print("=" * 70)

    tests = [
        test_job_parser,
        test_filter_engine,
        test_rag_ranking
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
        print("\n[SUCCESS] All RAG ranking tests passed!")
    else:
        print(f"\n[WARNING] {failed} test(s) failed")

    return failed == 0


if __name__ == "__main__":
    run_all_tests()
