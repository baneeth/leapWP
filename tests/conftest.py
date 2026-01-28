"""Pytest configuration and fixtures."""

import sys
from pathlib import Path

import pytest
from sqlalchemy.orm import Session

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from leap_ielts.data.database import Database
from leap_ielts.utils.config import TestingConfig


@pytest.fixture(scope="function")
def db_session() -> Session:
    """Create a test database session."""
    db = Database(":memory:")
    db.initialize()

    session = db.create_session()
    yield session
    session.close()
    db.close()


@pytest.fixture
def config():
    """Return testing configuration."""
    return TestingConfig()


@pytest.fixture
def app():
    """Create test Flask application."""
    from leap_ielts.web.app import create_app

    config = TestingConfig()
    app = create_app(config)
    app.config["TESTING"] = True

    with app.app_context():
        yield app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()
