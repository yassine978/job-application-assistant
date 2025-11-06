"""Test database connection and table creation."""

from database.connection import db_connection
from database.models import User, UserProfile, Job

def test_connection():
    """Test database connection and create tables."""
    print("=" * 60)
    print("Testing Database Connection")
    print("=" * 60)
    
    try:
        # Initialize connection
        db_connection.initialize()
        
        # Create tables
        db_connection.create_tables()
        
        # Test with a session
        with db_connection as session:
            # Count users (should be 0)
            user_count = session.query(User).count()
            print(f"\n📊 Current users in database: {user_count}")
            
            print("\n✅ Database connection test successful!")
            print("✅ All tables created")
            
        return True
        
    except Exception as e:
        print(f"\n❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()