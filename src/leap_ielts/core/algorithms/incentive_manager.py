"""Incentive unlock management algorithm."""

import logging
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from leap_ielts.data.models import User, IncentiveType, IncentiveUnlock
from leap_ielts.data.repositories.completion_repository import CompletionRepository
from leap_ielts.data.repositories.goal_repository import GoalRepository
from leap_ielts.utils.config import Config

logger = logging.getLogger(__name__)


class IncentiveManager:
    """Manager for incentive unlock criteria."""

    def __init__(self, session: Session, config: Config = None):
        """Initialize incentive manager.

        Args:
            session: SQLAlchemy session
            config: Configuration object
        """
        self.session = session
        self.config = config or Config()
        self.completion_repo = CompletionRepository(session)
        self.goal_repo = GoalRepository(session)

    def check_and_unlock_incentives(self, user: User) -> List[IncentiveUnlock]:
        """Check all incentive criteria and unlock any applicable.

        Args:
            user: User object

        Returns:
            List of newly unlocked incentives
        """
        unlocked = []

        # Check each incentive type
        if self._should_unlock_career_counseling_t1(user):
            incentive = self._unlock_incentive(
                user,
                IncentiveType.CAREER_COUNSELING_T1,
                "Career Counseling Tier 1"
            )
            if incentive:
                unlocked.append(incentive)

        if self._should_unlock_career_counseling_t2(user):
            incentive = self._unlock_incentive(
                user,
                IncentiveType.CAREER_COUNSELING_T2,
                "Career Counseling Tier 2"
            )
            if incentive:
                unlocked.append(incentive)

        if self._should_unlock_premium_content(user):
            incentive = self._unlock_incentive(
                user,
                IncentiveType.PREMIUM_CONTENT,
                "Premium Content Access"
            )
            if incentive:
                unlocked.append(incentive)

        return unlocked

    def _should_unlock_career_counseling_t1(self, user: User) -> bool:
        """Check if user qualifies for Tier 1 counseling.

        Criteria: 7-day streak OR 30 activities OR 500 points

        Args:
            user: User object

        Returns:
            True if criteria met
        """
        if user.current_streak >= self.config.INCENTIVE_TIER1_STREAK:
            return True

        if user.total_activities >= self.config.INCENTIVE_TIER1_ACTIVITIES:
            return True

        if user.total_points >= self.config.INCENTIVE_TIER1_POINTS:
            return True

        return False

    def _should_unlock_career_counseling_t2(self, user: User) -> bool:
        """Check if user qualifies for Tier 2 counseling.

        Criteria: 30-day streak OR 100 activities OR 2000 points

        Args:
            user: User object

        Returns:
            True if criteria met
        """
        if user.current_streak >= self.config.INCENTIVE_TIER2_STREAK:
            return True

        if user.total_activities >= self.config.INCENTIVE_TIER2_ACTIVITIES:
            return True

        if user.total_points >= self.config.INCENTIVE_TIER2_POINTS:
            return True

        return False

    def _should_unlock_premium_content(self, user: User) -> bool:
        """Check if user qualifies for premium content.

        Criteria: 14-day streak AND all skills practiced 5+ times

        Args:
            user: User object

        Returns:
            True if criteria met
        """
        if user.current_streak < self.config.INCENTIVE_PREMIUM_STREAK:
            return False

        # Check if all skills have 5+ completions
        all_completions = self.completion_repo.get_user_completions(user.id, limit=1000)

        from leap_ielts.data.models import SkillType
        skill_counts = {skill: 0 for skill in SkillType}

        for completion in all_completions:
            if completion.activity:
                skill_counts[completion.activity.skill] += 1

        # All skills must have 5+ completions
        return all(
            count >= self.config.INCENTIVE_PREMIUM_SKILL_ATTEMPTS
            for count in skill_counts.values()
        )

    def _unlock_incentive(
        self,
        user: User,
        incentive_type: IncentiveType,
        criteria_description: str
    ) -> Optional[IncentiveUnlock]:
        """Unlock an incentive for a user.

        Args:
            user: User object
            incentive_type: Type of incentive
            criteria_description: Description of unlocked criteria

        Returns:
            IncentiveUnlock record or None if already unlocked
        """
        # Check if already unlocked
        existing = self.session.query(IncentiveUnlock).filter(
            IncentiveUnlock.user_id == user.id,
            IncentiveUnlock.incentive_type == incentive_type,
        ).first()

        if existing:
            logger.debug(f"User {user.id} already has {incentive_type.value}")
            return None

        # Create unlock record
        unlock = IncentiveUnlock(
            user_id=user.id,
            incentive_type=incentive_type,
            criteria_met=criteria_description,
        )
        self.session.add(unlock)
        self.session.commit()

        logger.info(f"Unlocked {incentive_type.value} for user {user.id}")
        return unlock

    def get_user_unlocks(self, user_id: int) -> List[IncentiveUnlock]:
        """Get all unlocked incentives for a user.

        Args:
            user_id: User ID

        Returns:
            List of incentive unlocks
        """
        return self.session.query(IncentiveUnlock).filter(
            IncentiveUnlock.user_id == user_id
        ).all()

    def is_claimed(self, unlock_id: int) -> bool:
        """Check if incentive has been claimed.

        Args:
            unlock_id: Unlock record ID

        Returns:
            True if claimed
        """
        unlock = self.session.query(IncentiveUnlock).get(unlock_id)
        return unlock and unlock.claimed_at is not None

    def claim_incentive(self, unlock_id: int) -> Optional[IncentiveUnlock]:
        """Claim an incentive.

        Args:
            unlock_id: Unlock record ID

        Returns:
            Updated unlock record or None
        """
        unlock = self.session.query(IncentiveUnlock).get(unlock_id)
        if not unlock:
            return None

        unlock.claimed_at = datetime.utcnow()
        self.session.commit()

        logger.info(f"Claimed incentive {unlock.incentive_type.value} for user {unlock.user_id}")
        return unlock
