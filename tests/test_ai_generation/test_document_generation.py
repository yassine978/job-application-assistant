"""Test CV and cover letter generation."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from ai_generation import cv_generator, cover_letter_generator, rag_pipeline
from ai_generation.rag.project_selector import project_selector
from ai_generation.rag.page_optimizer import page_optimizer
from database.db_manager import db_manager
from ai_generation.embeddings.vector_store import vector_store
import uuid
from datetime import datetime, timedelta


def test_project_selector():
    """Test intelligent project selection."""
    print("=" * 70)
    print("Test 1: Project Selector")
    print("=" * 70)

    try:
        # Initialize
        print("\n[*] Initializing systems...")
        db_manager.initialize()
        vector_store.initialize()
        project_selector.initialize()

        # Create test user
        user_id = str(uuid.uuid4())
        test_email = f"proj_test_{user_id[:8]}@test.com"

        with db_manager.db as session:
            from database.models import User
            user = User(
                id=uuid.UUID(user_id),
                email=test_email,
                password_hash='hashed',
                full_name='Test User'
            )
            session.add(user)
            session.commit()

        # Create profile
        profile_data = {
            'skills': ['Python', 'TensorFlow', 'React'],
            'experience': [],
            'education': {},
            'languages': ['English']
        }
        db_manager.create_profile(user_id, profile_data)
        vector_store.add_profile(user_id, profile_data)

        # Create test projects
        print("[*] Creating test projects...")
        projects = [
            {
                'title': 'ML Recommendation System',
                'description': 'Built a collaborative filtering system',
                'technologies': ['Python', 'TensorFlow', 'scikit-learn'],
                'highlights': ['Improved accuracy by 25%', 'Deployed to production']
            },
            {
                'title': 'React Dashboard',
                'description': 'Built a real-time analytics dashboard',
                'technologies': ['React', 'TypeScript', 'D3.js'],
                'highlights': ['Handles 10k users', 'Real-time updates']
            },
            {
                'title': 'API Gateway',
                'description': 'Microservices API gateway',
                'technologies': ['Python', 'FastAPI', 'Docker'],
                'highlights': ['Reduced latency by 40%']
            }
        ]

        for proj_data in projects:
            proj_id = db_manager.create_project(user_id, proj_data)
            vector_store.add_project(proj_id, user_id, proj_data)

        # Create test job (ML focused)
        job = {
            'id': str(uuid.uuid4()),
            'job_title': 'Machine Learning Engineer',
            'company_name': 'AI Corp',
            'description': 'Looking for ML engineer with Python and TensorFlow',
            'required_skills': ['Python', 'TensorFlow', 'Machine Learning']
        }

        # Select relevant projects
        print("\n[*] Selecting relevant projects...")
        selected = project_selector.select_relevant_projects(
            user_id=user_id,
            job=job,
            max_projects=2
        )

        print(f"\n[*] Selected {len(selected)} projects:")
        for proj in selected:
            print(f"  - {proj['project']['title']}")
            print(f"    Relevance: {proj['relevance_score']:.2f}")
            print(f"    Matching tech: {proj['matching_techs']}")

        # Assertions
        assert len(selected) <= 2, "Should select max 2 projects"
        assert selected[0]['project']['title'] == 'ML Recommendation System', "ML project should be first"

        print("\n[OK] Project selector test passed")
        return True

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_page_optimizer():
    """Test page length optimization."""
    print("\n" + "=" * 70)
    print("Test 2: Page Optimizer")
    print("=" * 70)

    # Create sample content
    content = {
        'contact': {'name': 'John Doe', 'email': 'john@example.com'},
        'summary': 'Experienced developer with 5 years of experience in Python and ML. ' * 10,  # Long summary
        'skills': ['Python', 'JavaScript', 'React', 'TensorFlow', 'Docker', 'Kubernetes',
                  'PostgreSQL', 'MongoDB', 'AWS', 'Git', 'CI/CD', 'Machine Learning'] * 2,  # Many skills
        'experience': [
            {
                'title': f'Developer {i}',
                'company': f'Company {i}',
                'achievements': [f'Achievement {j}' for j in range(5)]
            }
            for i in range(5)
        ],  # Many roles
        'projects': [
            {
                'title': f'Project {i}',
                'description': 'A very long description that goes on and on' * 5,
                'technologies': ['Python', 'React', 'Docker'],
                'highlights': [f'Highlight {j}' for j in range(4)]
            }
            for i in range(5)
        ],  # Many projects
        'education': [
            {'degree': 'Master', 'institution': 'University', 'year': 2020},
            {'degree': 'Bachelor', 'institution': 'College', 'year': 2018}
        ],
        'languages': ['English', 'French', 'Spanish', 'German']
    }

    # Test 1-page optimization
    print("\n[*] Optimizing for 1 page...")
    optimized_1 = page_optimizer.optimize_content(content, target_pages=1, include_projects=True)

    print(f"  Skills: {len(content['skills'])} -> {len(optimized_1['skills'])}")
    print(f"  Experience: {len(content['experience'])} -> {len(optimized_1['experience'])}")
    print(f"  Projects: {len(content['projects'])} -> {len(optimized_1['projects'])}")

    assert len(optimized_1['skills']) <= 10, "Should limit skills for 1-page"
    assert len(optimized_1['experience']) <= 3, "Should limit experience for 1-page"
    assert len(optimized_1['projects']) <= 2, "Should limit projects for 1-page"

    # Test 2-page optimization
    print("\n[*] Optimizing for 2 pages...")
    optimized_2 = page_optimizer.optimize_content(content, target_pages=2, include_projects=True)

    print(f"  Skills: {len(content['skills'])} -> {len(optimized_2['skills'])}")
    print(f"  Experience: {len(content['experience'])} -> {len(optimized_2['experience'])}")
    print(f"  Projects: {len(content['projects'])} -> {len(optimized_2['projects'])}")

    assert len(optimized_2['skills']) <= 15, "Should allow more skills for 2-page"
    assert len(optimized_2['experience']) <= 5, "Should allow more experience for 2-page"
    assert len(optimized_2['projects']) <= 4, "Should allow more projects for 2-page"

    print("\n[OK] Page optimizer test passed")
    return True


def test_cv_generation():
    """Test CV generation pipeline."""
    print("\n" + "=" * 70)
    print("Test 3: CV Generation")
    print("=" * 70)

    try:
        # Initialize
        print("\n[*] Initializing systems...")
        db_manager.initialize()
        vector_store.initialize()
        cv_generator.initialize()

        # Create test user
        user_id = str(uuid.uuid4())
        test_email = f"cv_test_{user_id[:8]}@test.com"

        with db_manager.db as session:
            from database.models import User
            user = User(
                id=uuid.UUID(user_id),
                email=test_email,
                password_hash='hashed',
                full_name='CV Test User',
                location_preference='Paris'
            )
            session.add(user)
            session.commit()

        # Create profile
        profile_data = {
            'skills': ['Python', 'Machine Learning', 'TensorFlow'],
            'experience': [{
                'title': 'ML Engineer',
                'company': 'Tech Corp',
                'duration': '2 years'
            }],
            'education': {
                'degree': 'Master',
                'field': 'Computer Science'
            },
            'languages': ['English', 'French']
        }
        db_manager.create_profile(user_id, profile_data)
        vector_store.add_profile(user_id, profile_data)

        # Create a project
        project_data = {
            'title': 'ML Recommendation System',
            'description': 'Built recommendation engine',
            'technologies': ['Python', 'TensorFlow'],
            'highlights': ['Improved accuracy by 25%']
        }
        proj_id = db_manager.create_project(user_id, project_data)
        vector_store.add_project(proj_id, user_id, project_data)

        # Create test job
        job = {
            'id': str(uuid.uuid4()),
            'job_title': 'Senior ML Engineer',
            'company_name': 'AI Startup',
            'location': 'Paris',
            'job_type': 'Full-time',
            'description': 'Looking for ML engineer with Python and TensorFlow',
            'required_skills': ['Python', 'TensorFlow', 'Machine Learning']
        }

        # Generate CV (without LLM for testing)
        print("\n[*] Generating CV...")
        cv_preferences = {
            'cv_length': 1,
            'include_projects': True,
            'max_projects_per_cv': 2
        }

        result = cv_generator.generate_cv(
            user_id=user_id,
            job=job,
            cv_preferences=cv_preferences,
            use_llm=False  # Use template for testing
        )

        print(f"\n[*] CV Generated:")
        print(f"  Length: {len(result['content'])} characters")
        print(f"  Projects included: {result['metadata']['projects_included']}")
        print(f"  Method: {result['metadata']['method']}")

        # Assertions
        assert result['content'], "Should generate CV content"
        assert result['metadata']['cv_length'] == 1, "Should be 1-page CV"
        assert result['metadata']['method'] == 'template', "Should use template method"

        print("\n[OK] CV generation test passed")
        return True

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cover_letter_generation():
    """Test cover letter generation."""
    print("\n" + "=" * 70)
    print("Test 4: Cover Letter Generation")
    print("=" * 70)

    try:
        # Initialize
        print("\n[*] Initializing systems...")
        db_manager.initialize()
        vector_store.initialize()
        cover_letter_generator.initialize()

        # Create test user
        user_id = str(uuid.uuid4())
        test_email = f"cl_test_{user_id[:8]}@test.com"

        with db_manager.db as session:
            from database.models import User
            user = User(
                id=uuid.UUID(user_id),
                email=test_email,
                password_hash='hashed',
                full_name='CL Test User'
            )
            session.add(user)
            session.commit()

        # Create profile
        profile_data = {
            'skills': ['Python', 'React'],
            'experience': [],
            'education': {},
            'languages': ['English']
        }
        db_manager.create_profile(user_id, profile_data)
        vector_store.add_profile(user_id, profile_data)

        # Create test job
        job = {
            'id': str(uuid.uuid4()),
            'job_title': 'Full Stack Developer',
            'company_name': 'Tech Company',
            'description': 'Looking for full stack developer',
            'required_skills': ['Python', 'React']
        }

        # Generate cover letter
        print("\n[*] Generating cover letter...")
        result = cover_letter_generator.generate_cover_letter(
            user_id=user_id,
            job=job,
            use_llm=False  # Use template for testing
        )

        print(f"\n[*] Cover Letter Generated:")
        print(f"  Length: {len(result['content'])} characters")
        print(f"  Method: {result['metadata']['method']}")

        # Assertions
        assert result['content'], "Should generate cover letter"
        assert job['company_name'] in result['content'], "Should mention company"
        assert result['metadata']['method'] == 'template', "Should use template"

        print("\n[OK] Cover letter generation test passed")
        return True

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all AI generation tests."""
    print("\n" + "=" * 70)
    print("AI GENERATION TEST SUITE")
    print("=" * 70)

    tests = [
        test_project_selector,
        test_page_optimizer,
        test_cv_generation,
        test_cover_letter_generation
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
        print("\n[SUCCESS] All AI generation tests passed!")
    else:
        print(f"\n[WARNING] {failed} test(s) failed")

    return failed == 0


if __name__ == "__main__":
    run_all_tests()
