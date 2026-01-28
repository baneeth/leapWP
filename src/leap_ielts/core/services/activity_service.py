"""Activity service for activity management and completion tracking."""

import logging
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from leap_ielts.data.models import (
    Activity,
    ActivityCompletion,
    ActivityType,
    SkillType,
    DifficultyLevel,
)
from leap_ielts.data.repositories.activity_repository import ActivityRepository
from leap_ielts.data.repositories.completion_repository import CompletionRepository
from leap_ielts.core.domain.exceptions import ActivityNotFoundError

logger = logging.getLogger(__name__)


class ActivityService:
    """Service for activity management and completion tracking."""

    def __init__(self, session: Session):
        """Initialize activity service.

        Args:
            session: SQLAlchemy session
        """
        self.session = session
        self.activity_repo = ActivityRepository(session)
        self.completion_repo = CompletionRepository(session)

    def create_activity(
        self,
        title: str,
        activity_type: ActivityType,
        skill: SkillType,
        difficulty: DifficultyLevel,
        duration_minutes: int,
        content: str,
        description: str = "",
        points_reward: int = 10
    ) -> Activity:
        """Create a new activity.

        Args:
            title: Activity title
            activity_type: Type of activity
            skill: Target skill
            difficulty: Difficulty level
            duration_minutes: Duration in minutes
            content: Activity content
            description: Optional description
            points_reward: Points for completion

        Returns:
            Created activity

        Raises:
            ValueError: If input validation fails
        """
        if not title or len(title) < 3:
            raise ValueError("Title must be at least 3 characters")
        if not (5 <= duration_minutes <= 60):
            raise ValueError("Duration must be between 5 and 60 minutes")
        if not (1 <= points_reward <= 100):
            raise ValueError("Points must be between 1 and 100")

        activity = self.activity_repo.create(
            title=title,
            activity_type=activity_type,
            skill=skill,
            difficulty=difficulty,
            duration_minutes=duration_minutes,
            content=content,
            description=description,
            points_reward=points_reward,
        )
        self.activity_repo.commit()

        logger.info(f"Created activity: {title}")
        return activity

    def get_activity_by_id(self, activity_id: int) -> Optional[Activity]:
        """Get activity by ID.

        Args:
            activity_id: Activity ID

        Returns:
            Activity or None
        """
        return self.activity_repo.get_by_id(activity_id)

    def get_activities_by_skill(
        self,
        skill: SkillType,
        limit: int = 100
    ) -> List[Activity]:
        """Get activities for a skill.

        Args:
            skill: Skill type
            limit: Maximum results

        Returns:
            List of activities
        """
        return self.activity_repo.get_by_skill(skill, limit)

    def get_activities_by_difficulty(
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
        return self.activity_repo.get_by_skill_and_difficulty(skill, difficulty, limit)

    def complete_activity(
        self,
        user_id: int,
        activity_id: int,
        score: float,
        time_spent_minutes: int = None,
        notes: str = ""
    ) -> ActivityCompletion:
        """Record activity completion.

        Args:
            user_id: User ID
            activity_id: Activity ID
            score: Score achieved (0-100)
            time_spent_minutes: Optional time spent
            notes: Optional notes

        Returns:
            Completion record

        Raises:
            ActivityNotFoundError: If activity not found
            ValueError: If input validation fails
        """
        activity = self.activity_repo.get_by_id(activity_id)
        if not activity:
            raise ActivityNotFoundError(f"Activity {activity_id} not found")

        if not (0 <= score <= 100):
            raise ValueError("Score must be between 0 and 100")

        # Calculate points earned
        points_earned = int(activity.points_reward * (score / 100))

        completion = self.completion_repo.create(
            user_id=user_id,
            activity_id=activity_id,
            score=score,
            points_earned=points_earned,
            time_spent_minutes=time_spent_minutes,
            notes=notes,
        )
        self.completion_repo.commit()

        logger.info(f"User {user_id} completed activity {activity_id} with score {score}")
        return completion

    def get_user_completions(
        self,
        user_id: int,
        limit: int = 100,
        offset: int = 0
    ) -> List[ActivityCompletion]:
        """Get user's activity completions.

        Args:
            user_id: User ID
            limit: Maximum results
            offset: Pagination offset

        Returns:
            List of completions
        """
        return self.completion_repo.get_user_completions(user_id, limit, offset)

    def get_last_completion(self, user_id: int) -> Optional[ActivityCompletion]:
        """Get user's most recent completion.

        Args:
            user_id: User ID

        Returns:
            Most recent completion or None
        """
        return self.completion_repo.get_last_completion(user_id)

    def get_user_stats(self, user_id: int) -> dict:
        """Get activity statistics for a user.

        Args:
            user_id: User ID

        Returns:
            Dictionary with activity stats
        """
        total_count = self.completion_repo.get_user_completions_count(user_id)
        recent_count = self.completion_repo.get_user_completions_count(user_id, days=7)
        active_days = self.completion_repo.get_active_days(user_id, days=30)
        avg_score = self.completion_repo.get_average_score(user_id)

        return {
            "total_completions": total_count,
            "recent_completions_7d": recent_count,
            "active_days_30d": active_days,
            "average_score": round(avg_score, 1),
        }

    def get_all_activities(self, limit: int = 100) -> List[Activity]:
        """Get all activities.

        Args:
            limit: Maximum results

        Returns:
            List of all activities
        """
        return self.activity_repo.get_all(limit=limit)

    def count_activities(self) -> int:
        """Count total activities.

        Returns:
            Total count
        """
        return self.activity_repo.count()

    def search_activities(self, search_term: str, limit: int = 100) -> List[Activity]:
        """Search activities by title.

        Args:
            search_term: Search string
            limit: Maximum results

        Returns:
            List of matching activities
        """
        return self.activity_repo.search_by_title(search_term, limit)
