"""Skill progress repository for data access."""

from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc

from leap_ielts.data.models import SkillProgress, SkillType
from leap_ielts.data.repositories.base import BaseRepository


class ProgressRepository(BaseRepository[SkillProgress]):
    """Repository for SkillProgress model operations."""

    def __init__(self, session: Session):
        """Initialize progress repository."""
        super().__init__(SkillProgress, session)

    def get_user_progress(
        self,
        user_id: int,
        limit: int = 100
    ) -> List[SkillProgress]:
        """Get all skill progress records for user.

        Args:
            user_id: User ID
            limit: Maximum results

        Returns:
            List of progress records
        """
        return self.session.query(SkillProgress).filter(
            SkillProgress.user_id == user_id
        ).order_by(desc(SkillProgress.recorded_at)).limit(limit).all()

    def get_user_skill_progress(
        self,
        user_id: int,
        skill: SkillType,
        limit: int = 100
    ) -> List[SkillProgress]:
        """Get progress records for a specific skill.

        Args:
            user_id: User ID
            skill: Skill type
            limit: Maximum results

        Returns:
            List of progress records
        """
        return self.session.query(SkillProgress).filter(
            SkillProgress.user_id == user_id,
            SkillProgress.skill == skill
        ).order_by(desc(SkillProgress.recorded_at)).limit(limit).all()

    def get_latest_skill_progress(
        self,
        user_id: int,
        skill: SkillType
    ) -> Optional[SkillProgress]:
        """Get most recent progress for a skill.

        Args:
            user_id: User ID
            skill: Skill type

        Returns:
            Most recent progress record or None
        """
        return self.session.query(SkillProgress).filter(
            SkillProgress.user_id == user_id,
            SkillProgress.skill == skill
        ).order_by(desc(SkillProgress.recorded_at)).first()

    def get_progress_history(
        self,
        user_id: int,
        skill: SkillType,
        days: int = 30
    ) -> List[SkillProgress]:
        """Get skill progress history over period.

        Args:
            user_id: User ID
            skill: Skill type
            days: Number of days to look back

        Returns:
            List of progress records
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        return self.session.query(SkillProgress).filter(
            SkillProgress.user_id == user_id,
            SkillProgress.skill == skill,
            SkillProgress.recorded_at >= cutoff_date
        ).order_by(desc(SkillProgress.recorded_at)).all()

    def get_all_skills_progress(self, user_id: int) -> dict[SkillType, Optional[SkillProgress]]:
        """Get latest progress for all skills.

        Args:
            user_id: User ID

        Returns:
            Dictionary mapping skill to latest progress
        """
        result = {}
        for skill in SkillType:
            latest = self.get_latest_skill_progress(user_id, skill)
            result[skill] = latest
        return result

    def get_skill_improvement(
        self,
        user_id: int,
        skill: SkillType,
        days: int = 30
    ) -> float:
        """Calculate skill improvement over period.

        Args:
            user_id: User ID
            skill: Skill type
            days: Number of days

        Returns:
            Improvement amount (new_level - old_level)
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        records = self.session.query(SkillProgress).filter(
            SkillProgress.user_id == user_id,
            SkillProgress.skill == skill,
            SkillProgress.recorded_at >= cutoff_date
        ).order_by(SkillProgress.recorded_at).all()

        if len(records) < 2:
            return 0.0

        oldest = records[0]
        newest = records[-1]
        return newest.new_level - oldest.previous_level

    def get_average_adjustment(
        self,
        user_id: int,
        skill: SkillType,
        limit: int = 10
    ) -> float:
        """Get average skill adjustment over recent updates.

        Args:
            user_id: User ID
            skill: Skill type
            limit: Number of recent updates

        Returns:
            Average adjustment
        """
        records = self.session.query(SkillProgress).filter(
            SkillProgress.user_id == user_id,
            SkillProgress.skill == skill
        ).order_by(desc(SkillProgress.recorded_at)).limit(limit).all()

        if not records:
            return 0.0

        total_adjustment = sum(r.adjustment for r in records)
        return total_adjustment / len(records)
