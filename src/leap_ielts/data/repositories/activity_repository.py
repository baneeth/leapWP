"""Activity repository for data access."""

from typing import List, Optional
from sqlalchemy.orm import Session

from leap_ielts.data.models import Activity, ActivityType, SkillType, DifficultyLevel
from leap_ielts.data.repositories.base import BaseRepository


class ActivityRepository(BaseRepository[Activity]):
    """Repository for Activity model operations."""

    def __init__(self, session: Session):
        """Initialize activity repository."""
        super().__init__(Activity, session)

    def get_by_skill(
        self,
        skill: SkillType,
        limit: int = 100
    ) -> List[Activity]:
        """Get activities for a specific skill.

        Args:
            skill: Skill type to filter
            limit: Maximum results

        Returns:
            List of activities
        """
        return self.session.query(Activity).filter(
            Activity.skill == skill
        ).limit(limit).all()

    def get_by_skill_and_difficulty(
        self,
        skill: SkillType,
        difficulty: DifficultyLevel,
        limit: int = 100
    ) -> List[Activity]:
        """Get activities by skill and difficulty.

        Args:
            skill: Skill type
            difficulty: Difficulty level
            limit: Maximum results

        Returns:
            List of activities
        """
        return self.session.query(Activity).filter(
            Activity.skill == skill,
            Activity.difficulty == difficulty
        ).limit(limit).all()

    def get_by_type(
        self,
        activity_type: ActivityType,
        limit: int = 100
    ) -> List[Activity]:
        """Get activities by type.

        Args:
            activity_type: Activity type to filter
            limit: Maximum results

        Returns:
            List of activities
        """
        return self.session.query(Activity).filter(
            Activity.activity_type == activity_type
        ).limit(limit).all()

    def get_by_duration_range(
        self,
        min_minutes: int,
        max_minutes: int,
        limit: int = 100
    ) -> List[Activity]:
        """Get activities within duration range.

        Args:
            min_minutes: Minimum duration
            max_minutes: Maximum duration
            limit: Maximum results

        Returns:
            List of activities
        """
        return self.session.query(Activity).filter(
            Activity.duration_minutes >= min_minutes,
            Activity.duration_minutes <= max_minutes
        ).limit(limit).all()

    def get_random_by_criteria(
        self,
        skill: SkillType,
        difficulty: Optional[DifficultyLevel] = None,
        limit: int = 1
    ) -> List[Activity]:
        """Get random activities matching criteria.

        Args:
            skill: Skill type
            difficulty: Optional difficulty level
            limit: Number of results

        Returns:
            List of random activities
        """
        query = self.session.query(Activity).filter(Activity.skill == skill)
        if difficulty:
            query = query.filter(Activity.difficulty == difficulty)
        return query.order_by("RANDOM()").limit(limit).all()

    def search_by_title(
        self,
        title_search: str,
        limit: int = 100
    ) -> List[Activity]:
        """Search activities by title.

        Args:
            title_search: Title search string
            limit: Maximum results

        Returns:
            List of activities
        """
        return self.session.query(Activity).filter(
            Activity.title.ilike(f"%{title_search}%")
        ).limit(limit).all()
