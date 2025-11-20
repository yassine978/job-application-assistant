"""Database connection management."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool
import config
from database.models import Base

class DatabaseConnection:
    """Manage database connections and sessions."""
    
    def __init__(self, database_url=None):
        """Initialize database connection.
        
        Args:
            database_url: Database URL (uses config if not provided)
        """
        self.database_url = database_url or config.DATABASE_URL
        self.engine = None
        self.SessionLocal = None
        self._initialized = False
    
    def initialize(self):
        """Create engine and session factory."""
        if self._initialized:
            return
        
        # Create engine
        self.engine = create_engine(
            self.database_url,
            echo=config.DEBUG,
            pool_pre_ping=True,  # Verify connections before using
            pool_size=5,
            max_overflow=10
        )
        
        # Create session factory
        session_factory = sessionmaker(bind=self.engine)
        self.SessionLocal = scoped_session(session_factory)
        
        self._initialized = True
        print(f"[OK] Database connection initialized: {self.database_url[:30]}...")
    
    def create_tables(self):
        """Create all tables in the database."""
        if not self._initialized:
            self.initialize()
        
        Base.metadata.create_all(bind=self.engine)
        print("[OK] Database tables created successfully")
    
    def drop_tables(self):
        """Drop all tables (use with caution!)."""
        if not self._initialized:
            self.initialize()
        
        Base.metadata.drop_all(bind=self.engine)
        print("[WARNING] All tables dropped")
    
    def get_session(self):
        """Get a new database session.
        
        Returns:
            SQLAlchemy session
        """
        if not self._initialized:
            self.initialize()
        
        return self.SessionLocal()
    
    def close_session(self, session):
        """Close a database session.
        
        Args:
            session: SQLAlchemy session to close
        """
        if session:
            session.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self.get_session()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.SessionLocal:
            self.SessionLocal.remove()


# Global database connection instance
db_connection = DatabaseConnection()