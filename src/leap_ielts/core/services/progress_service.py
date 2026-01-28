"""Progress service orchestrating skill and engagement tracking."""

import logging
from sqlalchemy.orm import Session

from leap_ielts.data.models import User, ActivityCompletion, SkillType
from leap_ielts.core.services.user_service import UserService
from leap_ielts.core.algorithms.streak_calculator import StreakCalculator
from leap_ielts.core.algorithms.skill_analyzer import SkillAnalyzer
from leap_ielts.core.algorithms.incentive_manager import IncentiveManager
from leap_ielts.utils.config import Config

logger = logging.getLogger(__name__)


class ProgressService:
    """Service for managing user progress and achievements."""

    def __init__(self, session: Session, config: Config = None):
        """Initialize progress service.

        Args:
            session: SQLAlchemy session
            config: Configuration object
        """
        self.session = session
        self.config = config or Config()
        self.user_service = UserService(session)
        self.streak_calculator = StreakCalculator(session, config)
        self.skill_analyzer = SkillAnalyzer(session, config)
        self.incentive_manager = IncentiveManager(session, config)

    def record_activity_completion(
        self,
        user_id: int,
        completion: ActivityCompletion
    ) -> dict:
        """Record activity completion and update all related metrics.

        Process:
        1. Add points to user
        2. Increment activity count
        3. Update last activity date
        4. Update streak
        5. Analyze skill progress
        6. Check for incentive unlocks

        Args:
            user_id: User ID
            completion: ActivityCompletion record

        Returns:
            Dictionary with update results
        """
        user = self.user_service.get_user_by_id(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        results = {
            "points_added": completion.points_earned,
            "streak_updated": False,
            "skill_analyzed": False,
            "incentives_unlocked": [],
        }

        # Update user metrics
        user.total_points += completion.points_earned
        user.total_activities += 1
        user.last_activity_date = completion.completed_at
        self.session.commit()

        # Update streak
        new_streak = self.streak_calculator.update_streak(user)
        results["streak_updated"] = True
        results["current_streak"] = new_streak

        # Analyze skill progress (trigger every N completions)
        if completion.activity and user.total_activities % self.config.SKILL_ANALYSIS_TRIGGER_COUNT == 0:
            progress = self.skill_analyzer.analyze_and_update_skill(
                user,
                completion.activity.skill
            )
            if progress:
                results["skill_analyzed"] = True
                results["skill_improvement"] = {
                    "skill": completion.activity.skill.value,
                    "previous": progress.previous_level,
                    "new": progress.new_level,
                }

        # Check incentive unlocks
        unlocked = self.incentive_manager.check_and_unlock_incentives(user)
        if unlocked:
            results["incentives_unlocked"] = [
                {
                    "type": u.incentive_type.value,
                    "criteria": u.criteria_met
                }
                for u in unlocked
            ]

        logger.info(f"Recorded completion for user {user_id}: {results}")
        return results

    def get_user_progress_summary(self, user_id: int) -> dict:
        """Get comprehensive progress summary for user.

        Args:
            user_id: User ID

        Returns:
            Dictionary with full progress stats
        """
        user = self.user_service.get_user_by_id(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        return {
            "user": self.user_service.get_user_summary(user_id),
            "streak": self.streak_calculator.get_streak_info(user),
            "streak_milestones": self.streak_calculator.get_streak_milestones(user),
            "skills": self.skill_analyzer.get_skill_progress_summary(user),
            "incentives": {
                "unlocked": [
                    u.incentive_type.value
                    for u in self.incentive_manager.get_user_unlocks(user_id)
                ]
            },
        }
