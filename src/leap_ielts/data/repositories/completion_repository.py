"""Activity completion repository for data access."""

from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc

from leap_ielts.data.models import ActivityCompletion, SkillType
from leap_ielts.data.repositories.base import BaseRepository


class CompletionRepository(BaseRepository[ActivityCompletion]):
    """Repository for ActivityCompletion model operations."""

    def __init__(self, session: Session):
        """Initialize completion repository."""
        super().__init__(ActivityCompletion, session)

    def get_user_completions(
        self,
        user_id: int,
        limit: int = 100,
        offset: int = 0
    ) -> List[ActivityCompletion]:
        """Get completions for a user.

        Args:
            user_id: User ID
            limit: Maximum results
            offset: Pagination offset

        Returns:
            List of completions
        """
        return self.session.query(ActivityCompletion).filter(
            ActivityCompletion.user_id == user_id
        ).order_by(desc(ActivityCompletion.completed_at)).offset(
            offset
        ).limit(limit).all()

    def get_user_completions_by_date(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> List[ActivityCompletion]:
        """Get user completions within date range.

        Args:
            user_id: User ID
            start_date: Start date
            end_date: End date

        Returns:
            List of completions
        """
        return self.session.query(ActivityCompletion).filter(
            ActivityCompletion.user_id == user_id,
            ActivityCompletion.completed_at >= start_date,
            ActivityCompletion.completed_at <= end_date
        ).order_by(desc(ActivityCompletion.completed_at)).all()

    def get_recent_completions(
        self,
        user_id: int,
        days: int = 7,
        limit: int = 100
    ) -> List[ActivityCompletion]:
        """Get user's recent completions.

        Args:
            user_id: User ID
            days: Number of days to look back
            limit: Maximum results

        Returns:
            List of recent completions
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return self.session.query(ActivityCompletion).filter(
            ActivityCompletion.user_id == user_id,
            ActivityCompletion.completed_at >= cutoff_date
        ).order_by(desc(ActivityCompletion.completed_at)).limit(limit).all()

    def get_last_completion(self, user_id: int) -> Optional[ActivityCompletion]:
        """Get user's most recent completion.

        Args:
            user_id: User ID

        Returns:
            Most recent completion or None
        """
        return self.session.query(ActivityCompletion).filter(
            ActivityCompletion.user_id == user_id
        ).order_by(desc(ActivityCompletion.completed_at)).first()

    def get_user_completions_count(
        self,
        user_id: int,
        days: Optional[int] = None
    ) -> int:
        """Get count of user completions.

        Args:
            user_id: User ID
            days: Optional - only count completions in last N days

        Returns:
            Count of completions
        """
        query = self.session.query(ActivityCompletion).filter(
            ActivityCompletion.user_id == user_id
        )
        if days:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            query = query.filter(ActivityCompletion.completed_at >= cutoff_date)
        return query.count()

    def get_active_days(
        self,
        user_id: int,
        days: int = 30
    ) -> int:
        """Get count of days with at least one completion.

        Args:
            user_id: User ID
            days: Number of days to check

        Returns:
            Number of active days
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        completions = self.session.query(ActivityCompletion).filter(
            ActivityCompletion.user_id == user_id,
            ActivityCompletion.completed_at >= cutoff_date
        ).all()

        # Count unique dates
        unique_dates = set(c.completed_at.date() for c in completions)
        return len(unique_dates)

    def get_average_score(
        self,
        user_id: int,
        days: Optional[int] = None
    ) -> float:
        """Get average score for user's completions.

        Args:
            user_id: User ID
            days: Optional - only average scores in last N days

        Returns:
            Average score (0-100) or 0.0 if no completions
        """
        query = self.session.query(ActivityCompletion).filter(
            ActivityCompletion.user_id == user_id
        )
        if days:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            query = query.filter(ActivityCompletion.completed_at >= cutoff_date)

        completions = query.all()
        if not completions:
            return 0.0

        total_score = sum(c.score for c in completions)
        return total_score / len(completions)

    def get_completions_by_activity(
        self,
        activity_id: int,
        limit: int = 100
    ) -> List[ActivityCompletion]:
        """Get all completions for an activity.

        Args:
            activity_id: Activity ID
            limit: Maximum results

        Returns:
            List of completions
        """
        return self.session.query(ActivityCompletion).filter(
            ActivityCompletion.activity_id == activity_id
        ).order_by(desc(ActivityCompletion.completed_at)).limit(limit).all()
