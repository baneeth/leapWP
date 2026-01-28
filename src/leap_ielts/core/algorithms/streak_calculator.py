"""Streak calculation algorithm."""

import logging
from typing import Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from leap_ielts.data.models import User, StreakHistory
from leap_ielts.data.repositories.user_repository import UserRepository
from leap_ielts.data.repositories.completion_repository import CompletionRepository
from leap_ielts.utils.config import Config

logger = logging.getLogger(__name__)


class StreakCalculator:
    """Algorithm for streak tracking and calculation."""

    def __init__(self, session: Session, config: Config = None):
        """Initialize streak calculator.

        Args:
            session: SQLAlchemy session
            config: Configuration object
        """
        self.session = session
        self.config = config or Config()
        self.user_repo = UserRepository(session)
        self.completion_repo = CompletionRepository(session)

    def update_streak(self, user: User) -> int:
        """Update user's streak based on activity.

        Logic:
        - days_gap = today - last_activity_date
        - IF gap == 0: Already counted (return current)
        - IF gap == 1: Consecutive day (increment)
        - IF gap == 2 AND last was Friday: Weekend recovery (increment)
        - ELSE: Streak broken (reset to 1)

        Args:
            user: User object

        Returns:
            Updated streak count
        """
        if user.last_activity_date is None:
            # First activity - start new streak
            user.current_streak = 1
            user.longest_streak = max(user.longest_streak, 1)
            self.user_repo.commit()
            logger.info(f"Started new streak for user {user.id}")
            return 1

        today = datetime.utcnow().date()
        last_activity_date = user.last_activity_date.date()
        days_gap = (today - last_activity_date).days

        if days_gap == 0:
            # Already counted today
            logger.debug(f"User {user.id} streak already counted for today")
            return user.current_streak

        if days_gap == 1:
            # Consecutive day
            user.current_streak += 1
            user.longest_streak = max(user.longest_streak, user.current_streak)
            self.user_repo.commit()
            logger.info(f"User {user.id} streak incremented to {user.current_streak}")
            return user.current_streak

        if days_gap == 2 and self._is_weekend_recovery_valid(user.last_activity_date):
            # Weekend recovery (Friday -> Monday)
            user.current_streak += 1
            user.longest_streak = max(user.longest_streak, user.current_streak)
            self.user_repo.commit()

            # Record recovery
            streak_history = StreakHistory(
                user_id=user.id,
                streak_count=user.current_streak,
                streak_started=user.last_activity_date,
                recovery_used=True,
            )
            self.session.add(streak_history)
            self.session.commit()

            logger.info(f"User {user.id} used weekend recovery (streak={user.current_streak})")
            return user.current_streak

        # Streak broken
        self._record_broken_streak(user)
        user.current_streak = 1
        user.longest_streak = max(user.longest_streak, 1)
        self.user_repo.commit()

        logger.info(f"User {user.id} streak broken after {days_gap} days, reset to 1")
        return 1

    def _is_weekend_recovery_valid(self, last_activity_datetime: datetime) -> bool:
        """Check if weekend recovery applies.

        Recovery applies if:
        - Last activity was Friday
        - Current day is Monday
        - Only 2 days gap (Friday to Sunday, activity on Monday)

        Args:
            last_activity_datetime: DateTime of last activity

        Returns:
            True if recovery applies
        """
        if not self.config.WEEKEND_RECOVERY_ENABLED:
            return False

        last_weekday = last_activity_datetime.weekday()  # 0=Monday, 4=Friday
        today_weekday = datetime.utcnow().weekday()

        # Friday (4) -> Monday (0)
        return last_weekday == 4 and today_weekday == 0

    def _record_broken_streak(self, user: User) -> None:
        """Record broken streak in history.

        Args:
            user: User object
        """
        if user.current_streak > 0:
            streak_history = StreakHistory(
                user_id=user.id,
                streak_count=user.current_streak,
                streak_started=datetime.utcnow() - timedelta(days=user.current_streak),
                streak_ended=datetime.utcnow(),
                broken_on=datetime.utcnow(),
            )
            self.session.add(streak_history)
            self.session.commit()

    def get_streak_info(self, user: User) -> dict:
        """Get comprehensive streak information.

        Args:
            user: User object

        Returns:
            Dictionary with streak stats
        """
        return {
            "current_streak": user.current_streak,
            "longest_streak": user.longest_streak,
            "last_activity": (
                user.last_activity_date.isoformat()
                if user.last_activity_date else None
            ),
            "days_since_activity": self._days_since_activity(user),
            "at_risk": self._is_streak_at_risk(user),
        }

    def _days_since_activity(self, user: User) -> int:
        """Calculate days since last activity.

        Args:
            user: User object

        Returns:
            Number of days, or -1 if never active
        """
        if user.last_activity_date is None:
            return -1

        days = (datetime.utcnow().date() - user.last_activity_date.date()).days
        return days

    def _is_streak_at_risk(self, user: User) -> bool:
        """Check if streak is at risk of breaking.

        At risk if no activity for 1+ days.

        Args:
            user: User object

        Returns:
            True if at risk
        """
        if user.current_streak == 0:
            return False

        days_since = self._days_since_activity(user)
        return days_since >= 1

    def get_streak_milestones(self, user: User) -> dict:
        """Get streak milestones and achievements.

        Args:
            user: User object

        Returns:
            Dictionary with milestone info
        """
        return {
            "week_milestone": user.current_streak >= 7,
            "two_weeks_milestone": user.current_streak >= 14,
            "month_milestone": user.current_streak >= 30,
            "days_until_week": max(0, 7 - user.current_streak),
            "days_until_month": max(0, 30 - user.current_streak),
        }
