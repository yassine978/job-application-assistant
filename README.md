# Job Application Assistant

AI-powered job application assistant with RAG (Retrieval-Augmented Generation) for automated job search, CV generation, and cover letter creation.

## Overview

This application helps job seekers streamline their application process by:
- Automatically scraping job listings from multiple sources
- Storing jobs in a searchable database with vector embeddings
- Generating tailored CVs and cover letters using AI
- Tracking application status and deadlines
- Providing analytics and insights via an interactive dashboard

## Features

- **Multi-Source Job Scraping**: Adzuna API, LinkedIn, Indeed, and custom sources
- **RAG-Powered AI Generation**: Context-aware CV and cover letter creation using Groq LLMs
- **Vector Search**: ChromaDB for semantic job search and matching
- **User Authentication**: Secure login and profile management
- **Project Management**: Organize applications by projects/campaigns
- **Interactive Dashboard**: Streamlit-based UI with analytics and visualizations
- **Automated Workflows**: Scheduled job scraping and cleanup via GitHub Actions
- **Export Capabilities**: Generate PDFs, Word documents, and Excel reports

## Tech Stack

- **Backend**: Python 3.9+
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Vector Store**: ChromaDB for embeddings
- **AI/LLM**: Groq API (Llama models)
- **Web Scraping**: Playwright, BeautifulSoup, Adzuna API
- **Frontend**: Streamlit
- **DevOps**: Docker, Docker Compose, GitHub Actions
- **Testing**: pytest with 95%+ coverage

## Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd job-application-assistant

# Create environment file
cp .env.example .env
# Edit .env with your API keys

# Start all services
docker-compose up -d

# Access the dashboard
open http://localhost:8501
```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Set up database
python -c "from database.db_manager import db_manager; db_manager.initialize()"

# Run the dashboard
streamlit run dashboard/app.py

# Or run tests
python run_tests.py
```

## Environment Variables

Create a `.env` file with the following variables:

```bash
# Database
DATABASE_URL=postgresql://user:password@host:5432/dbname

# API Keys
GROQ_API_KEY=your_groq_api_key
ADZUNA_APP_ID=your_adzuna_app_id
ADZUNA_API_KEY=your_adzuna_api_key

# Optional: Monitoring
SENTRY_DSN=your_sentry_dsn
ENVIRONMENT=production

# Debug mode
DEBUG=False
```

## Project Structure

```
job-application-assistant/
├── ai/                         # AI generation modules
│   ├── cv_generator.py         # CV generation
│   ├── cover_letter_generator.py  # Cover letter generation
│   └── groq_client.py          # Groq API client
├── database/                   # Database layer
│   ├── models.py               # SQLAlchemy models
│   ├── db_manager.py           # Database operations
│   └── connection.py           # Database connection
├── scrapers/                   # Job scraping modules
│   ├── adzuna_scraper.py       # Adzuna API scraper
│   ├── linkedin_scraper.py     # LinkedIn scraper
│   └── scraper_factory.py     # Scraper orchestration
├── vector_store/               # Vector database
│   ├── chroma_manager.py       # ChromaDB operations
│   └── embeddings.py           # Embedding generation
├── dashboard/                  # Streamlit UI
│   ├── app.py                  # Main dashboard
│   └── pages/                  # Dashboard pages
├── monitoring/                 # Error tracking
│   └── sentry_config.py        # Sentry configuration
├── tests/                      # Test suite
├── .github/workflows/          # CI/CD pipelines
├── docker/                     # Docker configuration
├── generated_documents/        # Output files
├── requirements.txt            # Python dependencies
├── docker-compose.yml          # Docker services
└── DEPLOYMENT.md              # Deployment guide
```

## Usage

### 1. Scrape Jobs

```python
from scrapers.scraper_factory import scraper_factory

jobs = scraper_factory.scrape_all_sources(
    keywords=['Python', 'Developer'],
    locations=['Paris', 'Remote'],
    max_age_days=7,
    auto_save_db=True
)
```

### 2. Generate CV

```python
from ai.cv_generator import cv_generator
from database.db_manager import db_manager

with db_manager.db as session:
    job = session.query(Job).first()
    user = session.query(User).first()

    cv_path = cv_generator.generate_cv(
        job=job,
        user=user,
        project_name="Software Engineer Applications"
    )
```

### 3. Use Dashboard

```bash
streamlit run dashboard/app.py
```

Navigate through:
- **Jobs**: Browse and filter job listings
- **Projects**: Organize applications by project
- **Generate**: Create CVs and cover letters
- **Analytics**: View application statistics
- **Profile**: Manage user information

## Testing

```bash
# Run all tests
python run_tests.py

# Run specific test suite
pytest tests/test_scrapers.py -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

**Test Coverage**: 95%+
- Unit tests for all core modules
- Integration tests for database and vector store
- End-to-end workflow tests

## CI/CD Pipeline

### GitHub Actions Workflows

1. **CI Pipeline** (`.github/workflows/ci.yml`)
   - Runs on: Push to main/develop, PRs
   - Steps: Lint, format check, type check, security scan, tests

2. **CD Pipeline** (`.github/workflows/cd.yml`)
   - Runs on: Push to main, version tags
   - Steps: Deploy to Streamlit Cloud, build Docker images, create releases

3. **Scheduled Scraping** (`.github/workflows/scheduled_scrape.yml`)
   - Runs: Daily at 9 AM UTC
   - Steps: Scrape new jobs, cleanup old jobs

### Creating a Release

```bash
git tag v1.0.0
git push origin v1.0.0
# Automatically builds Docker image and creates GitHub release
```

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions covering:
- Local development with Docker
- Streamlit Cloud deployment
- Docker Hub deployment
- Production deployment
- Monitoring and maintenance

## Monitoring

The application includes Sentry integration for error tracking and performance monitoring:

```python
from monitoring import initialize_sentry, capture_exception

initialize_sentry()

try:
    risky_operation()
except Exception as e:
    capture_exception(e, level="error")
```

## Development Phases

This project was developed in 11 phases:

1. **Phase 1**: Project setup and database schema
2. **Phase 2**: Basic job scraping (Adzuna API)
3. **Phase 3**: Advanced scrapers (LinkedIn, Indeed)
4. **Phase 4**: Vector database integration (ChromaDB)
5. **Phase 5**: RAG-powered AI generation
6. **Phase 6**: Enhanced AI with context
7. **Phase 7**: User authentication and profiles
8. **Phase 8**: Streamlit dashboard
9. **Phase 9**: Output and export functionality
10. **Phase 10**: Comprehensive testing
11. **Phase 11**: CI/CD and DevOps (current)

## API Documentation

### Scrapers

```python
# Adzuna API
from scrapers.adzuna_scraper import adzuna_scraper
jobs = adzuna_scraper.search_jobs(keywords='Python', location='Paris')

# LinkedIn
from scrapers.linkedin_scraper import linkedin_scraper
jobs = linkedin_scraper.scrape_jobs(keywords='Developer', location='Remote')
```

### AI Generation

```python
# CV Generator
from ai.cv_generator import cv_generator
cv_path = cv_generator.generate_cv(job, user, project_name)

# Cover Letter Generator
from ai.cover_letter_generator import cover_letter_generator
cl_path = cover_letter_generator.generate_cover_letter(job, user, project_name)
```

### Vector Search

```python
from vector_store.chroma_manager import chroma_manager

# Search similar jobs
similar_jobs = chroma_manager.search_similar_jobs(
    query="Python machine learning position",
    n_results=10
)
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check [DEPLOYMENT.md](DEPLOYMENT.md) for troubleshooting
- Review the test suite for usage examples

## Acknowledgments

- Groq for fast LLM inference
- Adzuna for job listing API
- ChromaDB for vector storage
- Streamlit for rapid UI development
