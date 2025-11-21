# Quick Start - See Your App Running in 5 Minutes

## Option 1: Automated Start (Easiest)

### Windows:
1. Double-click `start.bat`
2. Wait for services to start
3. Browser will open automatically to http://localhost:8501

### Mac/Linux:
```bash
./start.sh
```

## Option 2: Manual Start

### Step 1: Setup Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API keys
# IMPORTANT: Replace the placeholders with real keys!
```

### Step 2: Start Services
```bash
# Start Docker Desktop first, then:
docker-compose up -d
```

### Step 3: Access Dashboard
Open browser: **http://localhost:8501**

## What You'll See

1. **Welcome Page**: Job Application Assistant dashboard
2. **Sidebar**: Navigation menu with:
   - 🏠 Home
   - 👤 Profile
   - 💼 Jobs
   - 📁 Projects
   - ✨ Generate
   - 📊 Analytics

## First-Time Setup Flow

### 1. Create Your Profile (2 minutes)
- Click "Profile" in sidebar
- Fill in: Name, Email, Phone, Skills, Education, Experience
- Click "Save Profile"

### 2. Scrape Some Jobs (1 minute)
- Click "Jobs" in sidebar
- Click "Scrape New Jobs"
- Enter: Keywords: `Python`, Location: `Paris`
- Click "Start Scraping"
- Wait 30 seconds

### 3. Create a Project (30 seconds)
- Click "Projects" in sidebar
- Click "Create New Project"
- Name: `My Applications`
- Click "Create"

### 4. Generate Your First CV (1 minute)
- Click "Generate" in sidebar
- Select a job
- Select your profile
- Select your project
- Click "Generate CV"
- Download the PDF!

## Troubleshooting

**Port 8501 already in use?**
```bash
# Windows
netstat -ano | findstr :8501
taskkill /PID <process_id> /F

# Mac/Linux
lsof -ti:8501 | xargs kill -9
```

**Docker not running?**
- Open Docker Desktop
- Wait for it to fully start (whale icon stable)

**No jobs appearing?**
- Check your Adzuna API keys in `.env`
- Verify you have API quota remaining

**CV generation fails?**
- Check your Groq API key in `.env`
- Verify you have API quota remaining

## Useful Commands

```bash
# View logs
docker-compose logs -f app

# Stop services (keeps data)
docker-compose down

# Stop and remove all data
docker-compose down -v

# Restart services
docker-compose restart

# Check service status
docker-compose ps

# Open app container shell
docker-compose exec app /bin/bash
```

## What's Running?

- **PostgreSQL** (port 5432): Your database
- **Streamlit App** (port 8501): Your web interface
- **ChromaDB**: Vector database (embedded in app)

## Expected Resource Usage

- RAM: ~600-800 MB
- Disk: ~2-3 GB
- CPU: Minimal when idle

## Need More Help?

- Full guide: [TESTING_DEPLOYMENT.md](TESTING_DEPLOYMENT.md)
- Deployment guide: [DEPLOYMENT.md](DEPLOYMENT.md)
- README: [README.md](README.md)

---

**Ready? Let's go!** 🚀

Run `start.bat` (Windows) or `./start.sh` (Mac/Linux)
