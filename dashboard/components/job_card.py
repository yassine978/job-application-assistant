"""Job card component for displaying job postings."""

import streamlit as st
from typing import Dict, Optional, Callable
from datetime import datetime, timedelta


def render_job_card(
    job: Dict,
    rank: Optional[int] = None,
    show_actions: bool = True,
    on_generate_cv: Optional[Callable] = None,
    on_view_details: Optional[Callable] = None
) -> None:
    """Render a job posting card.

    Args:
        job: Job data dictionary
        rank: Job rank/position in list
        show_actions: Whether to show action buttons
        on_generate_cv: Callback for CV generation
        on_view_details: Callback for viewing details
    """
    with st.container():
        # Header row
        col1, col2, col3 = st.columns([6, 2, 2])

        with col1:
            if rank:
                st.markdown(f"### #{rank} - {job.get('job_title', 'Unknown Position')}")
            else:
                st.markdown(f"### {job.get('job_title', 'Unknown Position')}")

        with col2:
            # Match score badge
            if job.get('match_score'):
                score = job['match_score']
                color = "green" if score >= 80 else "orange" if score >= 60 else "red"
                st.markdown(
                    f"<div style='text-align: center; padding: 5px; background-color: {color}; "
                    f"color: white; border-radius: 5px; font-weight: bold;'>"
                    f"{score}% Match</div>",
                    unsafe_allow_html=True
                )

        with col3:
            # Job type badge
            job_type = job.get('job_type', 'Unknown')
            st.markdown(
                f"<div style='text-align: center; padding: 5px; background-color: #e0e0e0; "
                f"border-radius: 5px; font-size: 12px;'>{job_type}</div>",
                unsafe_allow_html=True
            )

        # Company and location
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Company:** {job.get('company_name', 'N/A')}")
        with col2:
            st.write(f"**Location:** {job.get('location', 'N/A')}")

        # Description preview
        description = job.get('description', '')
        if description:
            preview = description[:200] + "..." if len(description) > 200 else description
            st.write(preview)

        # Skills/Requirements
        if job.get('required_skills'):
            st.write("**Required Skills:**")
            skills = job['required_skills'][:8]  # Show first 8 skills
            skills_cols = st.columns(min(len(skills), 4))
            for i, skill in enumerate(skills):
                with skills_cols[i % 4]:
                    st.markdown(
                        f"<span style='background-color: #f0f0f0; padding: 2px 6px; "
                        f"border-radius: 3px; font-size: 11px;'>{skill}</span>",
                        unsafe_allow_html=True
                    )
            if len(job.get('required_skills', [])) > 8:
                st.caption(f"+{len(job['required_skills']) - 8} more skills")

        # Additional info row
        info_cols = st.columns(4)

        with info_cols[0]:
            if job.get('salary'):
                st.caption(f"💰 {job['salary']}")

        with info_cols[1]:
            if job.get('posted_date'):
                posted = job['posted_date']
                if isinstance(posted, str):
                    st.caption(f"📅 {posted}")
                elif isinstance(posted, datetime):
                    days_ago = (datetime.utcnow() - posted).days
                    if days_ago == 0:
                        st.caption("📅 Today")
                    elif days_ago == 1:
                        st.caption("📅 Yesterday")
                    else:
                        st.caption(f"📅 {days_ago} days ago")

        with info_cols[2]:
            if job.get('source'):
                st.caption(f"🔗 {job['source']}")

        with info_cols[3]:
            if job.get('language'):
                st.caption(f"🌐 {job['language']}")

        # RAG insights (if available)
        if job.get('selected_projects'):
            st.write("**🎯 Relevant Projects:**")
            for proj in job['selected_projects'][:2]:
                st.write(f"- {proj.get('title', 'Unnamed')} ({proj.get('relevance_score', 0):.0%} match)")

        if job.get('semantic_similarity'):
            st.caption(f"Semantic Similarity: {job['semantic_similarity']:.1%}")

        # Action buttons
        if show_actions:
            btn_cols = st.columns([2, 2, 2, 4])

            with btn_cols[0]:
                if st.button("📄 Generate CV", key=f"cv_{job.get('id')}", use_container_width=True):
                    if on_generate_cv:
                        on_generate_cv(job)

            with btn_cols[1]:
                if st.button("📝 Cover Letter", key=f"cl_{job.get('id')}", use_container_width=True):
                    st.info("Cover letter generation coming soon!")

            with btn_cols[2]:
                if st.button("ℹ️ Details", key=f"details_{job.get('id')}", use_container_width=True):
                    if on_view_details:
                        on_view_details(job)

        st.divider()


def render_job_list(
    jobs: list,
    start_rank: int = 1,
    show_actions: bool = True,
    on_generate_cv: Optional[Callable] = None,
    on_view_details: Optional[Callable] = None
) -> None:
    """Render a list of job cards.

    Args:
        jobs: List of job dictionaries
        start_rank: Starting rank number
        show_actions: Whether to show action buttons
        on_generate_cv: Callback for CV generation
        on_view_details: Callback for viewing details
    """
    if not jobs:
        st.info("No jobs to display")
        return

    for i, job in enumerate(jobs):
        render_job_card(
            job=job,
            rank=start_rank + i,
            show_actions=show_actions,
            on_generate_cv=on_generate_cv,
            on_view_details=on_view_details
        )


def render_job_details_modal(job: Dict) -> None:
    """Render detailed job information in a modal/expander.

    Args:
        job: Job data dictionary
    """
    st.subheader(f"{job.get('job_title', 'Job Details')}")

    # Company info
    st.write(f"**Company:** {job.get('company_name', 'N/A')}")
    st.write(f"**Location:** {job.get('location', 'N/A')}")
    st.write(f"**Job Type:** {job.get('job_type', 'N/A')}")

    if job.get('salary'):
        st.write(f"**Salary:** {job['salary']}")

    st.divider()

    # Full description
    st.subheader("Description")
    st.write(job.get('description', 'No description available'))

    st.divider()

    # Requirements
    if job.get('required_skills'):
        st.subheader("Required Skills")
        for skill in job['required_skills']:
            st.write(f"- {skill}")

    # URL
    if job.get('url'):
        st.divider()
        st.markdown(f"[🔗 View Original Posting]({job['url']})")

    # RAG insights
    if job.get('match_score') or job.get('selected_projects'):
        st.divider()
        st.subheader("Match Analysis")

        if job.get('match_score'):
            st.metric("Match Score", f"{job['match_score']}%")

        if job.get('semantic_similarity'):
            st.metric("Semantic Similarity", f"{job['semantic_similarity']:.1%}")

        if job.get('selected_projects'):
            st.write("**Recommended Projects to Highlight:**")
            for proj in job['selected_projects']:
                st.write(f"- **{proj.get('title')}** ({proj.get('relevance_score', 0):.0%} relevance)")
                if proj.get('matching_techs'):
                    st.caption(f"  Matching: {', '.join(proj['matching_techs'][:5])}")
