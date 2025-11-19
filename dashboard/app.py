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

            if st.button("📋 Search Results", use_container_width=True):
                st.session_state['page'] = 'results'
                st.rerun()

            if st.button("📊 My Applications", use_container_width=True):
                st.session_state['page'] = 'applications'
                st.rerun()

            if st.button("📈 Analytics", use_container_width=True):
                st.session_state['page'] = 'analytics'
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
    st.title("🔍 Job Search")

    user = st.session_state.get('user')

    # Check if profile exists
    from database.db_manager import db_manager
    profile = db_manager.get_profile(user['id'])

    if not profile:
        st.warning("⚠️ Please create your profile first before searching for jobs!")
        if st.button("Go to Profile Page"):
            st.session_state['page'] = 'profile'
            st.rerun()
        return

    # Import components
    from dashboard.components.filters import render_job_search_form

    # Render search form
    search_params = render_job_search_form(
        default_values=st.session_state.get('last_search_params')
    )

    if search_params:
        # Save search params
        st.session_state['last_search_params'] = search_params

        st.divider()
        st.subheader("🔄 Searching for Jobs...")

        # Progress indicators
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            # Step 1: Scrape jobs
            status_text.text("Step 1/4: Scraping job boards...")
            progress_bar.progress(25)

            from scrapers.scraper_factory import scraper_factory
            scraper_factory.initialize()

            jobs = []

            if search_params['sources']:
                # Scrape from selected sources
                scraped_jobs = scraper_factory.scrape_all_sources(
                    keywords=search_params['keywords'],
                    location=search_params['location'],
                    sources=search_params['sources'],
                    job_type=search_params['job_types'][0] if search_params['job_types'] else None,
                    max_results=search_params['num_results'],
                    auto_embed=True,
                    auto_save_db=True
                )
                jobs.extend(scraped_jobs)

            # Add cached jobs if requested
            if search_params.get('use_cached'):
                cached_jobs = db_manager.get_recent_jobs(
                    max_age_days=search_params['max_age_days'],
                    limit=search_params['num_results']
                )
                jobs.extend(cached_jobs)

            status_text.text(f"Step 2/4: Found {len(jobs)} jobs, filtering...")
            progress_bar.progress(50)

            # Step 2: Filter jobs
            from processing.filter_engine import filter_engine
            filter_engine.initialize()

            filtered_jobs = filter_engine.filter_jobs(
                jobs=jobs,
                keywords=search_params['keywords'],
                location=search_params['location'],
                job_types=search_params['job_types'],
                max_age_days=search_params['max_age_days'],
                language=search_params.get('language')
            )

            status_text.text(f"Step 3/4: Ranking {len(filtered_jobs)} jobs with RAG...")
            progress_bar.progress(75)

            # Step 3: RAG ranking
            from processing.rag_ranker import rag_ranker
            rag_ranker.initialize()

            ranked_jobs = rag_ranker.rank_jobs(
                user_id=user['id'],
                jobs=filtered_jobs,
                top_n=search_params['num_results']
            )

            status_text.text("Step 4/4: Selecting relevant projects...")
            progress_bar.progress(90)

            # Step 4: Select projects for each job
            from ai_generation.rag.project_selector import project_selector
            project_selector.initialize()

            for job in ranked_jobs:
                selected_projects = project_selector.select_relevant_projects(
                    user_id=user['id'],
                    job=job,
                    max_projects=st.session_state.get('cv_preferences', {}).get('max_projects_per_cv', 3)
                )
                job['selected_projects'] = selected_projects

            # Complete
            progress_bar.progress(100)
            status_text.text("✅ Search complete!")

            # Save results to session
            st.session_state['search_results'] = ranked_jobs
            st.session_state['search_metadata'] = {
                'total_scraped': len(jobs),
                'total_filtered': len(filtered_jobs),
                'total_ranked': len(ranked_jobs),
                'search_params': search_params
            }

            st.success(f"🎉 Found {len(ranked_jobs)} matching jobs!")

            # Auto-navigate to results
            if st.button("📊 View Results", type="primary", use_container_width=True):
                st.session_state['page'] = 'results'
                st.rerun()

        except Exception as e:
            st.error(f"❌ Search failed: {str(e)}")
            import traceback
            with st.expander("Error Details"):
                st.code(traceback.format_exc())


def show_results_page():
    """Display search results page."""
    st.title("📋 Search Results")

    # Check if we have search results
    search_results = st.session_state.get('search_results')
    search_metadata = st.session_state.get('search_metadata')

    if not search_results:
        st.info("No search results yet. Please run a job search first!")
        if st.button("Go to Job Search"):
            st.session_state['page'] = 'search'
            st.rerun()
        return

    # Display search summary
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Jobs Scraped", search_metadata.get('total_scraped', 0))
    with col2:
        st.metric("After Filtering", search_metadata.get('total_filtered', 0))
    with col3:
        st.metric("Top Matches", search_metadata.get('total_ranked', 0))
    with col4:
        avg_score = sum(j.get('match_score', 0) for j in search_results) / len(search_results) if search_results else 0
        st.metric("Avg Match Score", f"{avg_score:.0f}%")

    st.divider()

    # Import components
    from dashboard.components.job_card import render_job_list, render_job_details_modal
    from dashboard.components.filters import render_results_filters, apply_filters_to_jobs

    # Filters sidebar
    filters = render_results_filters(
        total_jobs=len(search_results),
        current_filters=st.session_state.get('results_filters')
    )
    st.session_state['results_filters'] = filters

    # Apply filters
    filtered_results = apply_filters_to_jobs(search_results, filters)

    st.subheader(f"Showing {len(filtered_results)} Jobs")

    # Callbacks for job actions
    def handle_generate_cv(job):
        """Handle CV generation for a job."""
        st.session_state['selected_job_for_cv'] = job
        st.session_state['show_cv_generator'] = True
        st.rerun()

    def handle_view_details(job):
        """Handle viewing job details."""
        st.session_state['selected_job_details'] = job
        st.rerun()

    # Show CV generator if triggered
    if st.session_state.get('show_cv_generator'):
        job = st.session_state.get('selected_job_for_cv')

        with st.expander("📄 Generate CV", expanded=True):
            st.write(f"**Generating CV for:** {job.get('job_title')} at {job.get('company_name')}")

            use_llm = st.checkbox("Use LLM (Groq API)", value=False,
                                 help="Generate with AI (requires Groq API key)")

            if st.button("Generate CV", type="primary"):
                try:
                    user = st.session_state.get('user')
                    cv_prefs = st.session_state.get('cv_preferences', {
                        'cv_length': 1,
                        'include_projects': True,
                        'max_projects_per_cv': 3
                    })

                    with st.spinner("Generating CV..."):
                        from ai_generation.cv_generator import cv_generator
                        cv_generator.initialize()

                        cv_result = cv_generator.generate_cv(
                            user_id=user['id'],
                            job=job,
                            cv_preferences=cv_prefs,
                            use_llm=use_llm
                        )

                        st.success("✅ CV Generated!")
                        st.text_area("CV Content", cv_result['content'], height=400)

                        # Save to applications
                        st.session_state['generated_cvs'] = st.session_state.get('generated_cvs', [])
                        st.session_state['generated_cvs'].append({
                            'job': job,
                            'cv': cv_result,
                            'generated_at': datetime.utcnow()
                        })

                except Exception as e:
                    st.error(f"Failed to generate CV: {e}")
                    import traceback
                    with st.expander("Error Details"):
                        st.code(traceback.format_exc())

            if st.button("Close"):
                st.session_state['show_cv_generator'] = False
                st.rerun()

    # Show job details modal if triggered
    if st.session_state.get('selected_job_details'):
        job = st.session_state['selected_job_details']

        with st.expander("ℹ️ Job Details", expanded=True):
            render_job_details_modal(job)

            if st.button("Close Details"):
                st.session_state['selected_job_details'] = None
                st.rerun()

    # Export buttons
    st.divider()
    export_cols = st.columns(3)

    with export_cols[0]:
        if st.button("📥 Export to CSV", use_container_width=True):
            try:
                from output.csv_exporter import csv_exporter
                csv_path = csv_exporter.export_search_results(filtered_results)
                st.success(f"✅ Exported to: {csv_path.name}")
                st.download_button(
                    "⬇️ Download CSV",
                    data=open(csv_path, 'rb').read(),
                    file_name=csv_path.name,
                    mime='text/csv',
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Export failed: {e}")

    with export_cols[1]:
        if st.button("📊 Export to Excel", use_container_width=True):
            try:
                from output.excel_exporter import excel_exporter
                excel_path = excel_exporter.export_simple_excel(
                    [{'Rank': i+1, **job} for i, job in enumerate(filtered_results)],
                    sheet_name="Job Search Results"
                )
                st.success(f"✅ Exported to: {excel_path.name}")
                st.download_button(
                    "⬇️ Download Excel",
                    data=open(excel_path, 'rb').read(),
                    file_name=excel_path.name,
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Export failed: {e}")

    with export_cols[2]:
        st.write("")  # Placeholder for future export option

    st.divider()

    # Render job list
    render_job_list(
        jobs=filtered_results,
        show_actions=True,
        on_generate_cv=handle_generate_cv,
        on_view_details=handle_view_details
    )


def show_applications_page():
    """Display applications page."""
    st.title("📊 My Applications")

    user = st.session_state.get('user')
    generated_cvs = st.session_state.get('generated_cvs', [])

    if not generated_cvs:
        st.info("No applications yet. Generate CVs from search results to track them here!")
        if st.button("Go to Search"):
            st.session_state['page'] = 'search'
            st.rerun()
        return

    # Summary stats
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Applications", len(generated_cvs))
    with col2:
        this_week = len([cv for cv in generated_cvs
                        if (datetime.utcnow() - cv['generated_at']).days < 7])
        st.metric("This Week", this_week)
    with col3:
        avg_match = sum(cv['job'].get('match_score', 0) for cv in generated_cvs) / len(generated_cvs)
        st.metric("Avg Match Score", f"{avg_match:.0f}%")

    st.divider()

    # Export buttons
    export_cols = st.columns(3)

    with export_cols[0]:
        if st.button("📥 Export Applications to CSV", use_container_width=True):
            try:
                from output.csv_exporter import csv_exporter
                csv_path = csv_exporter.export_applications(generated_cvs)
                st.success(f"✅ Exported to: {csv_path.name}")
                st.download_button(
                    "⬇️ Download CSV",
                    data=open(csv_path, 'rb').read(),
                    file_name=csv_path.name,
                    mime='text/csv',
                    use_container_width=True,
                    key="download_apps_csv"
                )
            except Exception as e:
                st.error(f"Export failed: {e}")

    with export_cols[1]:
        if st.button("📊 Comprehensive Excel Report", use_container_width=True):
            try:
                from output.excel_exporter import excel_exporter
                from database.db_manager import db_manager

                # Gather all data
                search_results = st.session_state.get('search_results', [])
                projects = db_manager.get_user_projects(user['id'])

                # Calculate project usage stats
                project_usage = {}
                for app in generated_cvs:
                    for proj_id in app.get('cv', {}).get('metadata', {}).get('projects_included', []):
                        project_usage[str(proj_id)] = project_usage.get(str(proj_id), 0) + 1

                # Calculate skill counts
                skill_counts = {}
                for job in search_results:
                    for skill in job.get('required_skills', []):
                        skill_counts[skill] = skill_counts.get(skill, 0) + 1

                profile = db_manager.get_profile(user['id'])
                user_skills = profile.get('skills', []) if profile else []

                excel_path = excel_exporter.export_comprehensive_report(
                    search_results=search_results,
                    applications=generated_cvs,
                    projects=projects,
                    usage_stats=project_usage,
                    skill_counts=skill_counts,
                    user_skills=user_skills,
                    user_name=user['full_name']
                )

                st.success(f"✅ Comprehensive report generated: {excel_path.name}")
                st.download_button(
                    "⬇️ Download Excel Report",
                    data=open(excel_path, 'rb').read(),
                    file_name=excel_path.name,
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    use_container_width=True,
                    key="download_apps_excel"
                )
            except Exception as e:
                st.error(f"Export failed: {e}")
                import traceback
                with st.expander("Error Details"):
                    st.code(traceback.format_exc())

    with export_cols[2]:
        st.write("")  # Placeholder

    st.divider()

    # List applications
    st.subheader("Generated CVs")

    for i, app in enumerate(reversed(generated_cvs)):
        job = app['job']
        cv = app['cv']
        generated_at = app['generated_at']

        with st.expander(f"#{len(generated_cvs) - i} - {job.get('job_title')} at {job.get('company_name')}"):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.write(f"**Match Score:** {job.get('match_score', 0)}%")
                st.write(f"**Location:** {job.get('location', 'N/A')}")
                st.write(f"**Generated:** {generated_at.strftime('%Y-%m-%d %H:%M')}")

            with col2:
                if job.get('url'):
                    st.markdown(f"[🔗 View Job]({job['url']})")

            st.divider()

            # CV content
            st.text_area("CV Content", cv['content'], height=300, key=f"cv_{i}")

            # Metadata
            if cv.get('metadata'):
                with st.expander("CV Metadata"):
                    st.json(cv['metadata'])


def show_analytics_page():
    """Display analytics page."""
    st.title("📈 Analytics & Insights")

    user = st.session_state.get('user')

    # Get data
    from database.db_manager import db_manager
    profile = db_manager.get_profile(user['id'])
    projects = db_manager.get_user_projects(user['id'])
    generated_cvs = st.session_state.get('generated_cvs', [])
    search_results = st.session_state.get('search_results', [])

    if not profile:
        st.info("Create your profile first to see analytics!")
        return

    # Overview stats
    st.subheader("📊 Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Projects", len(projects))
    with col2:
        st.metric("Skills", len(profile.get('skills', [])))
    with col3:
        st.metric("Applications", len(generated_cvs))
    with col4:
        if search_results:
            avg_match = sum(j.get('match_score', 0) for j in search_results) / len(search_results)
            st.metric("Avg Match", f"{avg_match:.0f}%")
        else:
            st.metric("Avg Match", "N/A")

    st.divider()

    # Project Performance
    if projects:
        st.subheader("🎯 Project Performance")

        st.write("This shows how often each project was selected for job applications.")

        # Count project usage
        project_usage = {}
        for app in generated_cvs:
            if app.get('cv', {}).get('metadata', {}).get('projects_included'):
                for proj_id in app['cv']['metadata']['projects_included']:
                    project_usage[proj_id] = project_usage.get(proj_id, 0) + 1

        if project_usage:
            # Create chart data
            project_names = []
            usage_counts = []

            for proj in projects:
                proj_id = proj.get('id')
                project_names.append(proj.get('title', 'Unknown')[:30])
                usage_counts.append(project_usage.get(str(proj_id), 0))

            import pandas as pd
            chart_data = pd.DataFrame({
                'Project': project_names,
                'Times Used': usage_counts
            })

            st.bar_chart(chart_data.set_index('Project'))
        else:
            st.info("Generate some CVs to see project usage statistics!")

    st.divider()

    # Skills Gap Analysis
    st.subheader("🔍 Skills Gap Analysis")

    if search_results:
        # Count required skills from jobs
        skill_counts = {}
        for job in search_results:
            for skill in job.get('required_skills', []):
                skill_counts[skill] = skill_counts.get(skill, 0) + 1

        # Find top requested skills
        top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:15]

        # Check which skills user has
        user_skills = set(s.lower() for s in profile.get('skills', []))

        st.write("**Top Skills in Job Market:**")

        for skill, count in top_skills:
            has_skill = skill.lower() in user_skills
            emoji = "✅" if has_skill else "❌"
            pct = (count / len(search_results)) * 100

            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"{emoji} **{skill}**")
            with col2:
                st.write(f"{count} jobs")
            with col3:
                st.write(f"{pct:.0f}%")

        st.divider()

        # Recommend skills to learn
        missing_skills = [skill for skill, _ in top_skills if skill.lower() not in user_skills]

        if missing_skills:
            st.write("**💡 Recommended Skills to Learn:**")
            for skill in missing_skills[:5]:
                st.write(f"- {skill}")
        else:
            st.success("🎉 You have all top requested skills!")

    else:
        st.info("Run a job search to see skills gap analysis!")

    st.divider()

    # Match Score Distribution
    if search_results:
        st.subheader("📊 Match Score Distribution")

        scores = [j.get('match_score', 0) for j in search_results]

        # Create bins
        bins = [0, 20, 40, 60, 80, 100]
        bin_labels = ['0-20%', '21-40%', '41-60%', '61-80%', '81-100%']
        bin_counts = [0] * 5

        for score in scores:
            for i in range(len(bins) - 1):
                if bins[i] <= score < bins[i + 1]:
                    bin_counts[i] += 1
                    break
            if score == 100:
                bin_counts[-1] += 1

        import pandas as pd
        dist_data = pd.DataFrame({
            'Score Range': bin_labels,
            'Jobs': bin_counts
        })

        st.bar_chart(dist_data.set_index('Score Range'))

    st.divider()

    # Recent Activity
    st.subheader("📅 Recent Activity")

    if generated_cvs:
        st.write("**Last 5 Applications:**")

        for app in list(reversed(generated_cvs))[:5]:
            job = app['job']
            generated_at = app['generated_at']

            col1, col2, col3 = st.columns([3, 1, 1])

            with col1:
                st.write(f"**{job.get('job_title')}** at {job.get('company_name')}")
            with col2:
                st.write(f"{job.get('match_score', 0)}% match")
            with col3:
                days_ago = (datetime.utcnow() - generated_at).days
                if days_ago == 0:
                    st.write("Today")
                else:
                    st.write(f"{days_ago}d ago")

    else:
        st.info("No activity yet!")


def show_settings_page():
    """Display settings page."""
    st.title("⚙️ Settings")

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
        elif page == 'results':
            show_results_page()
        elif page == 'applications':
            show_applications_page()
        elif page == 'analytics':
            show_analytics_page()
        elif page == 'settings':
            show_settings_page()
        else:
            show_dashboard_page()


if __name__ == "__main__":
    main()
