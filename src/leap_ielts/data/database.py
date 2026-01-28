"""Database initialization and session management."""

import os
from pathlib import Path
from typing import Optional, Generator
import logging

from sqlalchemy import create_engine, event, Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from leap_ielts.data.models import Base


logger = logging.getLogger(__name__)


class Database:
    """Database connection and session management."""

    def __init__(self, database_url: Optional[str] = None):
        """Initialize database.

        Args:
            database_url: SQLAlchemy database URL. Defaults to SQLite in data/database/
        """
        if database_url is None:
            # Create data/database directory if it doesn't exist
            db_dir = Path("data") / "database"
            db_dir.mkdir(parents=True, exist_ok=True)
            database_url = f"sqlite:///{db_dir}/leap_ielts.db"

        self.database_url = database_url
        self.engine: Optional[Engine] = None
        self.SessionLocal: Optional[sessionmaker] = None

    def initialize(self) -> None:
        """Initialize database engine and create tables."""
        # Check if using SQLite for memory DB
        if ":memory:" in self.database_url:
            self.engine = create_engine(
                self.database_url,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
            )
        else:
            self.engine = create_engine(
                self.database_url,
                echo=False,
                pool_pre_ping=True,
            )

        # Register SQLite-specific optimizations
        if self.database_url.startswith("sqlite"):
            @event.listens_for(Engine, "connect")
            def set_sqlite_pragma(dbapi_conn, connection_record):
                cursor = dbapi_conn.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.execute("PRAGMA journal_mode=WAL")
                cursor.execute("PRAGMA synchronous=NORMAL")
                cursor.close()

        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine,
        )

        # Create all tables
        Base.metadata.create_all(bind=self.engine)
        logger.info(f"Database initialized: {self.database_url}")

    def get_session(self) -> Generator[Session, None, None]:
        """Get a database session (for dependency injection).

        Yields:
            SQLAlchemy Session
        """
        if self.SessionLocal is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")

        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()

    def create_session(self) -> Session:
        """Create a new database session."""
        if self.SessionLocal is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        return self.SessionLocal()

    def drop_all(self) -> None:
        """Drop all tables. Use with caution!"""
        if self.engine is None:
            raise RuntimeError("Database not initialized.")
        Base.metadata.drop_all(bind=self.engine)
        logger.warning("All tables dropped")

    def close(self) -> None:
        """Close database connection."""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connection closed")


# Global database instance
_db: Optional[Database] = None


def get_db() -> Database:
    """Get the global database instance."""
    global _db
    if _db is None:
        _db = Database()
    return _db


def init_db(database_url: Optional[str] = None) -> Database:
    """Initialize the global database instance.

    Args:
        database_url: Optional SQLAlchemy database URL

    Returns:
        Initialized Database instance
    """
    global _db
    _db = Database(database_url)
    _db.initialize()
    return _db
