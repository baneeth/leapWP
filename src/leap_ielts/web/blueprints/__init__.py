"""Flask blueprints for web routes."""

from leap_ielts.web.blueprints.auth import auth_bp
from leap_ielts.web.blueprints.dashboard import dashboard_bp
from leap_ielts.web.blueprints.activity import activity_bp
from leap_ielts.web.blueprints.admin import admin_bp

__all__ = ["auth_bp", "dashboard_bp", "activity_bp", "admin_bp"]
