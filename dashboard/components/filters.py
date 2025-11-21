"""Filters component for job search."""

import streamlit as st
from typing import Dict, List, Optional


def render_job_search_form(
    default_values: Optional[Dict] = None
) -> Optional[Dict]:
    """Render job search form with filters.

    Args:
        default_values: Default form values

    Returns:
        Search parameters dictionary if submitted, None otherwise
    """
    defaults = default_values or {}

    with st.form("job_search_form"):
        st.subheader("🔍 Search Jobs")

        # Keywords
        keywords = st.text_input(
            "Keywords / Job Title",
            value=defaults.get('keywords', ''),
            placeholder="Data Scientist, ML Engineer, Python Developer",
            help="Enter job titles or keywords separated by commas"
        )

        # Location and job type
        col1, col2 = st.columns(2)

        with col1:
            location = st.text_input(
                "Location",
                value=defaults.get('location', 'Paris'),
                placeholder="Paris, Remote, London"
            )

        with col2:
            job_types = st.multiselect(
                "Job Type",
                options=['Full-time', 'Part-time', 'Internship', 'Contract', 'Remote'],
                default=defaults.get('job_types', ['Full-time'])
            )

        # Advanced filters (collapsible)
        with st.expander("Advanced Filters"):
            col1, col2 = st.columns(2)

            with col1:
                max_age_days = st.slider(
                    "Posted Within (Days)",
                    min_value=1,
                    max_value=30,
                    value=defaults.get('max_age_days', 7),
                    help="Only show jobs posted within this many days"
                )

                min_match_score = st.slider(
                    "Minimum Match Score (%)",
                    min_value=0,
                    max_value=100,
                    value=defaults.get('min_match_score', 50),
                    help="Only show jobs with at least this match score"
                )

            with col2:
                language = st.selectbox(
                    "Language",
                    options=['Any', 'English', 'French', 'German', 'Spanish'],
                    index=0 if not defaults.get('language') else ['Any', 'English', 'French', 'German', 'Spanish'].index(defaults.get('language', 'Any'))
                )

                num_results = st.number_input(
                    "Max Results",
                    min_value=5,
                    max_value=100,
                    value=defaults.get('num_results', 20),
                    step=5
                )

        # Source selection
        st.write("**Data Sources:**")
        source_cols = st.columns(4)

        with source_cols[0]:
            use_linkedin = st.checkbox(
                "LinkedIn",
                value=defaults.get('use_linkedin', True),
                help="Scrape public jobs from LinkedIn (no login)"
            )

        with source_cols[1]:
            use_wttj = st.checkbox(
                "Welcome to the Jungle",
                value=defaults.get('use_wttj', True),
                help="Scrape from Welcome to the Jungle"
            )

        with source_cols[2]:
            use_adzuna = st.checkbox(
                "Adzuna API",
                value=defaults.get('use_adzuna', True),
                help="Fetch from Adzuna API"
            )

        with source_cols[3]:
            use_cached = st.checkbox(
                "Use Cached Jobs",
                value=defaults.get('use_cached', False),
                help="Include previously scraped jobs from database"
            )

        # Submit button
        submitted = st.form_submit_button(
            "🚀 Search Jobs",
            use_container_width=True,
            type="primary"
        )

        if submitted:
            # Build sources list
            sources = []
            if use_linkedin:
                sources.append('linkedin')
            if use_wttj:
                sources.append('welcome')
            if use_adzuna:
                sources.append('adzuna')

            return {
                'keywords': keywords,
                'location': location,
                'job_types': job_types,
                'max_age_days': max_age_days,
                'min_match_score': min_match_score,
                'language': language if language != 'Any' else None,
                'num_results': num_results,
                'sources': sources,
                'use_cached': use_cached
            }

    return None


def render_results_filters(
    total_jobs: int,
    current_filters: Optional[Dict] = None
) -> Dict:
    """Render filters for search results.

    Args:
        total_jobs: Total number of jobs
        current_filters: Current filter values

    Returns:
        Updated filter dictionary
    """
    filters = current_filters or {}

    st.sidebar.header("Filter Results")

    # Sort options
    sort_by = st.sidebar.selectbox(
        "Sort By",
        options=['Match Score (High to Low)', 'Match Score (Low to High)',
                 'Date (Newest First)', 'Date (Oldest First)',
                 'Salary (High to Low)', 'Salary (Low to High)'],
        index=0
    )

    # Match score filter
    min_score = st.sidebar.slider(
        "Minimum Match Score",
        min_value=0,
        max_value=100,
        value=filters.get('min_score', 0),
        help="Filter jobs by minimum match score"
    )

    # Job type filter
    st.sidebar.write("**Job Types:**")
    filter_fulltime = st.sidebar.checkbox("Full-time", value=True)
    filter_parttime = st.sidebar.checkbox("Part-time", value=True)
    filter_internship = st.sidebar.checkbox("Internship", value=True)
    filter_contract = st.sidebar.checkbox("Contract", value=True)

    job_types = []
    if filter_fulltime:
        job_types.append('Full-time')
    if filter_parttime:
        job_types.append('Part-time')
    if filter_internship:
        job_types.append('Internship')
    if filter_contract:
        job_types.append('Contract')

    # Location filter
    filter_remote = st.sidebar.checkbox("Remote Only", value=False)

    # Results count
    st.sidebar.metric("Total Jobs", total_jobs)

    return {
        'sort_by': sort_by,
        'min_score': min_score,
        'job_types': job_types,
        'remote_only': filter_remote
    }


def apply_filters_to_jobs(jobs: List[Dict], filters: Dict) -> List[Dict]:
    """Apply filters to job list.

    Args:
        jobs: List of job dictionaries
        filters: Filter parameters

    Returns:
        Filtered job list
    """
    filtered = jobs.copy()

    # Filter by match score
    if filters.get('min_score', 0) > 0:
        filtered = [j for j in filtered if j.get('match_score', 0) >= filters['min_score']]

    # Filter by job type
    if filters.get('job_types'):
        filtered = [j for j in filtered if j.get('job_type') in filters['job_types']]

    # Filter remote only
    if filters.get('remote_only'):
        filtered = [j for j in filtered if 'remote' in j.get('location', '').lower()]

    # Sort
    sort_by = filters.get('sort_by', 'Match Score (High to Low)')

    if sort_by == 'Match Score (High to Low)':
        filtered.sort(key=lambda x: x.get('match_score', 0), reverse=True)
    elif sort_by == 'Match Score (Low to High)':
        filtered.sort(key=lambda x: x.get('match_score', 0))
    elif sort_by == 'Date (Newest First)':
        filtered.sort(key=lambda x: x.get('posted_date', ''), reverse=True)
    elif sort_by == 'Date (Oldest First)':
        filtered.sort(key=lambda x: x.get('posted_date', ''))
    elif sort_by == 'Salary (High to Low)':
        filtered.sort(key=lambda x: x.get('salary_max', 0), reverse=True)
    elif sort_by == 'Salary (Low to High)':
        filtered.sort(key=lambda x: x.get('salary_max', 0))

    return filtered
