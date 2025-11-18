"""Project card component."""

import streamlit as st
from typing import Dict, Optional


def render_project_card(
    project: Dict,
    show_actions: bool = True,
    on_delete_callback=None
) -> None:
    """Render a project card.

    Args:
        project: Project data dictionary
        show_actions: Whether to show action buttons
        on_delete_callback: Function to call when delete is clicked
    """
    with st.container():
        # Header with title and tech badges
        col1, col2 = st.columns([3, 1])

        with col1:
            st.subheader(f"📁 {project.get('title', 'Untitled Project')}")

        with col2:
            if show_actions:
                if st.button("🗑️ Delete", key=f"delete_{project.get('id')}", use_container_width=True):
                    if on_delete_callback:
                        on_delete_callback(project.get('id'))

        # Description
        if project.get('description'):
            st.write(project['description'])

        # Technologies
        if project.get('technologies'):
            st.write("**Technologies:**")
            tech_cols = st.columns(min(len(project['technologies']), 5))
            for i, tech in enumerate(project['technologies'][:5]):
                with tech_cols[i]:
                    st.markdown(f"<span style='background-color: #e0e0e0; padding: 3px 8px; border-radius: 3px; font-size: 12px;'>{tech}</span>", unsafe_allow_html=True)

            if len(project['technologies']) > 5:
                st.caption(f"+{len(project['technologies']) - 5} more")

        # Highlights
        if project.get('highlights'):
            st.write("**Highlights:**")
            for highlight in project['highlights'][:3]:
                st.write(f"- {highlight}")

            if len(project['highlights']) > 3:
                st.caption(f"+{len(project['highlights']) - 3} more")

        # Links
        if project.get('github_url') or project.get('demo_url'):
            link_cols = st.columns(2)

            with link_cols[0]:
                if project.get('github_url'):
                    st.markdown(f"[🔗 GitHub]({project['github_url']})")

            with link_cols[1]:
                if project.get('demo_url'):
                    st.markdown(f"[🌐 Demo]({project['demo_url']})")

        st.divider()


def render_project_upload_form(on_submit_callback=None) -> Optional[Dict]:
    """Render project upload form.

    Args:
        on_submit_callback: Function to call on form submission

    Returns:
        Project data dictionary if submitted
    """
    with st.form("upload_project_form"):
        st.subheader("Upload New Project")

        project_title = st.text_input(
            "Project Title *",
            placeholder="E-Commerce Recommendation System"
        )

        readme_file = st.file_uploader(
            "Upload README.md *",
            type=['md', 'txt'],
            help="Upload your project's README file"
        )

        col1, col2 = st.columns(2)

        with col1:
            github_url = st.text_input(
                "GitHub URL (Optional)",
                placeholder="https://github.com/username/project"
            )

        with col2:
            demo_url = st.text_input(
                "Demo URL (Optional)",
                placeholder="https://demo.example.com"
            )

        upload = st.form_submit_button("Upload Project", use_container_width=True)

        if upload:
            if not project_title:
                st.error("Please enter a project title")
                return None
            elif not readme_file:
                st.error("Please upload a README file")
                return None
            else:
                try:
                    # Read README content
                    readme_content = readme_file.read().decode('utf-8')

                    project_data = {
                        'title': project_title,
                        'readme_content': readme_content,
                        'github_url': github_url if github_url else None,
                        'demo_url': demo_url if demo_url else None
                    }

                    if on_submit_callback:
                        on_submit_callback(project_data)

                    return project_data

                except Exception as e:
                    st.error(f"Failed to read README file: {e}")
                    return None

    return None
