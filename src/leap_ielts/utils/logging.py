"""Logging configuration."""

import logging
import logging.handlers
from pathlib import Path
from leap_ielts.utils.config import Config


def setup_logging(config: Config) -> None:
    """Set up application logging.

    Args:
        config: Configuration object
    """
    # Get log level
    log_level = getattr(logging, config.LOG_LEVEL.upper(), logging.INFO)

    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter(
        "[%(asctime)s] %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # Set specific loggers
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("werkzeug").setLevel(logging.INFO)
