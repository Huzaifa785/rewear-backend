# app/database.py - Enhanced with connection pooling and error handling
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import redis
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# Create database engine with connection pooling
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=300,    # Recycle connections every 5 minutes
    pool_size=5,         # Number of connections to maintain
    max_overflow=10,     # Additional connections if needed
    echo=settings.DEBUG  # Log SQL queries in debug mode
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base model class
Base = declarative_base()


def get_db():
    """
    Dependency to get database session with proper error handling
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def get_db_for_background_tasks():
    """
    Get database session for background tasks (like sending emails)
    """
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        logger.error(f"Background task DB session error: {e}")
        if db:
            db.close()
        raise


def test_db_connection() -> bool:
    """Test database connection"""
    try:
        db = SessionLocal()
        # Test with a simple query
        db.execute(text("SELECT 1"))
        db.close()
        return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False


def test_redis_connection() -> bool:
    """Test Redis connection"""
    try:
        if hasattr(settings, 'REDIS_URL') and settings.REDIS_URL:
            r = redis.from_url(settings.REDIS_URL)
            r.ping()
            return True
        else:
            logger.warning("Redis URL not configured")
            return False
    except Exception as e:
        logger.error(f"Redis connection test failed: {e}")
        return False


# Redis client (optional)
redis_client = None
try:
    if hasattr(settings, 'REDIS_URL') and settings.REDIS_URL:
        redis_client = redis.from_url(settings.REDIS_URL)
        redis_client.ping()  # Test connection
        logger.info("Redis connected successfully")
except Exception as e:
    logger.warning(f"Redis connection failed: {e}")
    redis_client = None