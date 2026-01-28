"""Dashboard blueprint."""

from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/")


@dashboard_bp.route("/")
@dashboard_bp.route("/dashboard")
@login_required
def index():
    """Dashboard home page."""
    return render_template("dashboard/index.html", user=current_user)


@dashboard_bp.route("/profile")
@login_required
def profile():
    """User profile page."""
    return render_template("dashboard/profile.html", user=current_user)
