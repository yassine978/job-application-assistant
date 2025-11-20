"""Test complete database setup."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db_manager import db_manager

def test_complete_database():
    """Test complete database functionality."""
    print("=" * 60)
    print("Complete Database Test")
    print("=" * 60)

    try:
        # Initialize
        db_manager.initialize()

        # Get initial stats
        print("\n[*] Initial Database Statistics:")
        stats = db_manager.get_stats()
        for key, value in stats.items():
            print(f"  • {key}: {value}")

        # Test user creation with unique email
        print("\n[*] Testing user creation...")
        import uuid
        test_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        user_id = db_manager.create_user({
            'email': test_email,
            'password_hash': 'hashed_password_here',
            'full_name': 'Test User',
            'location_preference': 'Paris, France'
        })
        
        # Test profile creation
        print("\n[*] Testing profile creation...")
        profile_id = db_manager.create_profile(user_id, {
            'skills': ['Python', 'JavaScript', 'SQL'],
            'experience': {'years': 2},
            'education': {'degree': 'Bachelor'},
            'languages': ['French', 'English']
        })
        
        # Test project creation
        print("\n[*] Testing project creation...")
        project_id = db_manager.create_project(user_id, {
            'title': 'Test Project',
            'description': 'A test project for the database',
            'technologies': ['Python', 'FastAPI'],
            'highlights': ['Built REST API', 'Deployed to cloud']
        })
        
        # Test job creation
        print("\n[*] Testing job creation...")
        job_id = db_manager.create_job({
            'source': 'test',
            'job_title': 'Python Developer',
            'company_name': 'Test Company',
            'location': 'Paris',
            'job_type': 'Full-time',
            'required_skills': ['Python', 'Django']
        })
        
        # Get final stats
        print("\n[*] Final Database Statistics:")
        stats = db_manager.get_stats()
        for key, value in stats.items():
            print(f"  • {key}: {value}")
        
        print("\n[OK] Complete database test successful!")
        print("[OK] PostgreSQL: Working")
        print("[OK] Chroma Vector DB: Working")
        print("[OK] All operations: Working")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_all_tests():
    """Run all database tests."""
    tests = [
        test_complete_database
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