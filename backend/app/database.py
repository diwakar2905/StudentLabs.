"""
Database Initialization & Setup

This script initializes the database with all required tables.
Use this to create the database schema from models.
"""

import logging
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.core.database import Base
from app.models import (
    User,
    Project,
    Paper,
    Summary,
    Assignment,
    Presentation,
    Export,
    Embedding,
)

logger = logging.getLogger(__name__)


def init_db():
    """
    Initialize database by creating all tables.
    
    Usage:
        from app.database import init_db
        init_db()
    """
    try:
        logger.info(f"Initializing database: {settings.DATABASE_URL}")
        
        # Create engine
        if "sqlite" in settings.DATABASE_URL:
            # For SQLite, use special connection parameters
            engine = create_engine(
                settings.DATABASE_URL,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
            )
        else:
            engine = create_engine(settings.DATABASE_URL)
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        logger.info("✅ Database initialized successfully")
        logger.info(f"Tables created: {', '.join(Base.metadata.tables.keys())}")
        
        return engine
        
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}", exc_info=True)
        raise


def drop_db():
    """
    Drop all tables from database.
    WARNING: Irreversible - deletes all data!
    
    Usage:
        from app.database import drop_db
        drop_db()
    """
    try:
        logger.warning("DROPPING ALL TABLES - THIS IS IRREVERSIBLE!")
        
        engine = create_engine(settings.DATABASE_URL)
        Base.metadata.drop_all(bind=engine)
        
        logger.info("✅ All tables dropped")
        
    except Exception as e:
        logger.error(f"Error dropping tables: {str(e)}", exc_info=True)
        raise


def reset_db():
    """
    Reset database: drop all tables and recreate.
    WARNING: Deletes all data!
    
    Usage:
        from app.database import reset_db
        reset_db()
    """
    logger.warning("RESETTING DATABASE - ALL DATA WILL BE LOST!")
    drop_db()
    init_db()
    logger.info("✅ Database reset complete")


if __name__ == "__main__":
    # Direct execution for initialization
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "init":
            init_db()
        elif command == "drop":
            response = input("WARNING: This will delete all data. Type 'yes' to confirm: ")
            if response.lower() == "yes":
                drop_db()
            else:
                print("Cancelled")
        elif command == "reset":
            response = input("WARNING: This will delete all data. Type 'yes' to confirm: ")
            if response.lower() == "yes":
                reset_db()
            else:
                print("Cancelled")
        else:
            print(f"Unknown command: {command}")
            print("Usage: python app/database.py [init|drop|reset]")
    else:
        # Default: initialize
        init_db()
