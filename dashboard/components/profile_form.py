"""Profile form component."""

import streamlit as st
from typing import Dict, Optional


def render_profile_form(
    initial_data: Optional[Dict] = None,
    on_submit_callback=None
) -> Dict:
    """Render profile creation/edit form.

    Args:
        initial_data: Existing profile data (for edit mode)
        on_submit_callback: Function to call on form submission

    Returns:
        Form data dictionary
    """
    is_edit = initial_data is not None

    with st.form("profile_form"):
        st.subheader("Profile Information")

        # Skills
        st.write("**Skills**")
        skills_default = '\n'.join(initial_data.get('skills', [])) if is_edit else ""
        skills_input = st.text_area(
            "Enter your skills (one per line)",
            value=skills_default,
            placeholder="Python\nMachine Learning\nReact\nSQL",
            help="List your technical and professional skills"
        )

        st.divider()

        # Experience
        st.write("**Experience**")
        num_exp = st.number_input(
            "Number of experiences to add",
            min_value=0,
            max_value=10,
            value=1 if not is_edit else len(initial_data.get('experience', [])),
            help="How many work experiences do you want to add?"
        )

        experiences = []
        for i in range(int(num_exp)):
            st.write(f"Experience {i + 1}")
            exp_data = initial_data.get('experience', [])[i] if is_edit and i < len(initial_data.get('experience', [])) else {}

            col1, col2 = st.columns(2)
            with col1:
                title = st.text_input(
                    "Job Title",
                    value=exp_data.get('title', ''),
                    key=f"exp_title_{i}"
                )
            with col2:
                company = st.text_input(
                    "Company",
                    value=exp_data.get('company', ''),
                    key=f"exp_company_{i}"
                )

            duration = st.text_input(
                "Duration",
                value=exp_data.get('duration', ''),
                placeholder="6 months (Jan 2024 - Jun 2024)",
                key=f"exp_duration_{i}"
            )

            description = st.text_area(
                "Description (Optional)",
                value=exp_data.get('description', ''),
                key=f"exp_desc_{i}"
            )

            if title and company:
                experiences.append({
                    'title': title,
                    'company': company,
                    'duration': duration,
                    'description': description
                })

        st.divider()

        # Education
        st.write("**Education**")
        num_edu = st.number_input(
            "Number of education entries",
            min_value=0,
            max_value=5,
            value=1 if not is_edit else (1 if initial_data.get('education') else 0),
            help="How many degrees/certifications to add?"
        )

        education = []
        for i in range(int(num_edu)):
            st.write(f"Education {i + 1}")
            edu_data = initial_data.get('education', {}) if is_edit and i == 0 else {}

            col1, col2 = st.columns(2)
            with col1:
                degree = st.text_input(
                    "Degree/Certification",
                    value=edu_data.get('degree', ''),
                    placeholder="Master in Computer Science",
                    key=f"edu_degree_{i}"
                )
            with col2:
                institution = st.text_input(
                    "Institution",
                    value=edu_data.get('institution', ''),
                    placeholder="University of Paris",
                    key=f"edu_institution_{i}"
                )

            col3, col4 = st.columns(2)
            with col3:
                year = st.number_input(
                    "Year",
                    min_value=1980,
                    max_value=2030,
                    value=edu_data.get('year', 2024),
                    key=f"edu_year_{i}"
                )
            with col4:
                field = st.text_input(
                    "Field (Optional)",
                    value=edu_data.get('field', ''),
                    placeholder="Computer Science",
                    key=f"edu_field_{i}"
                )

            if degree and institution:
                education.append({
                    'degree': degree,
                    'institution': institution,
                    'year': year,
                    'field': field
                })

        st.divider()

        # Languages
        st.write("**Languages**")
        languages_default = '\n'.join(initial_data.get('languages', [])) if is_edit else ""
        languages_input = st.text_area(
            "Languages (one per line)",
            value=languages_default,
            placeholder="English (Fluent)\nFrench (Native)",
            help="List languages and proficiency levels"
        )

        # Submit button
        submit = st.form_submit_button(
            "Update Profile" if is_edit else "Create Profile",
            use_container_width=True
        )

        if submit:
            # Parse inputs
            skills = [s.strip() for s in skills_input.split('\n') if s.strip()]
            languages = [l.strip() for l in languages_input.split('\n') if l.strip()]

            profile_data = {
                'skills': skills,
                'experience': experiences,
                'education': education[0] if education else {},
                'languages': languages
            }

            if on_submit_callback:
                on_submit_callback(profile_data)

            return profile_data

    return {}
