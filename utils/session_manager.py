"""Session management utilities for Streamlit."""

import streamlit as st
from typing import Any, Optional, Dict
from datetime import datetime, timedelta


class SessionManager:
    """Manage Streamlit session state."""

    @staticmethod
    def init_session_state():
        """Initialize all session state variables."""
        defaults = {
            'authenticated': False,
            'user': None,
            'page': 'login',
            'search_results': [],
            'selected_job': None,
            'cv_preferences': {
                'cv_length': 1,
                'include_projects': True,
                'max_projects_per_cv': 3
            },
            'notifications': [],
            'last_activity': datetime.utcnow()
        }

        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

    @staticmethod
    def get(key: str, default: Any = None) -> Any:
        """Get value from session state.

        Args:
            key: Session key
            default: Default value if key doesn't exist

        Returns:
            Session value or default
        """
        return st.session_state.get(key, default)

    @staticmethod
    def set(key: str, value: Any) -> None:
        """Set value in session state.

        Args:
            key: Session key
            value: Value to set
        """
        st.session_state[key] = value
        st.session_state['last_activity'] = datetime.utcnow()

    @staticmethod
    def delete(key: str) -> None:
        """Delete key from session state.

        Args:
            key: Session key to delete
        """
        if key in st.session_state:
            del st.session_state[key]

    @staticmethod
    def clear():
        """Clear all session state."""
        st.session_state.clear()

    @staticmethod
    def is_authenticated() -> bool:
        """Check if user is authenticated.

        Returns:
            True if authenticated
        """
        return st.session_state.get('authenticated', False)

    @staticmethod
    def get_user() -> Optional[Dict]:
        """Get current user.

        Returns:
            User dictionary or None
        """
        return st.session_state.get('user')

    @staticmethod
    def set_user(user: Dict):
        """Set current user and mark as authenticated.

        Args:
            user: User dictionary
        """
        st.session_state['user'] = user
        st.session_state['authenticated'] = True
        st.session_state['last_activity'] = datetime.utcnow()

    @staticmethod
    def logout():
        """Logout current user."""
        st.session_state['authenticated'] = False
        st.session_state['user'] = None
        st.session_state['page'] = 'login'

    @staticmethod
    def add_notification(message: str, type: str = 'info'):
        """Add notification to session.

        Args:
            message: Notification message
            type: Notification type (success, info, warning, error)
        """
        if 'notifications' not in st.session_state:
            st.session_state['notifications'] = []

        st.session_state['notifications'].append({
            'message': message,
            'type': type,
            'timestamp': datetime.utcnow()
        })

    @staticmethod
    def get_notifications() -> list:
        """Get all notifications.

        Returns:
            List of notification dictionaries
        """
        return st.session_state.get('notifications', [])

    @staticmethod
    def clear_notifications():
        """Clear all notifications."""
        st.session_state['notifications'] = []

    @staticmethod
    def check_session_timeout(timeout_minutes: int = 30) -> bool:
        """Check if session has timed out.

        Args:
            timeout_minutes: Timeout duration in minutes

        Returns:
            True if session has timed out
        """
        last_activity = st.session_state.get('last_activity')

        if not last_activity:
            return False

        if isinstance(last_activity, str):
            last_activity = datetime.fromisoformat(last_activity)

        timeout_delta = timedelta(minutes=timeout_minutes)
        return datetime.utcnow() - last_activity > timeout_delta

    @staticmethod
    def update_cv_preferences(preferences: Dict):
        """Update CV generation preferences.

        Args:
            preferences: CV preferences dictionary
        """
        if 'cv_preferences' not in st.session_state:
            st.session_state['cv_preferences'] = {}

        st.session_state['cv_preferences'].update(preferences)

    @staticmethod
    def get_cv_preferences() -> Dict:
        """Get CV generation preferences.

        Returns:
            CV preferences dictionary
        """
        return st.session_state.get('cv_preferences', {
            'cv_length': 1,
            'include_projects': True,
            'max_projects_per_cv': 3
        })


# Global session manager instance
session_manager = SessionManager()
