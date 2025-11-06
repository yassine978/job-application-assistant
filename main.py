"""Main entry point for the job application assistant."""

import config

def main():
    print("=" * 60)
    print("Job Application Assistant - Setup Verification")
    print("=" * 60)
    
    print(f"\n📁 Base Directory: {config.BASE_DIR}")
    print(f"💾 Database URL: {config.DATABASE_URL[:30]}...")
    print(f"🔑 Groq API Key: {'✅ Set' if config.GROQ_API_KEY else '❌ Not set'}")
    print(f"🧠 Embedding Model: {config.EMBEDDING_MODEL}")
    print(f"📊 Embedding Dimension: {config.EMBEDDING_DIMENSION}")
    
    print("\n✨ Setup complete! Ready for Phase 2.")

if __name__ == "__main__":
    main()