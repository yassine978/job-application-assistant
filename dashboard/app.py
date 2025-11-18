"""Main Streamlit dashboard application."""

import streamlit as st
from dashboard.auth import auth_manager
from config import APP_NAME, VERSION


def init_session_state():
    """Initialize session state variables."""
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False
    if 'user' not in st.session_state:
        st.session_state['user'] = None
    if 'page' not in st.session_state:
        st.session_state['page'] = 'login'


def show_login_page():
    """Display login/registration page."""
    st.title(f"{APP_NAME} - Login")

    tab1, tab2 = st.tabs(["Login", "Register"])

    # Login Tab
    with tab1:
        st.subheader("Login to Your Account")

        with st.form("login_form"):
            email = st.text_input("Email", placeholder="your.email@example.com")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")

            if submit:
                if not email or not password:
                    st.error("Please enter both email and password")
                else:
                    result = auth_manager.login_user(email, password)

                    if result['success']:
                        st.session_state['authenticated'] = True
                        st.session_state['user'] = result['user']
                        st.success(result['message'])
                        st.rerun()
                    else:
                        st.error(result['message'])

    # Register Tab
    with tab2:
        st.subheader("Create New Account")

        with st.form("register_form"):
            reg_email = st.text_input("Email", placeholder="your.email@example.com", key="reg_email")
            reg_name = st.text_input("Full Name", placeholder="John Doe")
            reg_location = st.text_input("Location Preference (Optional)", placeholder="Paris, France")
            reg_password = st.text_input("Password", type="password", key="reg_password")
            reg_password2 = st.text_input("Confirm Password", type="password")
            register = st.form_submit_button("Register")

            if register:
                if not reg_email or not reg_name or not reg_password:
                    st.error("Please fill in all required fields")
                elif reg_password != reg_password2:
                    st.error("Passwords do not match")
                elif len(reg_password) < 6:
                    st.error("Password must be at least 6 characters")
                else:
                    result = auth_manager.register_user(
                        email=reg_email,
                        password=reg_password,
                        full_name=reg_name,
                        location_preference=reg_location if reg_location else None
                    )

                    if result['success']:
                        st.success(result['message'])
                        st.info("Please login with your credentials")
                    else:
                        st.error(result['message'])


def show_sidebar():
    """Display sidebar with navigation and user info."""
    with st.sidebar:
        user = st.session_state.get('user')

        if user:
            st.title(APP_NAME)
            st.write(f"**{user['full_name']}**")
            st.write(f"📧 {user['email']}")

            if user.get('location_preference'):
                st.write(f"📍 {user['location_preference']}")

            st.divider()

            # Navigation
            st.subheader("Navigation")

            # Page buttons
            if st.button("🏠 Dashboard", use_container_width=True):
                st.session_state['page'] = 'dashboard'
                st.rerun()

            if st.button("👤 Profile & Projects", use_container_width=True):
                st.session_state['page'] = 'profile'
                st.rerun()

            if st.button("🔍 Job Search", use_container_width=True):
                st.session_state['page'] = 'search'
                st.rerun()

            if st.button("📊 My Applications", use_container_width=True):
                st.session_state['page'] = 'applications'
                st.rerun()

            if st.button("⚙️ Settings", use_container_width=True):
                st.session_state['page'] = 'settings'
                st.rerun()

            st.divider()

            # Logout button
            if st.button("🚪 Logout", use_container_width=True):
                auth_manager.logout()
                st.rerun()

            # Footer
            st.caption(f"Version {VERSION}")


def show_dashboard_page():
    """Display main dashboard page."""
    st.title("Dashboard")

    user = st.session_state.get('user')
    st.write(f"Welcome back, **{user['full_name']}**!")

    # Quick stats
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Applications", "0", "0 this week")

    with col2:
        st.metric("Active Projects", "0", "0 new")

    with col3:
        st.metric("Job Matches", "0", "0 pending")

    with col4:
        st.metric("Match Score Avg", "0%", "0%")

    st.divider()

    # Quick actions
    st.subheader("Quick Actions")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔍 Search New Jobs", use_container_width=True):
            st.session_state['page'] = 'search'
            st.rerun()

    with col2:
        if st.button("📁 Upload Project", use_container_width=True):
            st.session_state['page'] = 'profile'
            st.rerun()

    with col3:
        if st.button("👤 Update Profile", use_container_width=True):
            st.session_state['page'] = 'settings'
            st.rerun()

    st.divider()

    # Recent activity (placeholder)
    st.subheader("Recent Activity")
    st.info("No recent activity. Start by searching for jobs or uploading your projects!")


def show_profile_page():
    """Display profile and project management page."""
    st.title("Profile & Projects")

    user = st.session_state.get('user')

    # Import here to avoid circular imports
    from database.db_manager import db_manager

    # Profile section
    st.subheader("Your Profile")

    # Get profile data
    profile = db_manager.get_profile(user['id'])

    if not profile:
        st.warning("Profile not created yet. Please complete your profile below.")

        with st.form("create_profile"):
            st.write("**Skills**")
            skills_input = st.text_area(
                "Enter your skills (one per line)",
                placeholder="Python\nMachine Learning\nReact\nSQL"
            )

            st.write("**Experience**")
            exp_title = st.text_input("Job Title")
            exp_company = st.text_input("Company")
            exp_duration = st.text_input("Duration", placeholder="6 months (Jan 2024 - Jun 2024)")

            st.write("**Education**")
            edu_degree = st.text_input("Degree", placeholder="Master in Computer Science")
            edu_institution = st.text_input("Institution", placeholder="University of Paris")
            edu_year = st.number_input("Year", min_value=2000, max_value=2030, value=2024)

            st.write("**Languages**")
            languages_input = st.text_area(
                "Languages (one per line)",
                placeholder="English (Fluent)\nFrench (Native)"
            )

            submit = st.form_submit_button("Create Profile")

            if submit:
                # Parse inputs
                skills = [s.strip() for s in skills_input.split('\n') if s.strip()]
                languages = [l.strip() for l in languages_input.split('\n') if l.strip()]

                experience = []
                if exp_title and exp_company:
                    experience.append({
                        'title': exp_title,
                        'company': exp_company,
                        'duration': exp_duration
                    })

                education = {}
                if edu_degree and edu_institution:
                    education = {
                        'degree': edu_degree,
                        'institution': edu_institution,
                        'year': edu_year
                    }

                profile_data = {
                    'skills': skills,
                    'experience': experience,
                    'education': education,
                    'languages': languages
                }

                # Create profile
                try:
                    db_manager.create_profile(user['id'], profile_data)
                    st.success("Profile created successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to create profile: {e}")

    else:
        # Display existing profile
        with st.expander("View Profile Details", expanded=True):
            st.write("**Skills:**", ', '.join(profile.get('skills', [])))

            if profile.get('experience'):
                st.write("**Experience:**")
                for exp in profile['experience']:
                    st.write(f"- {exp.get('title')} at {exp.get('company')} ({exp.get('duration', 'N/A')})")

            if profile.get('education'):
                edu = profile['education']
                st.write(f"**Education:** {edu.get('degree')} from {edu.get('institution')} ({edu.get('year')})")

            if profile.get('languages'):
                st.write("**Languages:**", ', '.join(profile['languages']))

    st.divider()

    # Projects section
    st.subheader("Your Projects")

    # Get user projects
    projects = db_manager.get_user_projects(user['id'])

    if not projects:
        st.info("No projects yet. Upload your first project!")
    else:
        for project in projects:
            with st.expander(f"📁 {project['title']}", expanded=False):
                st.write(f"**Description:** {project.get('description', 'N/A')}")
                st.write(f"**Technologies:** {', '.join(project.get('technologies', []))}")

                if project.get('highlights'):
                    st.write("**Highlights:**")
                    for highlight in project['highlights']:
                        st.write(f"- {highlight}")

                if project.get('github_url'):
                    st.write(f"**GitHub:** {project['github_url']}")

                if project.get('demo_url'):
                    st.write(f"**Demo:** {project['demo_url']}")

    st.divider()

    # Upload new project
    st.subheader("Upload New Project")

    with st.form("upload_project"):
        project_title = st.text_input("Project Title")
        readme_file = st.file_uploader("Upload README.md", type=['md', 'txt'])
        github_url = st.text_input("GitHub URL (Optional)")
        demo_url = st.text_input("Demo URL (Optional)")

        upload = st.form_submit_button("Upload Project")

        if upload:
            if not project_title:
                st.error("Please enter a project title")
            elif not readme_file:
                st.error("Please upload a README file")
            else:
                try:
                    # Read README content
                    readme_content = readme_file.read().decode('utf-8')

                    # Parse README
                    from processing.project_parser import project_parser
                    project_parser.initialize()
                    parsed_data = project_parser.parse_readme(readme_content)

                    # Create project
                    project_data = {
                        'title': project_title,
                        'description': parsed_data.get('description', ''),
                        'technologies': parsed_data.get('technologies', []),
                        'highlights': parsed_data.get('highlights', []),
                        'readme_content': readme_content,
                        'github_url': github_url if github_url else None,
                        'demo_url': demo_url if demo_url else None
                    }

                    # Save to database
                    from ai_generation.embeddings.vector_store import vector_store
                    vector_store.initialize()

                    project_id = db_manager.create_project(user['id'], project_data)
                    vector_store.add_project(project_id, user['id'], project_data)

                    st.success(f"Project '{project_title}' uploaded successfully!")
                    st.rerun()

                except Exception as e:
                    st.error(f"Failed to upload project: {e}")


def show_search_page():
    """Display job search page."""
    st.title("Job Search")
    st.info("Job search functionality coming in Phase 8!")


def show_applications_page():
    """Display applications page."""
    st.title("My Applications")
    st.info("Applications tracking coming in Phase 8!")


def show_settings_page():
    """Display settings page."""
    st.title("Settings")

    user = st.session_state.get('user')

    # Account settings
    st.subheader("Account Settings")

    with st.form("update_account"):
        new_name = st.text_input("Full Name", value=user['full_name'])
        new_location = st.text_input(
            "Location Preference",
            value=user.get('location_preference', '')
        )

        update = st.form_submit_button("Update Account")

        if update:
            result = auth_manager.update_user_profile(
                user['id'],
                full_name=new_name,
                location_preference=new_location
            )

            if result['success']:
                st.success(result['message'])
                # Update session state
                st.session_state['user']['full_name'] = new_name
                st.session_state['user']['location_preference'] = new_location
                st.rerun()
            else:
                st.error(result['message'])

    st.divider()

    # Change password
    st.subheader("Change Password")

    with st.form("change_password"):
        old_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")

        change = st.form_submit_button("Change Password")

        if change:
            if not old_password or not new_password:
                st.error("Please fill in all fields")
            elif new_password != confirm_password:
                st.error("New passwords do not match")
            elif len(new_password) < 6:
                st.error("Password must be at least 6 characters")
            else:
                result = auth_manager.change_password(
                    user['id'],
                    old_password,
                    new_password
                )

                if result['success']:
                    st.success(result['message'])
                else:
                    st.error(result['message'])

    st.divider()

    # CV Preferences
    st.subheader("CV Preferences")

    from database.db_manager import db_manager

    with st.form("cv_preferences"):
        cv_length = st.selectbox("CV Length", [1, 2], index=0)
        include_projects = st.checkbox("Include Projects in CV", value=True)
        max_projects = st.slider("Max Projects per CV", 1, 5, 3)

        save_prefs = st.form_submit_button("Save Preferences")

        if save_prefs:
            st.success("CV preferences saved!")


def main():
    """Main application entry point."""
    # Page config
    st.set_page_config(
        page_title=APP_NAME,
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Initialize
    init_session_state()
    auth_manager.initialize()

    # Check authentication
    if not st.session_state.get('authenticated'):
        show_login_page()
    else:
        # Show sidebar
        show_sidebar()

        # Route to appropriate page
        page = st.session_state.get('page', 'dashboard')

        if page == 'dashboard':
            show_dashboard_page()
        elif page == 'profile':
            show_profile_page()
        elif page == 'search':
            show_search_page()
        elif page == 'applications':
            show_applications_page()
        elif page == 'settings':
            show_settings_page()
        else:
            show_dashboard_page()


if __name__ == "__main__":
    main()
