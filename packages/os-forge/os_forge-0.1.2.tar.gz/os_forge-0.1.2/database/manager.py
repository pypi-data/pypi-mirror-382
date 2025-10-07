"""
Database Manager for OS Forge

Handles database connections, sessions, and initialization.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .models import Base

# Database configuration
DATABASE_URL = "sqlite:///./policy_guard.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class DatabaseManager:
    """
    Database manager class for handling database operations
    """
    
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal
    
    def init_db(self):
        """Initialize database tables"""
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self) -> Session:
        """Get a database session"""
        return self.SessionLocal()
    
    def close_session(self, session: Session):
        """Close a database session"""
        session.close()


# Global database manager instance
db_manager = DatabaseManager()


def init_db():
    """Initialize database tables - convenience function"""
    db_manager.init_db()


def get_db():
    """
    Dependency function for FastAPI to get database sessions
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = db_manager.get_session()
    try:
        yield db
    finally:
        db_manager.close_session(db)

