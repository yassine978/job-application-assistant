# Testing Deployment Guide

This guide walks you through testing the Job Application Assistant deployment locally using Docker.

## Prerequisites

Before you start, ensure you have:
- Docker Desktop installed and running
- Git repository cloned locally
- API keys (Groq, Adzuna)
- At least 4GB of free RAM
- At least 5GB of free disk space

## Quick Start - Test the App in 5 Minutes

### Step 1: Start Docker Desktop

1. Open Docker Desktop application
2. Wait for Docker to fully start (whale icon should be stable)
3. Verify Docker is running:
   ```bash
   docker --version
   docker-compose --version
   ```

### Step 2: Set Up Environment Variables

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` file with your actual credentials:
   ```bash
   # Database Configuration (keep these as-is for local testing)
   DATABASE_URL=postgresql://postgres:postgres@postgres:5432/job_assistant
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   POSTGRES_DB=job_assistant

   # API Keys (REPLACE WITH YOUR ACTUAL KEYS)
   GROQ_API_KEY=your_actual_groq_api_key_here
   ADZUNA_APP_ID=your_actual_adzuna_app_id_here
   ADZUNA_API_KEY=your_actual_adzuna_api_key_here

   # Application Settings
   DEBUG=True
   ```

   **Important**: Replace the placeholder API keys with your real keys!

### Step 3: Start All Services

```bash
# Start PostgreSQL database and Streamlit app
docker-compose up -d

# This will:
# 1. Download PostgreSQL image (first time only)
# 2. Build your application image (takes 3-5 minutes first time)
# 3. Start both containers
# 4. Set up the database
```

### Step 4: Watch the Logs

```bash
# Watch all logs
docker-compose logs -f

# Or watch just the app logs
docker-compose logs -f app

# Press Ctrl+C to stop watching (containers keep running)
```

**What to look for**:
- `postgres_1  | ... database system is ready to accept connections` - Database is ready
- `app_1       | You can now view your Streamlit app in your browser` - App is ready
- `app_1       | Network URL: http://0.0.0.0:8501` - App is accessible

### Step 5: Access the Dashboard

1. Open your browser
2. Go to: **http://localhost:8501**
3. You should see the Job Application Assistant dashboard!

### Step 6: Test the Application

#### 6.1. Create a User Profile

1. Click on "Profile" in the sidebar
2. Fill in your information:
   - Full Name
   - Email
   - Phone
   - Skills (comma-separated)
   - Education
   - Work Experience
3. Click "Save Profile"

#### 6.2. Scrape Some Jobs

1. Click on "Jobs" in the sidebar
2. Click "Scrape New Jobs" button
3. Enter search criteria:
   - Keywords: `Python Developer`
   - Location: `Paris` or `Remote`
4. Click "Start Scraping"
5. Wait for jobs to appear (takes 30-60 seconds)

#### 6.3. Create a Project

1. Click on "Projects" in the sidebar
2. Click "Create New Project"
3. Enter project details:
   - Name: `Software Engineer Applications`
   - Description: `Applying for Python developer positions`
4. Click "Create Project"

#### 6.4. Generate a CV

1. Click on "Generate" in the sidebar
2. Select a job from the list
3. Select your profile
4. Select the project you created
5. Click "Generate CV"
6. Download the generated PDF

#### 6.5. View Analytics

1. Click on "Analytics" in the sidebar
2. View your application statistics
3. Check job distribution charts
4. Review timeline data

### Step 7: Stop the Services

```bash
# Stop all services (keeps data)
docker-compose down

# Or stop and remove all data (fresh start)
docker-compose down -v
```

## Detailed Testing Scenarios

### Scenario 1: Test Database Persistence

**Purpose**: Verify data persists between container restarts

1. Start services: `docker-compose up -d`
2. Create a user profile
3. Stop services: `docker-compose down`
4. Start services again: `docker-compose up -d`
5. Check if your profile still exists
6. ✅ **Expected**: Profile should be there

### Scenario 2: Test Job Scraping

**Purpose**: Verify scrapers work correctly

1. Go to Jobs page
2. Click "Scrape New Jobs"
3. Use these test parameters:
   - Keywords: `Python`
   - Location: `Paris`
4. Wait for results
5. ✅ **Expected**: At least 5-10 jobs should appear

**Troubleshooting**:
- If no jobs appear, check Adzuna API keys in `.env`
- Check logs: `docker-compose logs app`
- Verify API quota isn't exceeded

### Scenario 3: Test AI Generation

**Purpose**: Verify Groq API integration works

1. Create a profile if you haven't
2. Scrape at least one job
3. Go to Generate page
4. Select job, profile, and project
5. Click "Generate CV"
6. ✅ **Expected**: CV should generate within 10-15 seconds

**Troubleshooting**:
- If generation fails, check Groq API key in `.env`
- Check logs: `docker-compose logs app | grep -i error`
- Verify Groq API quota isn't exceeded

### Scenario 4: Test Vector Search

**Purpose**: Verify ChromaDB integration

1. Scrape at least 20 jobs
2. Go to Jobs page
3. Use the search box
4. Search for: `machine learning`
5. ✅ **Expected**: Results should be semantically relevant

### Scenario 5: Test Export Functionality

**Purpose**: Verify document generation

1. Generate a CV
2. Click "Export All Documents"
3. Check the generated files
4. ✅ **Expected**: Should download ZIP with PDF/DOCX files

### Scenario 6: Test Multi-User Support

**Purpose**: Verify multiple profiles work

1. Create Profile 1: "John Doe"
2. Create Profile 2: "Jane Smith"
3. Generate CV for same job with both profiles
4. ✅ **Expected**: Different CVs with different information

## Advanced Testing

### Test with Docker Only (No Compose)

```bash
# 1. Start PostgreSQL manually
docker run -d \
  --name test-postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=job_assistant \
  -p 5432:5432 \
  postgres:14-alpine

# 2. Build the app image
docker build -t job-app:test -f docker/Dockerfile .

# 3. Run the app
docker run -d \
  --name test-app \
  -p 8501:8501 \
  -e DATABASE_URL=postgresql://postgres:postgres@host.docker.internal:5432/job_assistant \
  -e GROQ_API_KEY=your_key \
  -e ADZUNA_APP_ID=your_id \
  -e ADZUNA_API_KEY=your_key \
  job-app:test

# 4. Access at http://localhost:8501

# 5. Cleanup
docker stop test-app test-postgres
docker rm test-app test-postgres
```

### Test Scraper Separately

```bash
# Run just the scraper
docker-compose --profile scraper up scraper

# Check scraper logs
docker-compose logs scraper
```

### Test Health Check

```bash
# Check if app is healthy
curl http://localhost:8501/_stcore/health

# Expected response: OK (HTTP 200)
```

## Monitoring and Debugging

### View Container Status

```bash
# List running containers
docker-compose ps

# Expected output:
# NAME                STATUS              PORTS
# job-app-postgres    Up (healthy)        0.0.0.0:5432->5432/tcp
# job-app-streamlit   Up                  0.0.0.0:8501->8501/tcp
```

### View Logs

```bash
# All logs
docker-compose logs

# Last 100 lines of app logs
docker-compose logs --tail=100 app

# Follow logs in real-time
docker-compose logs -f app

# Logs with timestamps
docker-compose logs -f -t app
```

### Access Container Shell

```bash
# Open shell in app container
docker-compose exec app /bin/bash

# Inside container, you can:
# - Check files: ls -la
# - Test Python: python --version
# - Run commands: python -c "from database.db_manager import db_manager; print(db_manager)"
# - Exit: exit
```

### Check Database

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U postgres -d job_assistant

# Inside psql, you can:
# - List tables: \dt
# - Describe table: \d users
# - Query data: SELECT * FROM users;
# - Exit: \q
```

### Monitor Resource Usage

```bash
# Check CPU, memory, network usage
docker stats

# Expected usage:
# - postgres: ~50-100 MB RAM
# - app: ~500-800 MB RAM
```

## Common Issues and Solutions

### Issue 1: Port 8501 Already in Use

**Symptom**: Error binding to port 8501

**Solution**:
```bash
# Option 1: Find and kill process using port 8501
# Windows:
netstat -ano | findstr :8501
taskkill /PID <process_id> /F

# macOS/Linux:
lsof -ti:8501 | xargs kill -9

# Option 2: Change port in docker-compose.yml
# Edit ports section: "8502:8501"
# Then access at http://localhost:8502
```

### Issue 2: Database Connection Failed

**Symptom**: App logs show "could not connect to database"

**Solution**:
```bash
# 1. Check if postgres is healthy
docker-compose ps

# 2. If not healthy, check postgres logs
docker-compose logs postgres

# 3. Restart just the database
docker-compose restart postgres

# 4. Wait for health check to pass
docker-compose ps
```

### Issue 3: Out of Memory

**Symptom**: Container crashes or Docker becomes unresponsive

**Solution**:
1. Open Docker Desktop
2. Go to Settings → Resources
3. Increase Memory limit to at least 4GB
4. Click "Apply & Restart"

### Issue 4: Slow Build Times

**Symptom**: Docker build takes 10+ minutes

**Solution**:
```bash
# Use BuildKit for faster builds
export DOCKER_BUILDKIT=1
docker-compose build

# Or clear build cache and rebuild
docker builder prune
docker-compose build --no-cache
```

### Issue 5: Playwright Browser Not Found

**Symptom**: Scraping fails with "Browser executable not found"

**Solution**:
```bash
# Rebuild image to reinstall browsers
docker-compose build --no-cache app
docker-compose up -d
```

### Issue 6: API Keys Not Working

**Symptom**: "Invalid API key" errors in logs

**Solution**:
1. Verify `.env` file exists and has correct keys
2. Ensure no extra spaces around `=` sign
3. Restart containers to reload environment:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

### Issue 7: ChromaDB Errors

**Symptom**: Vector search fails or embeddings error

**Solution**:
```bash
# Delete ChromaDB data and restart
docker-compose down
rm -rf chroma_db/
docker-compose up -d
```

## Performance Benchmarks

Expected performance on typical hardware (i5/Ryzen 5, 8GB RAM):

- **Container startup**: 10-30 seconds
- **App ready**: 30-60 seconds after startup
- **Job scraping (10 jobs)**: 20-40 seconds
- **CV generation**: 5-15 seconds
- **Vector search**: < 1 second
- **Page load**: < 2 seconds

## Testing Checklist

Use this checklist to verify full functionality:

- [ ] Docker Desktop is running
- [ ] `.env` file created with real API keys
- [ ] `docker-compose up -d` runs successfully
- [ ] Can access http://localhost:8501
- [ ] Dashboard loads without errors
- [ ] Can create user profile
- [ ] Profile saves successfully
- [ ] Can scrape jobs (at least 5 appear)
- [ ] Jobs display in Jobs page
- [ ] Can create project
- [ ] Can generate CV for a job
- [ ] CV downloads as PDF
- [ ] Can generate cover letter
- [ ] Can view analytics
- [ ] Search works on Jobs page
- [ ] Filter works on Jobs page
- [ ] Can export documents
- [ ] Logs show no errors
- [ ] Database persists after restart
- [ ] Health check passes

## Success Criteria

Your deployment is successful if:

✅ All containers start without errors
✅ Dashboard is accessible at http://localhost:8501
✅ You can create a profile and it persists
✅ Job scraping returns at least 5 jobs
✅ CV generation works and produces a PDF
✅ No errors in logs (some warnings are OK)
✅ Data persists after `docker-compose down` and `up`

## Next Steps After Testing

Once you've verified everything works locally:

1. **Push to GitHub** (you've done this! ✅)
2. **Deploy to Streamlit Cloud**:
   - Go to https://share.streamlit.io
   - Connect your GitHub repository
   - Set main file: `dashboard/app.py`
   - Add secrets from your `.env` file
   - Click "Deploy"

3. **Monitor CI/CD**:
   - Go to your GitHub repo
   - Click "Actions" tab
   - Watch CI pipeline run
   - Verify all tests pass

4. **Create a Release**:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
   - GitHub Actions will automatically build and publish Docker image

## Getting Help

If you encounter issues:

1. Check logs: `docker-compose logs -f app`
2. Check this guide's troubleshooting section
3. Review [DEPLOYMENT.md](DEPLOYMENT.md)
4. Check container status: `docker-compose ps`
5. Verify environment variables: `docker-compose config`

## Clean Up After Testing

```bash
# Stop and remove containers, but keep data
docker-compose down

# Stop and remove everything including data
docker-compose down -v

# Remove Docker images to free space
docker rmi job-application-assistant-app
docker rmi postgres:14-alpine

# Remove all unused Docker resources
docker system prune -a
```

---

**Ready to test?** Start with the Quick Start section above!
