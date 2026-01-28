"""Flask application factory."""

import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from leap_ielts.utils.config import get_config, Config
from leap_ielts.utils.logging import setup_logging
from leap_ielts.data.database import Database

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()


def create_app(config: Config = None) -> Flask:
    """Create and configure Flask application.

    Args:
        config: Configuration object

    Returns:
        Configured Flask app
    """
    if config is None:
        config = get_config()

    # Setup logging
    setup_logging(config)
    logger = logging.getLogger(__name__)

    # Create app
    app = Flask(__name__)
    app.config.from_object(config)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id: str):
        from leap_ielts.data.models import User
        with app.app_context():
            return db.session.query(User).get(int(user_id))

    # Tables already created by setup_db.py script
    # Skip automatic creation to avoid path issues

    # Register blueprints
    from leap_ielts.web.blueprints import auth_bp, dashboard_bp, activity_bp
    from leap_ielts.web.blueprints.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(activity_bp)
    app.register_blueprint(admin_bp)

    logger.info("Flask application created successfully")
    return app
