# Deployment Guide

This guide covers deploying the Job Application Assistant to various environments.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Variables](#environment-variables)
3. [Local Development with Docker](#local-development-with-docker)
4. [Streamlit Cloud Deployment](#streamlit-cloud-deployment)
5. [Docker Hub Deployment](#docker-hub-deployment)
6. [Production Deployment](#production-deployment)
7. [CI/CD Pipeline](#cicd-pipeline)
8. [Monitoring and Maintenance](#monitoring-and-maintenance)

## Prerequisites

- Docker and Docker Compose (for containerized deployment)
- Python 3.9+ (for local development)
- PostgreSQL 14+ (for production database)
- GitHub account (for CI/CD)
- API Keys:
  - Groq API key (for AI generation)
  - Adzuna API credentials (for job scraping)

## Environment Variables

Create a `.env` file in the project root:

```bash
# Database
DATABASE_URL=postgresql://user:password@host:5432/dbname
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=job_assistant

# API Keys
GROQ_API_KEY=your_groq_api_key
ADZUNA_APP_ID=your_adzuna_app_id
ADZUNA_API_KEY=your_adzuna_api_key

# Application
DEBUG=False
```

## Local Development with Docker

### Quick Start

```bash
# 1. Clone the repository
git clone <repository-url>
cd job-application-assistant

# 2. Create .env file with your credentials
cp .env.example .env
# Edit .env with your API keys

# 3. Start all services
docker-compose up -d

# 4. Access the dashboard
open http://localhost:8501
```

### Running Individual Services

```bash
# Start only the database
docker-compose up -d postgres

# Start the main application
docker-compose up -d app

# Run the scraper manually
docker-compose run --rm scraper
```

### Viewing Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f app
docker-compose logs -f postgres
```

### Stopping Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes data)
docker-compose down -v
```

## Streamlit Cloud Deployment

### Prerequisites

1. GitHub repository with the code
2. Streamlit Cloud account (free tier available)

### Steps

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Prepare for Streamlit deployment"
   git push origin main
   ```

2. **Configure Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io/)
   - Click "New app"
   - Select your repository
   - Set main file path: `dashboard/app.py`
   - Click "Advanced settings"

3. **Add Secrets**
   Create a `secrets.toml` file in Streamlit Cloud settings:
   ```toml
   DATABASE_URL = "your_database_url"
   GROQ_API_KEY = "your_groq_api_key"
   ADZUNA_APP_ID = "your_adzuna_app_id"
   ADZUNA_API_KEY = "your_adzuna_api_key"
   ```

4. **Deploy**
   - Click "Deploy"
   - Wait for deployment to complete
   - Your app will be available at `https://your-app-name.streamlit.app`

### Auto-Deployment

Streamlit Cloud automatically redeploys when you push to the main branch.

## Docker Hub Deployment

### Building and Pushing Images

```bash
# 1. Build the image
docker build -t your-username/job-application-assistant:latest -f docker/Dockerfile .

# 2. Tag with version
docker tag your-username/job-application-assistant:latest \
  your-username/job-application-assistant:v1.0.0

# 3. Login to Docker Hub
docker login

# 4. Push images
docker push your-username/job-application-assistant:latest
docker push your-username/job-application-assistant:v1.0.0
```

### Pulling and Running

```bash
# Pull the image
docker pull your-username/job-application-assistant:latest

# Run the container
docker run -d \
  -p 8501:8501 \
  -e DATABASE_URL="your_database_url" \
  -e GROQ_API_KEY="your_key" \
  -e ADZUNA_APP_ID="your_id" \
  -e ADZUNA_API_KEY="your_key" \
  --name job-app \
  your-username/job-application-assistant:latest
```

## Production Deployment

### Database Setup

1. **Create PostgreSQL Database**
   ```bash
   # Using managed service (recommended):
   # - Neon.tech (free tier available)
   # - Railway.app
   # - Supabase
   # - AWS RDS
   # - DigitalOcean Managed Databases

   # Or self-hosted:
   createdb job_assistant
   ```

2. **Initialize Database**
   ```bash
   docker-compose run --rm app python -c "
   from database.db_manager import db_manager
   db_manager.initialize()
   print('Database initialized successfully')
   "
   ```

### Production Docker Compose

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  app:
    image: your-username/job-application-assistant:latest
    container_name: job-app-prod
    environment:
      DATABASE_URL: ${DATABASE_URL}
      GROQ_API_KEY: ${GROQ_API_KEY}
      ADZUNA_APP_ID: ${ADZUNA_APP_ID}
      ADZUNA_API_KEY: ${ADZUNA_API_KEY}
      DEBUG: "False"
    ports:
      - "8501:8501"
    volumes:
      - chroma_data:/app/chroma_db
      - generated_docs:/app/generated_documents
      - app_logs:/app/logs
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  chroma_data:
  generated_docs:
  app_logs:
```

Run with:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Scheduled Job Scraping

**Option 1: GitHub Actions (Recommended)**
- Automatically runs daily at 9 AM UTC
- Configured in `.github/workflows/scheduled_scrape.yml`
- No additional setup needed

**Option 2: Cron Job**
```bash
# Add to crontab
0 9 * * * docker-compose run --rm scraper python -m scrapers.scraper_factory
```

**Option 3: Manual Run**
```bash
docker-compose run --rm scraper
```

## CI/CD Pipeline

### GitHub Actions Workflows

The project includes three automated workflows:

1. **CI Pipeline** (`.github/workflows/ci.yml`)
   - Triggers: Push to main/develop, PRs to main
   - Steps: Lint, test, integration tests
   - Runs on every commit

2. **CD Pipeline** (`.github/workflows/cd.yml`)
   - Triggers: Push to main, version tags
   - Steps: Deploy to Streamlit, build Docker, create releases

3. **Scheduled Scraping** (`.github/workflows/scheduled_scrape.yml`)
   - Triggers: Daily at 9 AM UTC, manual trigger
   - Steps: Scrape jobs, cleanup old jobs

### Setting Up GitHub Secrets

Go to repository Settings > Secrets and variables > Actions:

```
Required Secrets:
- DATABASE_URL: PostgreSQL connection string
- GROQ_API_KEY: Groq API key
- ADZUNA_APP_ID: Adzuna application ID
- ADZUNA_API_KEY: Adzuna API key

Optional (for Docker Hub):
- DOCKER_USERNAME: Docker Hub username
- DOCKER_PASSWORD: Docker Hub password or access token
```

### Creating a Release

```bash
# 1. Update version and commit changes
git add .
git commit -m "Prepare v1.0.0 release"

# 2. Create and push tag
git tag v1.0.0
git push origin v1.0.0

# 3. GitHub Actions automatically:
#    - Builds Docker image
#    - Pushes to Docker Hub
#    - Creates GitHub release with changelog
```

### Manual Workflow Triggers

```bash
# Trigger CI manually
gh workflow run ci.yml

# Trigger scraper manually
gh workflow run scheduled_scrape.yml
```

## Monitoring and Maintenance

### Health Checks

```bash
# Check application health
curl http://localhost:8501/_stcore/health

# Check Docker containers
docker-compose ps

# View resource usage
docker stats
```

### Logs

```bash
# Application logs
docker-compose logs -f app

# Database logs
docker-compose logs -f postgres

# Follow specific service logs
docker-compose logs -f --tail=100 app
```

### Database Backup

```bash
# Backup database
docker-compose exec postgres pg_dump -U postgres job_assistant > backup.sql

# Restore database
docker-compose exec -T postgres psql -U postgres job_assistant < backup.sql
```

### Cleanup Old Data

```bash
# Manual cleanup (removes jobs older than 30 days)
docker-compose run --rm app python -c "
from database.db_manager import db_manager
from database.models import Job
from datetime import datetime, timedelta

db_manager.initialize()
with db_manager.db as session:
    cutoff = datetime.now() - timedelta(days=30)
    deleted = session.query(Job).filter(Job.posting_date < cutoff).delete()
    session.commit()
    print(f'Deleted {deleted} old jobs')
"
```

### Updating the Application

```bash
# 1. Pull latest changes
git pull origin main

# 2. Rebuild and restart
docker-compose down
docker-compose up -d --build

# 3. Check logs
docker-compose logs -f app
```

## Troubleshooting

### Common Issues

**Issue: Database connection failed**
```bash
# Check if database is running
docker-compose ps postgres

# Check database logs
docker-compose logs postgres

# Verify DATABASE_URL format
echo $DATABASE_URL
# Should be: postgresql://user:password@host:5432/dbname
```

**Issue: Playwright browser not found**
```bash
# Reinstall Playwright browsers
docker-compose run --rm app playwright install chromium
```

**Issue: Port 8501 already in use**
```bash
# Find process using port
lsof -i :8501  # macOS/Linux
netstat -ano | findstr :8501  # Windows

# Kill process or change port in docker-compose.yml
ports:
  - "8502:8501"  # Use different external port
```

**Issue: Out of memory**
```bash
# Increase Docker memory limit (Docker Desktop)
# Settings > Resources > Memory > Increase limit

# Or use memory limits in docker-compose.yml
services:
  app:
    mem_limit: 2g
```

### Getting Help

- Check logs: `docker-compose logs -f`
- Run tests: `docker-compose run --rm app pytest tests/`
- Open an issue on GitHub
- Check the [README.md](README.md) for additional information

## Security Best Practices

1. **Never commit secrets** - Use `.env` files and GitHub Secrets
2. **Use strong passwords** - Especially for production databases
3. **Keep dependencies updated** - Regularly update `requirements.txt`
4. **Enable HTTPS** - Use reverse proxy (nginx) in production
5. **Limit database access** - Use firewall rules and VPC
6. **Regular backups** - Automate database backups
7. **Monitor logs** - Set up log aggregation and alerts
8. **Update Docker images** - Keep base images updated

## Performance Optimization

1. **Database indexing** - Already configured in models
2. **Caching** - ChromaDB provides vector caching
3. **Connection pooling** - SQLAlchemy handles this
4. **Resource limits** - Set in docker-compose.yml
5. **CDN** - Use for static assets in production

## Cost Optimization

1. **Free tier services**:
   - Streamlit Cloud (free for public repos)
   - Neon.tech (free PostgreSQL database)
   - GitHub Actions (free for public repos)

2. **Scheduled scraping**:
   - Runs once daily to minimize API usage
   - Auto-cleanup to keep database small

3. **Docker optimization**:
   - Multi-stage builds reduce image size
   - Layer caching speeds up builds
