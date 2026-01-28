"""Activity blueprint."""

from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

activity_bp = Blueprint("activity", __name__, url_prefix="/activity")


@activity_bp.route("/list")
@login_required
def list_activities():
    """List activities."""
    return render_template("activity/list.html", user=current_user)


@activity_bp.route("/daily-goal")
@login_required
def daily_goal():
    """Show today's daily goal."""
    return render_template("activity/daily_goal.html", user=current_user)
