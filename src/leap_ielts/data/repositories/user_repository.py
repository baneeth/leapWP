"""User repository for data access."""

from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from leap_ielts.data.models import User
from leap_ielts.data.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User model operations."""

    def __init__(self, session: Session):
        """Initialize user repository."""
        super().__init__(User, session)

    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username.

        Args:
            username: Username to search for

        Returns:
            User or None
        """
        return self.session.query(User).filter(User.username == username).first()

    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email.

        Args:
            email: Email to search for

        Returns:
            User or None
        """
        return self.session.query(User).filter(User.email == email).first()

    def get_active_users(self, days: int = 7) -> list[User]:
        """Get users active in the last N days.

        Args:
            days: Number of days to check

        Returns:
            List of active users
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return self.session.query(User).filter(
            User.last_activity_date >= cutoff_date
        ).all()

    def get_users_by_target_score_group(
        self,
        min_score: float,
        max_score: float
    ) -> list[User]:
        """Get users within target score range.

        Args:
            min_score: Minimum target score
            max_score: Maximum target score

        Returns:
            List of users
        """
        return self.session.query(User).filter(
            User.target_score >= min_score,
            User.target_score <= max_score
        ).all()

    def get_users_by_timeline(self, timeline: str) -> list[User]:
        """Get users by preparation timeline.

        Args:
            timeline: Timeline group value

        Returns:
            List of users
        """
        return self.session.query(User).filter(
            User.preparation_timeline == timeline
        ).all()

    def get_top_streaks(self, limit: int = 10) -> list[User]:
        """Get users with longest current streaks.

        Args:
            limit: Number of users to return

        Returns:
            List of users sorted by streak
        """
        return self.session.query(User).order_by(
            User.current_streak.desc()
        ).limit(limit).all()

    def get_top_points(self, limit: int = 10) -> list[User]:
        """Get users with most points.

        Args:
            limit: Number of users to return

        Returns:
            List of users sorted by points
        """
        return self.session.query(User).order_by(
            User.total_points.desc()
        ).limit(limit).all()
