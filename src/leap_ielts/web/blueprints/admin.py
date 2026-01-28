"""Admin blueprint for database management."""

import logging
from flask import Blueprint, jsonify

logger = logging.getLogger(__name__)

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/init-db", methods=["POST", "GET"])
def init_db():
    """Initialize database tables.

    POST /admin/init-db - Initialize database
    Run this once after deployment to create all tables
    """
    try:
        from leap_ielts.web.app import db

        # Create all tables
        db.create_all()

        logger.info("Database initialized successfully")
        return jsonify(
            {
                "status": "success",
                "message": "Database initialized successfully",
                "tables_created": [
                    "user",
                    "activity",
                    "activity_completion",
                    "daily_goal",
                    "streak_history",
                    "skill_progress",
                    "leaderboard_entry",
                    "group_session",
                    "incentive_unlock",
                ],
            }
        ), 200

    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return (
            jsonify(
                {
                    "status": "error",
                    "message": f"Database initialization failed: {str(e)}",
                }
            ),
            500,
        )


@admin_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    try:
        from leap_ielts.web.app import db

        # Test database connection
        db.session.execute("SELECT 1")
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return jsonify(
        {
            "status": "healthy",
            "database": db_status,
            "service": "Leap IELTS Engagement System",
        }
    ), 200


@admin_bp.route("/db-status", methods=["GET"])
def db_status():
    """Check database status and table counts."""
    try:
        from leap_ielts.web.app import db
        from leap_ielts.data.models import User, Activity, ActivityCompletion

        user_count = db.session.query(User).count()
        activity_count = db.session.query(Activity).count()
        completion_count = db.session.query(ActivityCompletion).count()

        return jsonify(
            {
                "status": "ok",
                "counts": {
                    "users": user_count,
                    "activities": activity_count,
                    "completions": completion_count,
                },
            }
        ), 200

    except Exception as e:
        return jsonify(
            {
                "status": "error",
                "message": str(e),
            }
        ), 500
