"""Authentication blueprint."""

import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from sqlalchemy.orm import Session

from leap_ielts.web.app import db
from leap_ielts.data.models import User
from leap_ielts.core.services.user_service import UserService
from leap_ielts.core.domain.exceptions import DuplicateUserError, InvalidCredentialsError

logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Register new user."""
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        password_confirm = request.form.get("password_confirm", "")

        # Validate
        if not username or not email or not password:
            flash("All fields are required", "danger")
            return redirect(url_for("auth.register"))

        if password != password_confirm:
            flash("Passwords do not match", "danger")
            return redirect(url_for("auth.register"))

        try:
            user_service = UserService(db.session)
            user = user_service.create_user(username, email, password)
            db.session.commit()

            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("auth.login"))

        except DuplicateUserError as e:
            db.session.rollback()
            flash(str(e), "danger")
        except ValueError as e:
            db.session.rollback()
            flash(str(e), "danger")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Registration error: {e}")
            flash("An error occurred during registration", "danger")

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Login user."""
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Username and password required", "danger")
            return redirect(url_for("auth.login"))

        try:
            user_service = UserService(db.session)
            user = user_service.authenticate_user(username, password)
            db.session.commit()

            login_user(user)
            logger.info(f"User logged in: {username}")

            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("dashboard.index"))

        except InvalidCredentialsError:
            flash("Invalid username or password", "danger")
        except Exception as e:
            logger.error(f"Login error: {e}")
            flash("An error occurred during login", "danger")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    """Logout user."""
    logout_user()
    flash("You have been logged out", "info")
    return redirect(url_for("auth.login"))
