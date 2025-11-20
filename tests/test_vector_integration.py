"""Test complete integration: Database + Embeddings + Vector Store."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db_manager import db_manager
from ai_generation.embeddings.vector_store import vector_store
from ai_generation.embeddings.retriever import retriever
import uuid

def test_complete_integration():
    """Test end-to-end integration."""
    print("=" * 60)
    print("Complete Integration Test")
    print("=" * 60)
    
    try:
        # Initialize all systems
        print("\n[*] Initializing systems...")
        db_manager.initialize()
        vector_store.initialize()
        retriever.initialize()
        
        # Create test user with unique email
        print("\n[*] Creating test user...")
        user_id = str(uuid.uuid4())
        test_email = f"integration_{user_id[:8]}@test.com"  # Unique email
        
        user_data = {
            'email': test_email,
            'password_hash': 'hashed',
            'full_name': 'Integration Test User',
            'location_preference': 'Paris'
        }
        
        # Create user using database session
        with db_manager.db as session:
            from database.models import User
            user = User(
                id=uuid.UUID(user_id),
                **user_data
            )
            session.add(user)
            session.commit()

        print(f"  [OK] User created: {user_id}")
        print(f"  [*] Email: {test_email}")
        
        # Create profile
        print("\n[*] Creating profile with embedding...")
        profile_data = {
            'skills': ['Python', 'Machine Learning', 'TensorFlow'],
            'experience': [{
                'title': 'ML Engineer',
                'company': 'AI Startup',
                'duration': '2 years'
            }],
            'education': {
                'degree': 'Master',
                'field': 'Computer Science'
            },
            'languages': ['English', 'French']
        }
        
        profile_id = db_manager.create_profile(user_id, profile_data)
        
        # Add profile to vector store
        chroma_id = vector_store.add_profile(user_id, profile_data)
        print(f"  [OK] Profile embedded and stored: {chroma_id}")
        
        # Create project
        print("\n[*] Creating project with embedding...")
        project_data = {
            'title': 'ML Recommendation System',
            'description': 'Built a collaborative filtering recommender',
            'technologies': ['Python', 'TensorFlow', 'scikit-learn'],
            'highlights': [
                'Improved accuracy by 25%',
                'Deployed to production'
            ]
        }
        
        project_id = db_manager.create_project(user_id, project_data)
        
        # Add project to vector store
        project_chroma_id = vector_store.add_project(
            project_id, 
            user_id, 
            project_data
        )
        print(f"  [OK] Project embedded and stored: {project_chroma_id}")
        
        # Create job
        print("\n[*] Creating job with embedding...")
        job_data = {
            'source': 'test',
            'job_title': 'Senior ML Engineer',
            'company_name': 'Tech Giant',
            'location': 'Paris',
            'job_type': 'Full-time',
            'description': 'Looking for ML engineer with Python and TensorFlow',
            'required_skills': ['Python', 'TensorFlow', 'Machine Learning']
        }
        
        job_id = db_manager.create_job(job_data)
        
        # Add job to vector store
        job_chroma_id = vector_store.add_job(job_id, job_data)
        print(f"  [OK] Job embedded and stored: {job_chroma_id}")
        
        # Test semantic search
        print("\n[*] Testing semantic search...")
        
        # Find similar jobs to profile
        similar_jobs = vector_store.find_similar_jobs(user_id, n_results=5)
        print(f"\n  Found {len(similar_jobs)} similar jobs:")
        for job in similar_jobs:
            print(f"    • Job: {job['metadata']['title']}")
            print(f"      Company: {job['metadata']['company']}")
            print(f"      Similarity: {job['similarity']:.3f}")
        
        # Find relevant projects for job
        relevant_projects = vector_store.find_relevant_projects(
            job_id=job_id,
            user_id=user_id,
            n_results=3
        )
        print(f"\n  Found {len(relevant_projects)} relevant projects:")
        for proj in relevant_projects:
            print(f"    • Project: {proj['metadata']['title']}")
            print(f"      Relevance: {proj['relevance']:.3f}")
        
        # Test retriever context
        print("\n[*] Testing context retrieval...")
        
        profile_context = retriever.get_profile_context(user_id)
        print(f"\n  Profile context ({len(profile_context)} chars):")
        print(f"    {profile_context[:200]}...")
        
        job_context = retriever.get_job_context(job_id)
        print(f"\n  Job context ({len(job_context)} chars):")
        print(f"    {job_context[:200]}...")
        
        projects_context = retriever.get_relevant_projects_context(
            user_id=user_id,
            job_id=job_id,
            max_projects=2
        )
        print(f"\n  Projects context ({len(projects_context)} chars):")
        if projects_context:
            print(f"    {projects_context[:200]}...")
        else:
            print(f"    (empty)")
        
        # Get full context
        full_context = retriever.get_full_context(
            user_id=user_id,
            job_id=job_id,
            include_projects=True,
            max_projects=2
        )
        
        print("\n[*] Full Context Summary:")
        print(f"  • Profile: {len(full_context['profile'])} chars")
        print(f"  • Job: {len(full_context['job'])} chars")
        print(f"  • Projects: {len(full_context['projects'])} chars")
        print(f"  • Total: {sum(len(v) for v in full_context.values())} chars")
        
        print("\n[OK] Complete integration test successful!")
        print("[OK] Database + Embeddings + Vector Store: All working!")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_all_tests():
    """Run all vector integration tests."""
    tests = [
        test_complete_integration
    ]

    passed = sum(1 for test in tests if test())
    failed = len(tests) - passed

    print(f"\n[OK] Passed: {passed}/{len(tests)}")
    print(f"[X] Failed: {failed}/{len(tests)}")

    return failed == 0

if __name__ == "__main__":
    import sys
    success = run_all_tests()
    sys.exit(0 if success else 1)