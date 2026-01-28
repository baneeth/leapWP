"""Skill progress analysis algorithm."""

import logging
from typing import List
from datetime import datetime
from sqlalchemy.orm import Session

from leap_ielts.data.models import User, SkillType, SkillProgress, ActivityCompletion
from leap_ielts.data.repositories.completion_repository import CompletionRepository
from leap_ielts.data.repositories.progress_repository import ProgressRepository
from leap_ielts.utils.config import Config

logger = logging.getLogger(__name__)


class SkillAnalyzer:
    """Algorithm for skill progress analysis."""

    def __init__(self, session: Session, config: Config = None):
        """Initialize skill analyzer.

        Args:
            session: SQLAlchemy session
            config: Configuration object
        """
        self.session = session
        self.config = config or Config()
        self.completion_repo = CompletionRepository(session)
        self.progress_repo = ProgressRepository(session)

    def analyze_and_update_skill(self, user: User, skill: SkillType) -> SkillProgress:
        """Analyze recent scores and update skill level.

        Process:
        1. Get recent 10 completions for skill
        2. Calculate average score
        3. Map to adjustment using scoring table
        4. Apply moving average
        5. Clamp to [0.0, 9.0]
        6. Max change ±0.5

        Args:
            user: User object
            skill: Target skill

        Returns:
            SkillProgress record
        """
        # Get recent completions for this skill
        all_completions = self.completion_repo.get_user_completions(user.id, limit=100)
        skill_completions = [
            c for c in all_completions
            if c.activity and c.activity.skill == skill
        ]

        if len(skill_completions) < self.config.SKILL_ANALYSIS_TRIGGER_COUNT:
            logger.debug(f"Not enough completions for {skill.value} analysis")
            return None

        # Get last 10 scores
        recent_scores = [c.score for c in skill_completions[:10]]
        avg_score = sum(recent_scores) / len(recent_scores)

        # Map score to adjustment
        adjustment = self._get_score_adjustment(avg_score)

        # Get current skill level
        current_level = user.get_skill_level(skill)

        # Apply moving average
        new_level = (
            current_level * (1 - self.config.SKILL_MOVING_AVERAGE_ALPHA) +
            adjustment * self.config.SKILL_MOVING_AVERAGE_ALPHA
        )

        # Clamp change
        change = new_level - current_level
        max_change = self.config.SKILL_MAX_CHANGE_PER_UPDATE
        if abs(change) > max_change:
            new_level = current_level + (max_change if change > 0 else -max_change)

        # Clamp to valid range
        new_level = max(0.0, min(9.0, new_level))

        # Update user
        user.set_skill_level(skill, new_level)
        self.session.commit()

        # Record progress
        progress = SkillProgress(
            user_id=user.id,
            skill=skill,
            previous_level=current_level,
            new_level=new_level,
            adjustment=adjustment,
            recent_scores=str(recent_scores),
            trigger_count=len(skill_completions),
        )
        self.session.add(progress)
        self.session.commit()

        logger.info(
            f"Updated {skill.value} for user {user.id}: "
            f"{current_level:.1f} -> {new_level:.1f}"
        )

        return progress

    def _get_score_adjustment(self, score: float) -> float:
        """Map score to skill adjustment.

        Args:
            score: Score (0-100)

        Returns:
            Adjustment value
        """
        for (min_score, max_score), adjustment in self.config.SCORE_ADJUSTMENTS.items():
            if min_score <= score <= max_score:
                return adjustment

        return 0.0

    def get_skill_progress_summary(self, user: User) -> dict:
        """Get skill progress summary.

        Args:
            user: User object

        Returns:
            Dictionary with skill stats
        """
        summary = {}
        for skill in SkillType:
            current = user.get_skill_level(skill)
            gap = user.target_score - current
            recent_progress = self.progress_repo.get_user_skill_progress(
                user.id,
                skill,
                limit=5
            )

            summary[skill.value] = {
                "current_level": round(current, 1),
                "target_score": user.target_score,
                "gap": round(gap, 1),
                "recent_updates": len(recent_progress),
            }

        return summary
