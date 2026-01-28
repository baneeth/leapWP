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

    # Console handler (always enabled)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter(
        "[%(asctime)s] %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(console_formatter)

    # Add console handler
    root_logger.addHandler(console_handler)

    # File handler with rotation (only for local development)
    try:
        log_dir = Path(config.LOG_FILE).parent
        if log_dir.exists() or str(log_dir) != "data/logs":  # Only write to local filesystem
            log_dir.mkdir(parents=True, exist_ok=True)
            file_handler = logging.handlers.RotatingFileHandler(
                config.LOG_FILE,
                maxBytes=10485760,  # 10MB
                backupCount=5
            )
            file_handler.setLevel(log_level)
            file_formatter = logging.Formatter(
                "[%(asctime)s] %(name)s - %(levelname)s - %(message)s"
            )
            file_handler.setFormatter(file_formatter)
            root_logger.addHandler(file_handler)
    except Exception:
        # Skip file logging on Vercel or if filesystem not available
        pass

    # Set specific loggers
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("werkzeug").setLevel(logging.INFO)
