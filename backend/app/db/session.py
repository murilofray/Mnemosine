"""
Database session configuration and connection management.
"""

from typing import Generator

from app.config.settings import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Create SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    # Connection pool settings for PostgreSQL
    pool_pre_ping=True,
    pool_recycle=300,
)

# Create SessionLocal class
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Generator[Session, None, None]:
    """
    Database dependency for FastAPI.
    
    Yields a SQLAlchemy session and ensures it's properly closed.
    Use with FastAPI's Depends() for dependency injection.
    
    Example:
        @app.get("/items/")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 