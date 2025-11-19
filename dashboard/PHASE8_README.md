# Phase 8: Complete Streamlit Dashboard - User Guide

## Overview

Phase 8 completes the full-featured Streamlit dashboard with job search, RAG-powered ranking, CV generation, and analytics.

## New Features (Phase 8)

### 1. **Job Search Page** 🔍
- **Complete search form** with keywords, location, job type filters
- **Multi-source scraping**: Welcome to the Jungle + Adzuna API
- **Advanced filters**: Posted date, match score, language, max results
- **Real-time progress** indicators during search
- **4-stage pipeline**:
  1. Scrape jobs from selected sources
  2. Filter by criteria
  3. RAG ranking with match scores
  4. Project selection for each job

### 2. **Search Results Page** 📋
- **Results summary** with metrics (scraped, filtered, ranked, avg match)
- **Interactive job cards** with match scores, skills, salary
- **Sidebar filters**: Sort by match/date/salary, job type, remote filter
- **One-click CV generation** directly from results
- **Job details modal** with full description and RAG insights
- **Project recommendations** for each job

### 3. **Applications Tracking Page** 📊
- **Track all generated CVs** with job details
- **Summary statistics**: Total applications, this week, avg match score
- **View CV content** and metadata
- **Application history** with generation timestamps
- **Direct links** to original job postings

### 4. **Analytics & Insights Page** 📈
- **Overview dashboard**: Projects, skills, applications, avg match
- **Project performance**: Charts showing which projects were used most
- **Skills gap analysis**: Compare your skills vs market demand
- **Recommended skills** to learn based on job market
- **Match score distribution**: Visualize job match quality
- **Recent activity** timeline

### 5. **Enhanced UI Components**
- **Job cards** with color-coded match scores
- **Advanced filters** with multi-select options
- **Interactive charts** using pandas/Streamlit
- **Responsive layouts** with columns and metrics

## Complete Page Flow

```
Login/Register
    ↓
Dashboard (Home)
    ↓
Profile & Projects → Upload README → Auto-parse & embed
    ↓
Job Search → Enter criteria → Scrape & Rank → Project selection
    ↓
Search Results → Filter/Sort → View jobs → Generate CV
    ↓
Applications → Track generated CVs → View history
    ↓
Analytics → Insights, charts, recommendations
    ↓
Settings → Account, CV preferences
```

## Running the Complete Dashboard

### Prerequisites

```bash
# Install all dependencies
pip install streamlit pandas

# Initialize systems
python -c "from database.db_manager import db_manager; db_manager.initialize()"
python -c "from ai_generation.embeddings.vector_store import vector_store; vector_store.initialize()"
```

### Start Dashboard

```bash
streamlit run dashboard/app.py
```

## Page-by-Page Guide

### Job Search Page

**Purpose**: Search for jobs using multiple sources with RAG ranking

**Steps**:
1. Enter keywords (e.g., "Data Scientist, ML Engineer")
2. Set location (e.g., "Paris")
3. Select job types (Full-time, Internship, etc.)
4. Configure advanced filters (date range, match score, language)
5. Choose data sources (WTTJ, Adzuna, cached jobs)
6. Click "Search Jobs"
7. Wait for 4-stage pipeline to complete
8. Click "View Results" to see ranked jobs

**Behind the Scenes**:
```python
# Step 1: Scrape jobs
scraper_factory.scrape_all_sources(...)

# Step 2: Filter jobs
filter_engine.filter_jobs(...)

# Step 3: RAG ranking
rag_ranker.rank_jobs(user_id, jobs, top_n)

# Step 4: Select relevant projects
for job in ranked_jobs:
    job['selected_projects'] = project_selector.select_relevant_projects(...)
```

### Search Results Page

**Purpose**: View, filter, and act on search results

**Features**:
- **Metrics**: Jobs scraped, filtered, ranked, avg match score
- **Sidebar Filters**:
  - Sort by: Match score, date, salary
  - Filter by: Job type, remote only
  - Minimum match score slider
- **Job Cards**: Display all job details with RAG insights
- **Actions**:
  - "Generate CV": One-click CV generation
  - "Cover Letter": Coming soon
  - "Details": Full job description and analysis

**CV Generation Flow**:
```python
# When user clicks "Generate CV"
1. Select job → Open CV generator modal
2. Choose template or LLM mode
3. Click "Generate CV"
4. RAG pipeline builds context (profile + job + projects)
5. CV generator creates tailored CV
6. Display CV content
7. Save to Applications tracking
```

### Applications Page

**Purpose**: Track all generated CVs and applications

**Metrics**:
- Total applications
- Applications this week
- Average match score

**For Each Application**:
- Job title and company
- Match score
- Generation timestamp
- Link to original posting
- Full CV content
- CV metadata (projects included, generation method)

### Analytics Page

**Purpose**: Provide insights and recommendations

**Sections**:

1. **Overview Stats**
   - Total projects, skills, applications
   - Average match score

2. **Project Performance**
   - Bar chart showing usage frequency
   - Which projects were selected most often
   - Helps identify most valuable projects

3. **Skills Gap Analysis**
   - Top 15 skills in job market
   - Check marks for skills you have
   - Percentage of jobs requiring each skill
   - Top 5 recommended skills to learn

4. **Match Score Distribution**
   - Histogram of match scores (0-20%, 21-40%, etc.)
   - Shows quality of job matches

5. **Recent Activity**
   - Last 5 applications
   - Job titles, match scores, dates

## UI Components

### `job_card.py` (221 lines)

**Purpose**: Display job postings as interactive cards

**Key Functions**:
```python
render_job_card(job, rank, show_actions, on_generate_cv, on_view_details)
render_job_list(jobs, start_rank, show_actions, ...)
render_job_details_modal(job)
```

**Features**:
- Color-coded match score badges (green/orange/red)
- Job type, salary, location, date
- Skills with badges
- Selected projects display
- Action buttons (CV, Cover Letter, Details)

### `filters.py` (231 lines)

**Purpose**: Search and filter forms

**Key Functions**:
```python
render_job_search_form(default_values)
render_results_filters(total_jobs, current_filters)
apply_filters_to_jobs(jobs, filters)
```

**Search Form Fields**:
- Keywords, location, job types
- Advanced: Date range, match score, language, max results
- Sources: WTTJ, Adzuna, cached jobs

**Results Filters**:
- Sort options (match, date, salary)
- Job type checkboxes
- Match score slider
- Remote-only toggle

## Integration Architecture

### Phase 8 Integration Map

```
Phase 4 (Scrapers)
    ↓
Job Search Page → scraper_factory.scrape_all_sources()
    ↓
Phase 5 (Processing)
    ↓
filter_engine.filter_jobs() → rag_ranker.rank_jobs()
    ↓
Phase 6 (AI Generation)
    ↓
project_selector.select_relevant_projects()
cv_generator.generate_cv()
    ↓
Results Page → Applications Page → Analytics Page
```

## Session State Management

**Key Session Variables**:
```python
{
    'search_results': [],                   # Ranked jobs from last search
    'search_metadata': {...},               # Search statistics
    'last_search_params': {...},           # Re-fill search form
    'results_filters': {...},              # Persist filter state
    'generated_cvs': [],                    # Application history
    'selected_job_for_cv': {...},          # CV generation modal
    'selected_job_details': {...},         # Job details modal
    'show_cv_generator': False,            # Modal visibility
}
```

## Example Workflow

### Complete User Journey

```
1. User logs in
2. Creates profile (skills, experience, education)
3. Uploads 3 projects (README files auto-parsed)
4. Goes to Job Search
5. Searches for "ML Engineer" in "Paris"
6. System scrapes 50 jobs, filters to 30, ranks top 20
7. Selects 2-3 relevant projects for each job
8. User goes to Results
9. Sees 20 jobs ranked by match score (72% avg)
10. Clicks "Generate CV" on top job (85% match)
11. CV generated with 2 selected projects
12. Saves to Applications
13. Repeats for 3 more jobs
14. Goes to Analytics
15. Sees:
    - Project "ML Recommender" used 3 times
    - Missing skill "TensorFlow" in 80% of jobs
    - Match score distribution: 4 jobs 80%+, 10 jobs 60-80%
    - Recommendation: Learn TensorFlow, PyTorch
```

## Technical Implementation Details

### Job Search Pipeline

**4-Stage Process**:
```python
# Stage 1: Scraping (25% progress)
jobs = scraper_factory.scrape_all_sources(
    keywords="ML Engineer",
    location="Paris",
    sources=['welcome', 'adzuna'],
    max_results=50
)

# Stage 2: Filtering (50% progress)
filtered = filter_engine.filter_jobs(
    jobs=jobs,
    keywords="ML Engineer",
    location="Paris",
    job_types=['Full-time'],
    max_age_days=7
)

# Stage 3: RAG Ranking (75% progress)
ranked = rag_ranker.rank_jobs(
    user_id=user_id,
    jobs=filtered,
    top_n=20
)
# Calculates: semantic_similarity * 30 + skills_match * 30 + ...

# Stage 4: Project Selection (90% progress)
for job in ranked:
    job['selected_projects'] = project_selector.select_relevant_projects(
        user_id=user_id,
        job=job,
        max_projects=3
    )
    # Returns projects with relevance scores and matching technologies
```

### CV Generation

**Template vs LLM Mode**:
```python
# Template mode (always works, no API)
cv_result = cv_generator.generate_cv(
    user_id=user_id,
    job=job,
    cv_preferences={'cv_length': 1, 'include_projects': True},
    use_llm=False
)

# LLM mode (requires Groq API key)
cv_result = cv_generator.generate_cv(
    user_id=user_id,
    job=job,
    cv_preferences={'cv_length': 2, 'max_projects_per_cv': 3},
    use_llm=True
)
```

**Result Structure**:
```python
{
    'content': "# John Doe\n\n## Summary\n...",
    'metadata': {
        'generation_method': 'template',  # or 'groq_llm'
        'cv_length': 1,
        'projects_included': ['proj-id-1', 'proj-id-2'],
        'word_count': 415,
        'generated_at': '2024-01-15T10:30:00'
    }
}
```

## Analytics Calculations

### Skills Gap Analysis

```python
# Count required skills across all jobs
skill_counts = {}
for job in search_results:
    for skill in job['required_skills']:
        skill_counts[skill] = skill_counts.get(skill, 0) + 1

# Sort by frequency
top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:15]

# Compare with user skills
user_skills = set(profile['skills'])
missing_skills = [skill for skill, count in top_skills
                  if skill.lower() not in {s.lower() for s in user_skills}]

# Recommend top 5 missing skills
recommendations = missing_skills[:5]
```

### Project Performance

```python
# Count how many times each project was selected
project_usage = {}
for app in generated_cvs:
    for proj_id in app['cv']['metadata']['projects_included']:
        project_usage[proj_id] = project_usage.get(proj_id, 0) + 1

# Create bar chart
chart_data = pd.DataFrame({
    'Project': [p['title'] for p in projects],
    'Times Used': [project_usage.get(p['id'], 0) for p in projects]
})
st.bar_chart(chart_data.set_index('Project'))
```

## Performance Considerations

### Optimization Strategies

1. **Caching**: Search results stored in session state
2. **Lazy loading**: Only scrape when user submits search
3. **Batch operations**: Embed multiple jobs at once
4. **Progressive rendering**: Show results as they load
5. **Session persistence**: Filters and preferences remembered

### Resource Usage

- **Search**: ~10-30 seconds (depends on sources)
- **CV Generation**: ~2-5 seconds (template), ~5-10 seconds (LLM)
- **Analytics**: Instant (computed from session data)

## Troubleshooting

### Common Issues

**Search fails**:
```
Error: Connection timeout
Solution: Check internet connection, try fewer sources
```

**No results**:
```
0 jobs found after filtering
Solution: Broaden search criteria, increase max_age_days
```

**CV generation fails**:
```
Error: Profile not found
Solution: Create profile first on Profile page
```

**Analytics empty**:
```
No data to display
Solution: Run a job search and generate some CVs first
```

## API Keys Required

### Groq API (Optional - for LLM CV generation)

```bash
# In .env file
GROQ_API_KEY=gsk_your_api_key_here
```

Get free API key: https://console.groq.com

### Adzuna API (Optional - for job scraping)

```bash
# In .env file
ADZUNA_APP_ID=your_app_id
ADZUNA_APP_KEY=your_app_key
```

Get free API key: https://developer.adzuna.com

## Next Steps (Future Phases)

### Phase 9: Output & Export
- CSV export of applications
- Excel export with analytics
- PDF CV generation
- Bulk export functionality

### Phase 10: Testing
- Unit tests for all pages
- Integration tests for workflows
- Performance tests
- UI/UX testing

### Phase 11: CI/CD
- GitHub Actions workflows
- Automated testing
- Deployment pipelines

## Changelog

### Phase 8 Additions

**New Pages**:
- Job Search (complete implementation)
- Search Results (with filtering)
- Applications Tracking
- Analytics & Insights

**New Components**:
- `job_card.py`: Job display and interaction
- `filters.py`: Search and filter forms

**Enhanced**:
- Navigation with 7 pages total
- Session state management
- RAG integration throughout
- Real-time progress tracking
- Interactive charts and visualizations

## Support

For issues:
1. Check error details in expanders
2. Verify database and vector store are initialized
3. Check API keys in `.env` file
4. Review logs for detailed error messages
