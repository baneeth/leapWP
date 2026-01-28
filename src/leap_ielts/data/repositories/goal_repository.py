"""Daily goal repository for data access."""

from typing import List, Optional
from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import desc

from leap_ielts.data.models import DailyGoal, SkillType
from leap_ielts.data.repositories.base import BaseRepository


class GoalRepository(BaseRepository[DailyGoal]):
    """Repository for DailyGoal model operations."""

    def __init__(self, session: Session):
        """Initialize goal repository."""
        super().__init__(DailyGoal, session)

    def get_user_goals(
        self,
        user_id: int,
        limit: int = 100
    ) -> List[DailyGoal]:
        """Get all goals for a user.

        Args:
            user_id: User ID
            limit: Maximum results

        Returns:
            List of goals
        """
        return self.session.query(DailyGoal).filter(
            DailyGoal.user_id == user_id
        ).order_by(desc(DailyGoal.assigned_date)).limit(limit).all()

    def get_today_goal(self, user_id: int) -> Optional[DailyGoal]:
        """Get today's goal for a user.

        Args:
            user_id: User ID

        Returns:
            Today's goal or None
        """
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = datetime.utcnow().replace(hour=23, minute=59, second=59, microsecond=999999)

        return self.session.query(DailyGoal).filter(
            DailyGoal.user_id == user_id,
            DailyGoal.assigned_date >= today_start,
            DailyGoal.assigned_date <= today_end
        ).first()

    def get_goals_by_date(
        self,
        user_id: int,
        target_date: date
    ) -> List[DailyGoal]:
        """Get goals for a specific date.

        Args:
            user_id: User ID
            target_date: Target date

        Returns:
            List of goals for that date
        """
        start = datetime.combine(target_date, datetime.min.time())
        end = datetime.combine(target_date, datetime.max.time())

        return self.session.query(DailyGoal).filter(
            DailyGoal.user_id == user_id,
            DailyGoal.assigned_date >= start,
            DailyGoal.assigned_date <= end
        ).all()

    def get_incomplete_goals(self, user_id: int) -> List[DailyGoal]:
        """Get incomplete goals for a user.

        Args:
            user_id: User ID

        Returns:
            List of incomplete goals
        """
        return self.session.query(DailyGoal).filter(
            DailyGoal.user_id == user_id,
            DailyGoal.completed == False
        ).order_by(desc(DailyGoal.assigned_date)).all()

    def get_completed_goals(
        self,
        user_id: int,
        limit: int = 100
    ) -> List[DailyGoal]:
        """Get completed goals for a user.

        Args:
            user_id: User ID
            limit: Maximum results

        Returns:
            List of completed goals
        """
        return self.session.query(DailyGoal).filter(
            DailyGoal.user_id == user_id,
            DailyGoal.completed == True
        ).order_by(desc(DailyGoal.completed_at)).limit(limit).all()

    def get_completion_rate(self, user_id: int, days: int = 30) -> float:
        """Get goal completion rate over period.

        Args:
            user_id: User ID
            days: Number of days to check

        Returns:
            Completion rate (0.0-1.0)
        """
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        total_goals = self.session.query(DailyGoal).filter(
            DailyGoal.user_id == user_id,
            DailyGoal.assigned_date >= cutoff_date
        ).count()

        if total_goals == 0:
            return 0.0

        completed_goals = self.session.query(DailyGoal).filter(
            DailyGoal.user_id == user_id,
            DailyGoal.assigned_date >= cutoff_date,
            DailyGoal.completed == True
        ).count()

        return completed_goals / total_goals

    def get_goals_by_skill(
        self,
        user_id: int,
        skill: SkillType,
        limit: int = 100
    ) -> List[DailyGoal]:
        """Get goals targeting a specific skill.

        Args:
            user_id: User ID
            skill: Skill type
            limit: Maximum results

        Returns:
            List of goals for that skill
        """
        return self.session.query(DailyGoal).filter(
            DailyGoal.user_id == user_id,
            DailyGoal.target_skill == skill
        ).order_by(desc(DailyGoal.assigned_date)).limit(limit).all()

    def get_goals_in_date_range(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> List[DailyGoal]:
        """Get goals assigned in date range.

        Args:
            user_id: User ID
            start_date: Start date
            end_date: End date

        Returns:
            List of goals in range
        """
        return self.session.query(DailyGoal).filter(
            DailyGoal.user_id == user_id,
            DailyGoal.assigned_date >= start_date,
            DailyGoal.assigned_date <= end_date
        ).order_by(desc(DailyGoal.assigned_date)).all()
