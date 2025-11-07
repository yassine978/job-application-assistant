"""Configuration management for the job application assistant."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).parent

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/jobassistant")
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", str(BASE_DIR / "chroma_db"))

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID", "")
ADZUNA_API_KEY = os.getenv("ADZUNA_API_KEY", "")

# App Settings
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Paths
GENERATED_DOCS_DIR = BASE_DIR / "generated_documents"
CVS_DIR = GENERATED_DOCS_DIR / "cvs"
COVER_LETTERS_DIR = GENERATED_DOCS_DIR / "cover_letters"
LOGS_DIR = BASE_DIR / "logs"

# Create directories if they don't exist
for directory in [GENERATED_DOCS_DIR, CVS_DIR, COVER_LETTERS_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# RAG Settings
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384
DEFAULT_K_RESULTS = 5
SIMILARITY_THRESHOLD = 0.7

# LLM Settings
LLM_MODEL = "llama-3.1-8b-instant"
LLM_TEMPERATURE = 0.7
MAX_TOKENS = 4000

# Scraping Settings
SCRAPE_DELAY = 2  # seconds between requests
MAX_JOBS_PER_SOURCE = 100

print(f"[OK] Configuration loaded. Debug mode: {DEBUG}")