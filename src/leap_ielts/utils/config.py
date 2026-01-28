"""Configuration management for Leap IELTS system."""

import os
from pathlib import Path
from dotenv import load_dotenv


class Config:
    """Base configuration."""

    # Load .env file
    env_file = Path(__file__).parent.parent.parent.parent / ".env"
    if env_file.exists():
        load_dotenv(env_file)

    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    DEBUG = False
    TESTING = False

    # Database
    # Use absolute path for SQLite
    _db_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "data",
        "database",
        "leap_ielts.db"
    )
    _database_url = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{_db_path.replace(chr(92), '/')}"  # Convert backslashes to forward slashes
    )
    # Fix PostgreSQL URL format for SQLAlchemy 2.x
    if _database_url.startswith("postgres://"):
        _database_url = _database_url.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = _database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 3600,
    }

    # Scheduler
    SCHEDULER_ENABLED = os.getenv("SCHEDULER_ENABLED", "1") == "1"
    SCHEDULER_TIMEZONE = os.getenv("SCHEDULER_TIMEZONE", "UTC")

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "data/logs/app.log")

    # Security
    PASSWORD_MIN_LENGTH = int(os.getenv("PASSWORD_MIN_LENGTH", "8"))
    MAX_LOGIN_ATTEMPTS = int(os.getenv("MAX_LOGIN_ATTEMPTS", "5"))
    LOGIN_ATTEMPT_TIMEOUT = int(os.getenv("LOGIN_ATTEMPT_TIMEOUT", "900"))

    # Application
    APP_NAME = os.getenv("APP_NAME", "Leap IELTS Engagement System")
    APP_VERSION = os.getenv("APP_VERSION", "0.1.0")

    # IELTS Configuration
    MIN_IELTS_SCORE = 0.0
    MAX_IELTS_SCORE = 9.0
    DEFAULT_TARGET_SCORE = 6.5

    # Activity Configuration
    MIN_ACTIVITY_DURATION = 5
    MAX_ACTIVITY_DURATION = 60
    DEFAULT_ACTIVITY_POINTS = 10

    # Daily Goal Configuration
    DAILY_GOAL_DURATION_MIN = 5
    DAILY_GOAL_DURATION_MAX = 15
    GOAL_PRIORITY_SCALING = 2.0
    GOAL_RECENCY_PENALTY = 0.1

    # Streak Configuration
    WEEKEND_RECOVERY_ENABLED = True
    WEEKEND_RECOVERY_DAYS = (4, 0)  # Friday to Monday

    # Leaderboard Configuration
    LEADERBOARD_PERIOD_DAYS = 30
    LEADERBOARD_ACTIVE_DAYS_WEIGHT = 0.4
    LEADERBOARD_STREAK_WEIGHT = 0.3
    LEADERBOARD_COMPLETION_WEIGHT = 0.3
    LEADERBOARD_UPDATE_HOUR = 0  # Midnight

    # Skill Analysis Configuration
    SKILL_ANALYSIS_TRIGGER_COUNT = 5
    SKILL_MOVING_AVERAGE_ALPHA = 0.3
    SKILL_MAX_CHANGE_PER_UPDATE = 0.5

    # Incentive Configuration
    INCENTIVE_TIER1_STREAK = 7
    INCENTIVE_TIER1_ACTIVITIES = 30
    INCENTIVE_TIER1_POINTS = 500
    INCENTIVE_TIER2_STREAK = 30
    INCENTIVE_TIER2_ACTIVITIES = 100
    INCENTIVE_TIER2_POINTS = 2000
    INCENTIVE_PREMIUM_STREAK = 14
    INCENTIVE_PREMIUM_SKILL_ATTEMPTS = 5
    INCENTIVE_GROUP_SESSIONS = 5
    INCENTIVE_GROUP_PARTICIPATION_MIN = 0.7

    # Score-to-Adjustment Mapping
    SCORE_ADJUSTMENTS = {
        (90, 100): 0.3,
        (80, 89): 0.2,
        (70, 79): 0.1,
        (60, 69): 0.0,
        (50, 59): -0.1,
        (0, 49): -0.2,
    }


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True
    LOG_LEVEL = "DEBUG"


class TestingConfig(Config):
    """Testing configuration."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    LOG_LEVEL = "DEBUG"


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False
    LOG_LEVEL = "INFO"


def get_config(env: str = None) -> Config:
    """Get configuration based on environment.

    Args:
        env: Environment name (development, testing, production)

    Returns:
        Configuration object
    """
    if env is None:
        env = os.getenv("FLASK_ENV", "development")

    config_map = {
        "development": DevelopmentConfig,
        "testing": TestingConfig,
        "production": ProductionConfig,
    }

    return config_map.get(env, DevelopmentConfig)()
