#!/usr/bin/env python
"""Initialize database with proper schema."""

import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from leap_ielts.data.database import init_db
from leap_ielts.utils.logging import setup_logging
from leap_ielts.utils.config import get_config


def main() -> None:
    """Initialize database."""
    config = get_config()
    setup_logging(config)
    logger = logging.getLogger(__name__)

    try:
        logger.info("Initializing database...")
        db = init_db(config.SQLALCHEMY_DATABASE_URI)
        logger.info(f"Database initialized successfully at: {config.SQLALCHEMY_DATABASE_URI}")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
