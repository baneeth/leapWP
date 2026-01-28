"""User service for user management operations."""

import logging
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session

from leap_ielts.data.models import User, TimelineGroup
from leap_ielts.data.repositories.user_repository import UserRepository
from leap_ielts.core.domain.exceptions import (
    UserNotFoundError,
    DuplicateUserError,
    InvalidCredentialsError,
)

logger = logging.getLogger(__name__)


class UserService:
    """Service for user management operations."""

    def __init__(self, session: Session):
        """Initialize user service.

        Args:
            session: SQLAlchemy session
        """
        self.session = session
        self.user_repo = UserRepository(session)

    def create_user(
        self,
        username: str,
        email: str,
        password: str,
        target_score: float = 6.5,
        timeline: str = TimelineGroup.MEDIUM_TERM.value
    ) -> User:
        """Create a new user.

        Args:
            username: Unique username
            email: Email address
            password: Password (will be hashed)
            target_score: Target IELTS score (0.0-9.0)
            timeline: Preparation timeline

        Returns:
            Created user

        Raises:
            DuplicateUserError: If username or email already exists
            ValueError: If input validation fails
        """
        # Validate input
        if not username or len(username) < 3:
            raise ValueError("Username must be at least 3 characters")
        if not email or "@" not in email:
            raise ValueError("Invalid email address")
        if not password or len(password) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not (0.0 <= target_score <= 9.0):
            raise ValueError("Target score must be between 0.0 and 9.0")

        # Check for duplicates
        if self.user_repo.get_by_username(username):
            raise DuplicateUserError(f"Username '{username}' already exists")
        if self.user_repo.get_by_email(email):
            raise DuplicateUserError(f"Email '{email}' already exists")

        # Create user
        user = self.user_repo.create(
            username=username,
            email=email,
            target_score=target_score,
            preparation_timeline=timeline,
        )
        user.set_password(password)
        self.user_repo.commit()

        logger.info(f"Created user: {username}")
        return user

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID.

        Args:
            user_id: User ID

        Returns:
            User or None
        """
        return self.user_repo.get_by_id(user_id)

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username.

        Args:
            username: Username

        Returns:
            User or None
        """
        return self.user_repo.get_by_username(username)

    def authenticate_user(self, username: str, password: str) -> User:
        """Authenticate user with password.

        Args:
            username: Username
            password: Password

        Returns:
            User if authenticated

        Raises:
            InvalidCredentialsError: If credentials are invalid
        """
        user = self.user_repo.get_by_username(username)
        if not user or not user.check_password(password):
            raise InvalidCredentialsError("Invalid username or password")

        # Update last login
        user.last_login = datetime.utcnow()
        self.user_repo.commit()

        logger.info(f"User authenticated: {username}")
        return user

    def update_user_profile(
        self,
        user_id: int,
        **kwargs
    ) -> User:
        """Update user profile information.

        Args:
            user_id: User ID
            **kwargs: Fields to update (target_score, preparation_timeline, etc.)

        Returns:
            Updated user

        Raises:
            UserNotFoundError: If user not found
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")

        # Allow specific fields to be updated
        allowed_fields = {
            "target_score",
            "preparation_timeline",
            "email",
        }

        for key, value in kwargs.items():
            if key in allowed_fields:
                if key == "target_score" and not (0.0 <= value <= 9.0):
                    raise ValueError("Target score must be between 0.0 and 9.0")
                setattr(user, key, value)

        self.user_repo.commit()
        logger.info(f"Updated user profile: {user.username}")
        return user

    def update_last_activity(self, user_id: int) -> User:
        """Update user's last activity date.

        Args:
            user_id: User ID

        Returns:
            Updated user

        Raises:
            UserNotFoundError: If user not found
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")

        user.last_activity_date = datetime.utcnow()
        self.user_repo.commit()
        return user

    def add_points(self, user_id: int, points: int) -> User:
        """Add points to user's total.

        Args:
            user_id: User ID
            points: Points to add

        Returns:
            Updated user

        Raises:
            UserNotFoundError: If user not found
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")

        user.total_points += points
        self.user_repo.commit()
        logger.info(f"Added {points} points to user {user.username}")
        return user

    def increment_activity_count(self, user_id: int) -> User:
        """Increment total activities count.

        Args:
            user_id: User ID

        Returns:
            Updated user

        Raises:
            UserNotFoundError: If user not found
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")

        user.total_activities += 1
        self.user_repo.commit()
        return user

    def get_user_summary(self, user_id: int) -> dict:
        """Get comprehensive user summary.

        Args:
            user_id: User ID

        Returns:
            Dictionary with user stats

        Raises:
            UserNotFoundError: If user not found
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")

        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "target_score": user.target_score,
            "current_level": user.current_level,
            "preparation_timeline": user.preparation_timeline.value if user.preparation_timeline else None,
            "skills": {
                "reading": user.reading_level,
                "writing": user.writing_level,
                "listening": user.listening_level,
                "speaking": user.speaking_level,
            },
            "engagement": {
                "total_points": user.total_points,
                "current_streak": user.current_streak,
                "longest_streak": user.longest_streak,
                "total_activities": user.total_activities,
            },
            "dates": {
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "last_login": user.last_login.isoformat() if user.last_login else None,
                "last_activity": user.last_activity_date.isoformat() if user.last_activity_date else None,
            }
        }

    def delete_user(self, user_id: int) -> None:
        """Delete a user.

        Args:
            user_id: User ID

        Raises:
            UserNotFoundError: If user not found
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")

        username = user.username
        self.user_repo.delete(user)
        self.user_repo.commit()
        logger.info(f"Deleted user: {username}")

    def get_active_users(self, days: int = 7) -> List[User]:
        """Get users active in the last N days.

        Args:
            days: Number of days

        Returns:
            List of active users
        """
        return self.user_repo.get_active_users(days)

    def get_top_performers(self, limit: int = 10) -> List[User]:
        """Get users with most points.

        Args:
            limit: Number of users

        Returns:
            List of users
        """
        return self.user_repo.get_top_points(limit)

    def get_top_streaks(self, limit: int = 10) -> List[User]:
        """Get users with longest streaks.

        Args:
            limit: Number of users

        Returns:
            List of users
        """
        return self.user_repo.get_top_streaks(limit)
