"""Integration tests for complete workflows."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime
import uuid


def test_complete_workflow():
    """Test complete end-to-end workflow.

    This tests the entire pipeline:
    1. User registration
    2. Profile creation
    3. Project upload
    4. Job search (mocked)
    5. RAG ranking
    6. CV generation
    7. Export to CSV/Excel
    """
    print("=" * 70)
    print("Test: Complete Workflow Integration")
    print("=" * 70)

    try:
        # Step 1: User Registration
        print("\n[1/7] Testing user registration...")
        from dashboard.auth import auth_manager
        auth_manager.initialize()

        test_email = f"integration_test_{uuid.uuid4().hex[:8]}@example.com"
        reg_result = auth_manager.register_user(
            email=test_email,
            password="test_password_123",
            full_name="Integration Test User",
            location_preference="Paris"
        )

        assert reg_result['success'], f"Registration failed: {reg_result['message']}"
        user_id = reg_result['user_id']
        print(f"[OK] User registered: {user_id}")

        # Step 2: Profile Creation
        print("\n[2/7] Testing profile creation...")
        from database.db_manager import db_manager
        db_manager.initialize()

        profile_data = {
            'skills': ['Python', 'Machine Learning', 'TensorFlow', 'SQL'],
            'experience': [
                {
                    'title': 'ML Engineer',
                    'company': 'Tech Corp',
                    'duration': '2 years'
                }
            ],
            'education': {
                'degree': 'Master in CS',
                'institution': 'University',
                'year': 2022
            },
            'languages': ['English', 'French']
        }

        profile_id = db_manager.create_profile(user_id, profile_data)
        print(f"[OK] Profile created: {profile_id}")

        # Step 3: Project Upload & Parsing
        print("\n[3/7] Testing project upload...")
        from processing.project_parser import project_parser
        project_parser.initialize()

        readme_content = """
# ML Recommendation System

A machine learning recommendation system built with Python and TensorFlow.

## Features

- Built ML engine serving 10k users
- Improved CTR by 35%
- Real-time recommendations

## Technologies

- Python
- TensorFlow
- Flask
- PostgreSQL
"""

        parsed_project = project_parser.parse_readme(readme_content)
        project_data = {
            'title': 'ML Recommender',
            'description': parsed_project.get('description', ''),
            'technologies': parsed_project.get('technologies', []),
            'highlights': parsed_project.get('highlights', []),
            'readme_content': readme_content
        }

        project_id = db_manager.create_project(user_id, project_data)
        print(f"[OK] Project created: {project_id}")

        # Embed project
        from ai_generation.embeddings.vector_store import vector_store
        vector_store.initialize()
        vector_store.add_project(project_id, user_id, project_data)
        print(f"[OK] Project embedded")

        # Step 4: Create Mock Jobs
        print("\n[4/7] Creating mock jobs...")
        mock_jobs = [
            {
                'id': 'job-1',
                'job_title': 'Senior ML Engineer',
                'company_name': 'AI Startup',
                'location': 'Paris',
                'job_type': 'Full-time',
                'description': 'Build ML systems with Python and TensorFlow',
                'required_skills': ['Python', 'TensorFlow', 'Machine Learning'],
                'salary': '€60k-€80k',
                'posted_date': datetime.utcnow(),
                'source': 'Test',
                'url': 'https://example.com/job1'
            },
            {
                'id': 'job-2',
                'job_title': 'Data Scientist',
                'company_name': 'Tech Corp',
                'location': 'Remote',
                'job_type': 'Full-time',
                'description': 'Analyze data and build models',
                'required_skills': ['Python', 'SQL', 'Pandas'],
                'salary': '€50k-€70k',
                'posted_date': datetime.utcnow(),
                'source': 'Test',
                'url': 'https://example.com/job2'
            }
        ]

        print(f"[OK] Created {len(mock_jobs)} mock jobs")

        # Step 5: RAG Ranking
        print("\n[5/7] Testing RAG ranking...")
        from processing.rag_ranker import rag_ranker
        rag_ranker.initialize()

        ranked_jobs = rag_ranker.rank_jobs(
            user_id=user_id,
            jobs=mock_jobs,
            top_n=2
        )

        print(f"[OK] Ranked {len(ranked_jobs)} jobs")
        print(f"[OK] Top match: {ranked_jobs[0].get('job_title')} ({ranked_jobs[0].get('match_score')}%)")

        # Step 6: CV Generation
        print("\n[6/7] Testing CV generation...")
        from ai_generation.cv_generator import cv_generator
        cv_generator.initialize()

        cv_result = cv_generator.generate_cv(
            user_id=user_id,
            job=ranked_jobs[0],
            cv_preferences={
                'cv_length': 1,
                'include_projects': True,
                'max_projects_per_cv': 2
            },
            use_llm=False  # Use template mode for testing
        )

        assert cv_result is not None, "CV generation failed"
        assert 'content' in cv_result, "CV missing content"
        assert 'metadata' in cv_result, "CV missing metadata"
        print(f"[OK] CV generated ({len(cv_result['content'])} characters)")

        # Step 7: Export
        print("\n[7/7] Testing export...")
        from output.csv_exporter import csv_exporter

        # Export search results
        csv_path = csv_exporter.export_search_results(ranked_jobs)
        assert csv_path.exists(), "CSV file not created"
        print(f"[OK] Exported to CSV: {csv_path.name}")

        # Export application
        application = {
            'job': ranked_jobs[0],
            'cv': cv_result,
            'generated_at': datetime.utcnow()
        }

        app_csv_path = csv_exporter.export_applications([application])
        assert app_csv_path.exists(), "Application CSV not created"
        print(f"[OK] Exported application: {app_csv_path.name}")

        print("\n" + "=" * 70)
        print("[SUCCESS] Complete workflow integration test PASSED")
        print("=" * 70)
        print("\nWorkflow Summary:")
        print(f"  1. User registered: {test_email}")
        print(f"  2. Profile created with {len(profile_data['skills'])} skills")
        print(f"  3. Project uploaded and parsed")
        print(f"  4. {len(mock_jobs)} jobs created")
        print(f"  5. Jobs ranked (top: {ranked_jobs[0].get('match_score')}%)")
        print(f"  6. CV generated ({cv_result['metadata'].get('word_count')} words)")
        print(f"  7. Data exported to CSV")

        return True

    except Exception as e:
        print(f"\n[ERROR] Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all integration tests."""
    print("\n" + "=" * 70)
    print("INTEGRATION TEST SUITE")
    print("=" * 70)

    tests = [
        test_complete_workflow
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"\n[X] Test error: {e}")
            failed += 1

    print("\n" + "=" * 70)
    print("INTEGRATION TEST SUMMARY")
    print("=" * 70)
    print(f"[OK] Passed: {passed}/{len(tests)}")
    print(f"[X] Failed: {failed}/{len(tests)}")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
