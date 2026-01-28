"""Daily goal assignment algorithm."""

import logging
import random
from typing import Optional, List, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from leap_ielts.data.models import (
    User,
    Activity,
    DailyGoal,
    ActivityCompletion,
    SkillType,
    DifficultyLevel,
)
from leap_ielts.data.repositories.activity_repository import ActivityRepository
from leap_ielts.data.repositories.goal_repository import GoalRepository
from leap_ielts.data.repositories.completion_repository import CompletionRepository
from leap_ielts.utils.config import Config

logger = logging.getLogger(__name__)


class GoalAssignmentAlgorithm:
    """Algorithm for intelligent daily goal assignment."""

    def __init__(self, session: Session, config: Config = None):
        """Initialize goal assignment algorithm.

        Args:
            session: SQLAlchemy session
            config: Configuration object
        """
        self.session = session
        self.config = config or Config()
        self.activity_repo = ActivityRepository(session)
        self.goal_repo = GoalRepository(session)
        self.completion_repo = CompletionRepository(session)

    def assign_daily_goal(self, user: User) -> Optional[DailyGoal]:
        """Assign a daily goal to a user.

        Algorithm:
        1. Calculate skill gaps (target - current)
        2. Apply recency penalties for neglected skills
        3. Apply rotation constraint for variety
        4. Select target skill with highest priority
        5. Filter eligible activities
        6. Weighted random selection

        Args:
            user: User to assign goal to

        Returns:
            Created DailyGoal or None if no suitable activity
        """
        # Check if already has today's goal
        today_goal = self.goal_repo.get_today_goal(user.id)
        if today_goal:
            logger.debug(f"User {user.id} already has today's goal")
            return today_goal

        # Calculate skill gaps
        skill_gaps = self._calculate_skill_gaps(user)
        if not skill_gaps:
            logger.warning(f"User {user.id} has no skill gaps")
            return None

        # Apply recency penalties
        priority_scores = self._calculate_priority_scores(user, skill_gaps)

        # Apply rotation constraint (reduce priority if same skill yesterday)
        priority_scores = self._apply_rotation_constraint(user, priority_scores)

        # Select target skill
        target_skill = self._select_target_skill(priority_scores)
        if not target_skill:
            logger.warning(f"Could not select target skill for user {user.id}")
            return None

        # Find eligible activities
        eligible_activities = self._find_eligible_activities(target_skill)
        if not eligible_activities:
            logger.warning(f"No eligible activities found for skill {target_skill.value}")
            return None

        # Weighted selection (prefer not recently attempted)
        selected_activity = self._weighted_activity_selection(user, eligible_activities)
        if not selected_activity:
            selected_activity = random.choice(eligible_activities)

        # Create daily goal
        goal = self.goal_repo.create(
            user_id=user.id,
            activity_id=selected_activity.id,
            assigned_date=datetime.utcnow(),
            target_skill=target_skill,
            skill_gap=skill_gaps[target_skill],
            priority_score=priority_scores.get(target_skill, 0),
        )
        self.goal_repo.commit()

        logger.info(
            f"Assigned daily goal to user {user.id}: "
            f"{selected_activity.title} (skill={target_skill.value})"
        )
        return goal

    def _calculate_skill_gaps(self, user: User) -> dict[SkillType, float]:
        """Calculate gaps between current and target for each skill.

        Args:
            user: User object

        Returns:
            Dictionary mapping skill to gap
        """
        gaps = {}
        for skill in SkillType:
            current = user.get_skill_level(skill)
            gap = user.target_score - current
            gaps[skill] = max(0, gap)

        return gaps

    def _calculate_priority_scores(
        self,
        user: User,
        skill_gaps: dict[SkillType, float]
    ) -> dict[SkillType, float]:
        """Calculate priority scores for each skill.

        Factors:
        - Skill gap (higher gap = higher priority)
        - Recency penalty (days since practice)

        Args:
            user: User object
            skill_gaps: Skill gaps dictionary

        Returns:
            Dictionary mapping skill to priority score
        """
        priority_scores = {}

        for skill in SkillType:
            gap = skill_gaps[skill]
            recency_score = self._calculate_recency_penalty(user, skill)

            # Combined: gap weighted heavily, recency as tiebreaker
            priority = (gap * self.config.GOAL_PRIORITY_SCALING) + recency_score
            priority_scores[skill] = priority

        return priority_scores

    def _calculate_recency_penalty(self, user: User, skill: SkillType) -> float:
        """Calculate recency penalty for a skill.

        More days since practice = higher penalty/score

        Args:
            user: User object
            skill: Target skill

        Returns:
            Recency score
        """
        # Get last completion for this skill
        recent_completions = self.completion_repo.get_recent_completions(
            user.id,
            days=30,
            limit=10
        )

        # Filter for target skill
        skill_completions = [
            c for c in recent_completions
            if c.activity and c.activity.skill == skill
        ]

        if not skill_completions:
            # Never practiced this skill recently - high priority
            return 30 * self.config.GOAL_RECENCY_PENALTY

        # Calculate days since last practice
        last_completion = skill_completions[0]
        days_since = (datetime.utcnow() - last_completion.completed_at).days
        return days_since * self.config.GOAL_RECENCY_PENALTY

    def _apply_rotation_constraint(
        self,
        user: User,
        priority_scores: dict[SkillType, float]
    ) -> dict[SkillType, float]:
        """Apply rotation constraint to ensure variety.

        Reduce priority for skills practiced yesterday.

        Args:
            user: User object
            priority_scores: Current priority scores

        Returns:
            Adjusted priority scores
        """
        yesterday = datetime.utcnow() - timedelta(days=1)
        yesterday_start = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday_end = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)

        yesterday_goals = self.goal_repo.get_goals_in_date_range(
            user.id,
            yesterday_start,
            yesterday_end
        )

        adjusted_scores = priority_scores.copy()

        if yesterday_goals:
            yesterday_skills = {goal.target_skill for goal in yesterday_goals}
            # Reduce priority for yesterday's skills by 50%
            for skill in yesterday_skills:
                if skill in adjusted_scores:
                    adjusted_scores[skill] *= 0.5

        return adjusted_scores

    def _select_target_skill(self, priority_scores: dict[SkillType, float]) -> Optional[SkillType]:
        """Select target skill with highest priority.

        Args:
            priority_scores: Priority scores dictionary

        Returns:
            Selected SkillType or None
        """
        if not priority_scores:
            return None

        # Filter out zero-priority skills
        non_zero_scores = {k: v for k, v in priority_scores.items() if v > 0}
        if not non_zero_scores:
            return None

        # Select skill with highest priority
        target_skill = max(non_zero_scores, key=non_zero_scores.get)
        return target_skill

    def _find_eligible_activities(self, skill: SkillType) -> List[Activity]:
        """Find eligible activities for a skill.

        Criteria:
        - Matches target skill
        - Duration between 5-15 minutes
        - Mix of difficulties

        Args:
            skill: Target skill

        Returns:
            List of eligible activities
        """
        all_activities = self.activity_repo.get_by_skill(skill, limit=1000)

        eligible = [
            a for a in all_activities
            if (
                self.config.DAILY_GOAL_DURATION_MIN <= a.duration_minutes <=
                self.config.DAILY_GOAL_DURATION_MAX
            )
        ]

        return eligible

    def _weighted_activity_selection(
        self,
        user: User,
        activities: List[Activity]
    ) -> Optional[Activity]:
        """Select activity with weighted preference.

        Prefers activities not recently attempted.

        Args:
            user: User object
            activities: List of eligible activities

        Returns:
            Selected activity or None
        """
        if not activities:
            return None

        # Get recent completions
        recent_completions = self.completion_repo.get_recent_completions(
            user.id,
            days=7,
            limit=20
        )
        recent_activity_ids = {c.activity_id for c in recent_completions}

        # Calculate weights (not recently attempted = higher weight)
        weights = []
        for activity in activities:
            if activity.id in recent_activity_ids:
                weight = 1  # Low weight for recent
            else:
                weight = 3  # High weight for not recent

            weights.append(weight)

        # Weighted random selection
        if sum(weights) > 0:
            return random.choices(activities, weights=weights, k=1)[0]

        return None
