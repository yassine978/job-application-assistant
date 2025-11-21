# GitHub Actions Errors - Fix Guide

## Why the Workflows Are Failing

The GitHub Actions workflows need **secrets** (API keys, database URL) to run, but they're not configured in your repository yet. This is expected and easy to fix!

## Current Status

✅ **Workflows are correctly configured** - The YAML files are perfect
❌ **Secrets are missing** - Need to add them to GitHub

## Which Workflows Are Failing

### 1. **Scheduled Job Scraping** ❌
- **Why**: Needs `DATABASE_URL`, `ADZUNA_APP_ID`, `ADZUNA_API_KEY`
- **Impact**: Can't scrape jobs automatically
- **Priority**: Low (you can scrape manually from dashboard)

### 2. **Final Tests and Deployment (CD Pipeline)** ❌
- **Why**: Tests might need secrets, Docker build might fail
- **Impact**: CI/CD pipeline incomplete
- **Priority**: Medium (for production deployment)

## Quick Fix: Disable Workflows (Temporary)

If you want to stop the errors immediately without setting up secrets:

### Option 1: Disable Scheduled Scraping

Edit [.github/workflows/scheduled_scrape.yml](.github/workflows/scheduled_scrape.yml):

```yaml
name: Scheduled Job Scraping

on:
  # schedule:  # COMMENTED OUT - disabled
  #   - cron: '0 9 * * *'
  workflow_dispatch:  # Keep manual trigger
```

This keeps the workflow but only runs when you manually trigger it.

### Option 2: Skip Workflows on Failure

Add `continue-on-error: true` to jobs that can fail:

```yaml
jobs:
  scrape-jobs:
    name: Scrape Job Listings
    runs-on: ubuntu-latest
    continue-on-error: true  # ADD THIS LINE
```

## Permanent Fix: Add GitHub Secrets

This is the proper solution for production.

### Step 1: Get Your Secrets Ready

You need these values from your `.env` file:
- `DATABASE_URL` - Your PostgreSQL connection string
- `GROQ_API_KEY` - Your Groq API key
- `ADZUNA_APP_ID` - Your Adzuna application ID
- `ADZUNA_API_KEY` - Your Adzuna API key

### Step 2: Add Secrets to GitHub

1. **Go to your GitHub repository**:
   ```
   https://github.com/yassine978/job-application-assistant
   ```

2. **Navigate to Settings**:
   - Click **Settings** tab (top right)
   - Click **Secrets and variables** (left sidebar)
   - Click **Actions**

3. **Add each secret**:
   - Click **New repository secret**
   - Name: `DATABASE_URL`
   - Value: Your actual database URL (from `.env`)
   - Click **Add secret**

   Repeat for:
   - `GROQ_API_KEY`
   - `ADZUNA_APP_ID`
   - `ADZUNA_API_KEY`

### Step 3: Optional Docker Hub Secrets

For Docker image publishing (only needed if you want to push to Docker Hub):

Add these secrets:
- `DOCKER_USERNAME` - Your Docker Hub username
- `DOCKER_PASSWORD` - Your Docker Hub password or access token

## Database URL for GitHub Actions

⚠️ **Important**: For GitHub Actions, you need a **publicly accessible database**.

Your local database (`localhost:5432`) won't work in GitHub Actions.

### Options:

#### Option 1: Free Database (Recommended)

Use a free hosted PostgreSQL database:

**Neon.tech (Free tier)**:
1. Go to https://neon.tech
2. Sign up (free)
3. Create new project
4. Copy connection string
5. Add as `DATABASE_URL` secret

**Supabase (Free tier)**:
1. Go to https://supabase.com
2. Sign up (free)
3. Create new project
4. Get connection string from Project Settings → Database
5. Add as `DATABASE_URL` secret

**Railway (Free tier)**:
1. Go to https://railway.app
2. Sign up (free)
3. Add PostgreSQL database
4. Copy connection string
5. Add as `DATABASE_URL` secret

#### Option 2: Skip Database Tests

If you don't want to set up a hosted database, modify the workflows to skip database-dependent jobs:

```yaml
- name: Run job scraper
  if: env.DATABASE_URL != ''  # Only run if DATABASE_URL exists
  env:
    DATABASE_URL: ${{ secrets.DATABASE_URL }}
    # ...
```

## Verify Secrets Are Working

After adding secrets:

### Test 1: Manual Workflow Trigger

1. Go to **Actions** tab in GitHub
2. Click **Scheduled Job Scraping**
3. Click **Run workflow** (right side)
4. Click **Run workflow** button
5. Wait for it to run
6. ✅ Should succeed if secrets are correct

### Test 2: Push a Commit

```bash
git add .
git commit -m "Test GitHub Actions with secrets"
git push origin main
```

Watch the **Actions** tab to see if workflows pass.

## What Each Workflow Does

### 1. CI Pipeline (`.github/workflows/ci.yml`)
**Triggers**: Every push, every PR
**Needs**:
- ✅ No secrets required for linting/testing
- ⚠️ Some integration tests might need `DATABASE_URL`

**Action**: Should work without secrets for basic checks

### 2. CD Pipeline (`.github/workflows/cd.yml`)
**Triggers**: Push to main, version tags
**Needs**:
- ⚠️ `DOCKER_USERNAME`, `DOCKER_PASSWORD` (optional)

**Action**: Works partially without secrets (deployment prep)

### 3. Scheduled Scraping (`.github/workflows/scheduled_scrape.yml`)
**Triggers**: Daily at 9 AM UTC, manual
**Needs**:
- ❌ `DATABASE_URL` (required)
- ❌ `ADZUNA_APP_ID` (required)
- ❌ `ADZUNA_API_KEY` (required)

**Action**: Will fail without secrets

## Recommended Approach for Now

Since your dashboard is working locally, here's what I recommend:

### Short Term (Today):
1. ✅ **Keep using local deployment** - It works!
2. ✅ **Ignore GitHub Actions errors** - They're expected
3. ✅ **Test dashboard locally** - Verify all features work

### Medium Term (This Week):
1. **Set up free hosted database** (Neon.tech - 5 minutes)
2. **Add GitHub Secrets** (5 minutes)
3. **Re-run failed workflows** - Should pass

### Long Term (Production):
1. **Deploy to Streamlit Cloud** (free, no secrets needed locally)
2. **Set up full CI/CD** (with all secrets)
3. **Enable scheduled scraping** (automated job updates)

## Quick Command to Disable Scheduled Workflow

If you want to stop the scheduled workflow from running:

```bash
# Rename the file to disable it
mv .github/workflows/scheduled_scrape.yml .github/workflows/scheduled_scrape.yml.disabled

# Commit and push
git add .
git commit -m "Temporarily disable scheduled scraping"
git push origin main
```

To re-enable later:
```bash
mv .github/workflows/scheduled_scrape.yml.disabled .github/workflows/scheduled_scrape.yml
git add .
git commit -m "Re-enable scheduled scraping"
git push origin main
```

## Summary

| Workflow | Status | Needs Secrets? | Action Needed |
|----------|--------|----------------|---------------|
| CI Pipeline | ⚠️ Partial | Some tests only | Optional: Add DATABASE_URL |
| CD Pipeline | ⚠️ Partial | Optional Docker | Optional: Add DOCKER_* |
| Scheduled Scraping | ❌ Failing | Yes, required | Add all API secrets OR disable |

**Bottom Line**: Your app works locally! The GitHub errors are just CI/CD automation issues. You can safely ignore them for now and set up secrets later when you're ready for production deployment.

---

## Want to Fix It Now?

If you want to fix the errors right now, do this:

1. **Sign up for Neon.tech** (2 minutes):
   - Go to https://neon.tech
   - Create free account
   - Create project
   - Copy connection string

2. **Add to GitHub Secrets** (3 minutes):
   - Go to your repo → Settings → Secrets → Actions
   - Add `DATABASE_URL` with the Neon connection string
   - Add `GROQ_API_KEY` from your `.env`
   - Add `ADZUNA_APP_ID` from your `.env`
   - Add `ADZUNA_API_KEY` from your `.env`

3. **Re-run workflows** (1 minute):
   - Go to Actions tab
   - Click failed workflow
   - Click "Re-run all jobs"

Total time: ~5-10 minutes to fix everything.

**Or just ignore them and focus on testing your local dashboard first!** ✅
