"""User authentication for Streamlit dashboard."""

import streamlit as st
import hashlib
import uuid
from typing import Optional, Dict
from datetime import datetime
from database.db_manager import db_manager
from database.models import User
from ai_generation.embeddings.vector_store import vector_store


class AuthManager:
    """Manage user authentication and sessions."""

    def __init__(self):
        """Initialize auth manager."""
        self.db_manager = db_manager

    def initialize(self):
        """Initialize dependencies."""
        self.db_manager.initialize()

    @staticmethod
    def _hash_password(password: str) -> str:
        """Hash password using SHA-256.

        Args:
            password: Plain text password

        Returns:
            Hashed password
        """
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(
        self,
        email: str,
        password: str,
        full_name: str,
        location_preference: Optional[str] = None
    ) -> Dict:
        """Register a new user.

        Args:
            email: User email
            password: Plain text password
            full_name: User's full name
            location_preference: Preferred location

        Returns:
            Result dictionary with success status and message
        """
        try:
            # Check if email already exists
            with self.db_manager.db as session:
                existing_user = session.query(User).filter(
                    User.email == email
                ).first()

                if existing_user:
                    return {
                        'success': False,
                        'message': 'Email already registered'
                    }

                # Create new user
                user_id = uuid.uuid4()
                hashed_password = self._hash_password(password)

                new_user = User(
                    id=user_id,
                    email=email,
                    password_hash=hashed_password,
                    full_name=full_name,
                    location_preference=location_preference,
                    created_at=datetime.utcnow()
                )

                session.add(new_user)
                session.commit()

                return {
                    'success': True,
                    'message': 'Registration successful',
                    'user_id': str(user_id)
                }

        except Exception as e:
            return {
                'success': False,
                'message': f'Registration failed: {str(e)}'
            }

    def login_user(self, email: str, password: str) -> Dict:
        """Authenticate user login.

        Args:
            email: User email
            password: Plain text password

        Returns:
            Result dictionary with user info if successful
        """
        try:
            hashed_password = self._hash_password(password)

            with self.db_manager.db as session:
                user = session.query(User).filter(
                    User.email == email,
                    User.password_hash == hashed_password
                ).first()

                if not user:
                    return {
                        'success': False,
                        'message': 'Invalid email or password'
                    }

                # Update last login
                user.last_login = datetime.utcnow()
                session.commit()

                return {
                    'success': True,
                    'message': 'Login successful',
                    'user': {
                        'id': str(user.id),
                        'email': user.email,
                        'full_name': user.full_name,
                        'location_preference': user.location_preference
                    }
                }

        except Exception as e:
            return {
                'success': False,
                'message': f'Login failed: {str(e)}'
            }

    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user information by ID.

        Args:
            user_id: User ID

        Returns:
            User dictionary or None
        """
        try:
            with self.db_manager.db as session:
                user = session.query(User).filter(
                    User.id == uuid.UUID(user_id)
                ).first()

                if not user:
                    return None

                return {
                    'id': str(user.id),
                    'email': user.email,
                    'full_name': user.full_name,
                    'location_preference': user.location_preference,
                    'created_at': user.created_at,
                    'last_login': user.last_login
                }

        except Exception as e:
            print(f"[ERROR] Failed to get user: {e}")
            return None

    def update_user_profile(
        self,
        user_id: str,
        full_name: Optional[str] = None,
        location_preference: Optional[str] = None
    ) -> Dict:
        """Update user profile information.

        Args:
            user_id: User ID
            full_name: New full name
            location_preference: New location preference

        Returns:
            Result dictionary
        """
        try:
            with self.db_manager.db as session:
                user = session.query(User).filter(
                    User.id == uuid.UUID(user_id)
                ).first()

                if not user:
                    return {
                        'success': False,
                        'message': 'User not found'
                    }

                if full_name:
                    user.full_name = full_name
                if location_preference:
                    user.location_preference = location_preference

                session.commit()

                return {
                    'success': True,
                    'message': 'Profile updated successfully'
                }

        except Exception as e:
            return {
                'success': False,
                'message': f'Update failed: {str(e)}'
            }

    def change_password(
        self,
        user_id: str,
        old_password: str,
        new_password: str
    ) -> Dict:
        """Change user password.

        Args:
            user_id: User ID
            old_password: Current password
            new_password: New password

        Returns:
            Result dictionary
        """
        try:
            old_hash = self._hash_password(old_password)
            new_hash = self._hash_password(new_password)

            with self.db_manager.db as session:
                user = session.query(User).filter(
                    User.id == uuid.UUID(user_id)
                ).first()

                if not user:
                    return {
                        'success': False,
                        'message': 'User not found'
                    }

                if user.password_hash != old_hash:
                    return {
                        'success': False,
                        'message': 'Current password is incorrect'
                    }

                user.password_hash = new_hash
                session.commit()

                return {
                    'success': True,
                    'message': 'Password changed successfully'
                }

        except Exception as e:
            return {
                'success': False,
                'message': f'Password change failed: {str(e)}'
            }

    @staticmethod
    def is_authenticated() -> bool:
        """Check if user is authenticated in current session.

        Returns:
            True if authenticated
        """
        return st.session_state.get('authenticated', False)

    @staticmethod
    def get_current_user() -> Optional[Dict]:
        """Get current authenticated user.

        Returns:
            User dictionary or None
        """
        if not AuthManager.is_authenticated():
            return None
        return st.session_state.get('user')

    @staticmethod
    def logout():
        """Logout current user."""
        st.session_state['authenticated'] = False
        st.session_state['user'] = None
        st.session_state.clear()


# Global auth manager instance
auth_manager = AuthManager()
