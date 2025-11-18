"""Test authentication functionality."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import uuid
from datetime import datetime
from dashboard.auth import auth_manager
from database.db_manager import db_manager
from database.models import User


def test_password_hashing():
    """Test password hashing."""
    print("=" * 70)
    print("Test 1: Password Hashing")
    print("=" * 70)

    password = "test_password_123"
    hash1 = auth_manager._hash_password(password)
    hash2 = auth_manager._hash_password(password)

    print(f"\n[*] Original password: {password}")
    print(f"[*] Hash 1: {hash1[:20]}...")
    print(f"[*] Hash 2: {hash2[:20]}...")

    # Same password should produce same hash
    assert hash1 == hash2, "Same password should produce same hash"

    # Different password should produce different hash
    hash3 = auth_manager._hash_password("different_password")
    assert hash1 != hash3, "Different passwords should produce different hashes"

    print("\n[OK] Password hashing test passed")
    return True


def test_user_registration():
    """Test user registration."""
    print("\n" + "=" * 70)
    print("Test 2: User Registration")
    print("=" * 70)

    try:
        # Initialize
        print("\n[*] Initializing systems...")
        db_manager.initialize()
        auth_manager.initialize()

        # Test data
        test_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        test_password = "secure_password_123"
        test_name = "Test User"
        test_location = "Paris, France"

        print(f"[*] Registering user: {test_email}")

        # Register user
        result = auth_manager.register_user(
            email=test_email,
            password=test_password,
            full_name=test_name,
            location_preference=test_location
        )

        print(f"\n[*] Registration result: {result['message']}")

        # Verify success
        assert result['success'], "Registration should succeed"
        assert 'user_id' in result, "Should return user_id"

        # Try to register same email again
        result2 = auth_manager.register_user(
            email=test_email,
            password="another_password",
            full_name="Another User"
        )

        print(f"[*] Duplicate registration result: {result2['message']}")
        assert not result2['success'], "Duplicate email should fail"
        assert 'already registered' in result2['message'].lower(), "Should indicate email exists"

        print("\n[OK] User registration test passed")
        return True

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_user_login():
    """Test user login."""
    print("\n" + "=" * 70)
    print("Test 3: User Login")
    print("=" * 70)

    try:
        # Initialize
        print("\n[*] Initializing systems...")
        db_manager.initialize()
        auth_manager.initialize()

        # Create test user
        test_email = f"login_test_{uuid.uuid4().hex[:8]}@example.com"
        test_password = "login_password_123"
        test_name = "Login Test User"

        print(f"[*] Creating test user: {test_email}")
        reg_result = auth_manager.register_user(
            email=test_email,
            password=test_password,
            full_name=test_name
        )

        assert reg_result['success'], "Registration should succeed"

        # Test successful login
        print(f"\n[*] Testing login with correct credentials...")
        login_result = auth_manager.login_user(test_email, test_password)

        print(f"[*] Login result: {login_result['message']}")
        assert login_result['success'], "Login should succeed"
        assert 'user' in login_result, "Should return user data"
        assert login_result['user']['email'] == test_email, "Should return correct user"

        # Test failed login (wrong password)
        print(f"\n[*] Testing login with wrong password...")
        wrong_result = auth_manager.login_user(test_email, "wrong_password")

        print(f"[*] Wrong password result: {wrong_result['message']}")
        assert not wrong_result['success'], "Login should fail with wrong password"
        assert 'invalid' in wrong_result['message'].lower(), "Should indicate invalid credentials"

        # Test failed login (wrong email)
        print(f"\n[*] Testing login with wrong email...")
        wrong_email_result = auth_manager.login_user("wrong@email.com", test_password)

        print(f"[*] Wrong email result: {wrong_email_result['message']}")
        assert not wrong_email_result['success'], "Login should fail with wrong email"

        print("\n[OK] User login test passed")
        return True

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_get_user_by_id():
    """Test getting user by ID."""
    print("\n" + "=" * 70)
    print("Test 4: Get User by ID")
    print("=" * 70)

    try:
        # Initialize
        print("\n[*] Initializing systems...")
        db_manager.initialize()
        auth_manager.initialize()

        # Create test user
        test_email = f"getuser_test_{uuid.uuid4().hex[:8]}@example.com"
        test_name = "Get User Test"

        reg_result = auth_manager.register_user(
            email=test_email,
            password="password123",
            full_name=test_name,
            location_preference="New York"
        )

        assert reg_result['success'], "Registration should succeed"
        user_id = reg_result['user_id']

        print(f"\n[*] Getting user by ID: {user_id}")

        # Get user
        user = auth_manager.get_user_by_id(user_id)

        print(f"[*] Retrieved user: {user['full_name']}")
        assert user is not None, "Should retrieve user"
        assert user['email'] == test_email, "Should have correct email"
        assert user['full_name'] == test_name, "Should have correct name"
        assert user['location_preference'] == "New York", "Should have correct location"

        # Test non-existent user
        print(f"\n[*] Testing with non-existent user ID...")
        fake_id = str(uuid.uuid4())
        fake_user = auth_manager.get_user_by_id(fake_id)

        assert fake_user is None, "Should return None for non-existent user"

        print("\n[OK] Get user by ID test passed")
        return True

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_update_profile():
    """Test updating user profile."""
    print("\n" + "=" * 70)
    print("Test 5: Update User Profile")
    print("=" * 70)

    try:
        # Initialize
        print("\n[*] Initializing systems...")
        db_manager.initialize()
        auth_manager.initialize()

        # Create test user
        test_email = f"update_test_{uuid.uuid4().hex[:8]}@example.com"

        reg_result = auth_manager.register_user(
            email=test_email,
            password="password123",
            full_name="Original Name",
            location_preference="Original Location"
        )

        user_id = reg_result['user_id']

        # Update profile
        print(f"\n[*] Updating user profile...")
        update_result = auth_manager.update_user_profile(
            user_id=user_id,
            full_name="Updated Name",
            location_preference="Updated Location"
        )

        print(f"[*] Update result: {update_result['message']}")
        assert update_result['success'], "Update should succeed"

        # Verify update
        user = auth_manager.get_user_by_id(user_id)
        assert user['full_name'] == "Updated Name", "Name should be updated"
        assert user['location_preference'] == "Updated Location", "Location should be updated"

        print(f"[*] Verified updated name: {user['full_name']}")
        print(f"[*] Verified updated location: {user['location_preference']}")

        print("\n[OK] Update profile test passed")
        return True

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_change_password():
    """Test changing user password."""
    print("\n" + "=" * 70)
    print("Test 6: Change Password")
    print("=" * 70)

    try:
        # Initialize
        print("\n[*] Initializing systems...")
        db_manager.initialize()
        auth_manager.initialize()

        # Create test user
        test_email = f"password_test_{uuid.uuid4().hex[:8]}@example.com"
        old_password = "old_password_123"
        new_password = "new_password_456"

        reg_result = auth_manager.register_user(
            email=test_email,
            password=old_password,
            full_name="Password Test User"
        )

        user_id = reg_result['user_id']

        # Test password change with wrong old password
        print(f"\n[*] Testing password change with wrong old password...")
        wrong_result = auth_manager.change_password(
            user_id=user_id,
            old_password="wrong_password",
            new_password=new_password
        )

        print(f"[*] Wrong password result: {wrong_result['message']}")
        assert not wrong_result['success'], "Should fail with wrong old password"

        # Test successful password change
        print(f"\n[*] Testing password change with correct old password...")
        change_result = auth_manager.change_password(
            user_id=user_id,
            old_password=old_password,
            new_password=new_password
        )

        print(f"[*] Change result: {change_result['message']}")
        assert change_result['success'], "Password change should succeed"

        # Verify login with new password
        print(f"\n[*] Verifying login with new password...")
        login_result = auth_manager.login_user(test_email, new_password)
        assert login_result['success'], "Should login with new password"

        # Verify old password doesn't work
        print(f"\n[*] Verifying old password no longer works...")
        old_login_result = auth_manager.login_user(test_email, old_password)
        assert not old_login_result['success'], "Old password should not work"

        print("\n[OK] Change password test passed")
        return True

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all authentication tests."""
    print("\n" + "=" * 70)
    print("AUTHENTICATION TEST SUITE")
    print("=" * 70)

    tests = [
        test_password_hashing,
        test_user_registration,
        test_user_login,
        test_get_user_by_id,
        test_update_profile,
        test_change_password
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
        print("\n[SUCCESS] All authentication tests passed!")
    else:
        print(f"\n[WARNING] {failed} test(s) failed")

    return failed == 0


if __name__ == "__main__":
    run_all_tests()
