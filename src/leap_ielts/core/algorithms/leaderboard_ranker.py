"""Leaderboard ranking algorithm."""

import logging
from typing import List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from leap_ielts.data.models import User, LeaderboardEntry, TimelineGroup
from leap_ielts.data.repositories.user_repository import UserRepository
from leap_ielts.data.repositories.completion_repository import CompletionRepository
from leap_ielts.data.repositories.goal_repository import GoalRepository
from leap_ielts.data.repositories.leaderboard_repository import LeaderboardRepository
from leap_ielts.utils.config import Config

logger = logging.getLogger(__name__)


class LeaderboardRanker:
    """Algorithm for leaderboard ranking by consistency."""

    def __init__(self, session: Session, config: Config = None):
        """Initialize leaderboard ranker.

        Args:
            session: SQLAlchemy session
            config: Configuration object
        """
        self.session = session
        self.config = config or Config()
        self.user_repo = UserRepository(session)
        self.completion_repo = CompletionRepository(session)
        self.goal_repo = GoalRepository(session)
        self.leaderboard_repo = LeaderboardRepository(session)

    def calculate_leaderboards(self) -> int:
        """Calculate leaderboards for all groups.

        Returns:
            Number of leaderboard entries created
        """
        score_groups = self._get_score_groups()
        total_entries = 0

        for score_group in score_groups:
            for timeline_group in TimelineGroup:
                count = self._calculate_group_leaderboard(score_group, timeline_group)
                total_entries += count

        logger.info(f"Calculated leaderboards: {total_entries} entries")
        return total_entries

    def _get_score_groups(self) -> List[float]:
        """Get score groups for leaderboards.

        Returns:
            List of score group thresholds
        """
        return [5.0, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0]

    def _calculate_group_leaderboard(
        self,
        target_score_group: float,
        timeline_group: TimelineGroup
    ) -> int:
        """Calculate leaderboard for a specific group.

        Args:
            target_score_group: Target score threshold
            timeline_group: Timeline group

        Returns:
            Number of entries created
        """
        # Get users in this group
        min_score = target_score_group - 0.5
        users = self.user_repo.get_users_by_target_score_group(min_score, target_score_group)
        users = [u for u in users if u.preparation_timeline == timeline_group]

        if not users:
            logger.debug(f"No users for {target_score_group} / {timeline_group.value}")
            return 0

        # Calculate consistency score for each user
        entries = []
        for user in users:
            score = self._calculate_consistency_score(user)
            if score > 0:
                entries.append((user, score))

        # Sort by consistency score
        entries.sort(key=lambda x: x[1], reverse=True)

        # Delete old entries
        self.leaderboard_repo.delete_old_entries(target_score_group, timeline_group)

        # Create new entries
        created_count = 0
        for rank, (user, consistency_score) in enumerate(entries, 1):
            active_days = self.completion_repo.get_active_days(
                user.id,
                self.config.LEADERBOARD_PERIOD_DAYS
            )
            completion_rate = self.goal_repo.get_completion_rate(
                user.id,
                self.config.LEADERBOARD_PERIOD_DAYS
            )

            entry = LeaderboardEntry(
                user_id=user.id,
                target_score_group=target_score_group,
                timeline_group=timeline_group,
                rank=rank,
                consistency_score=consistency_score,
                active_days=active_days,
                current_streak=user.current_streak,
                goal_completion_rate=completion_rate,
                period_days=self.config.LEADERBOARD_PERIOD_DAYS,
            )
            self.session.add(entry)
            created_count += 1

        self.session.commit()
        logger.debug(f"Created {created_count} leaderboard entries for {target_score_group}")
        return created_count

    def _calculate_consistency_score(self, user: User) -> float:
        """Calculate consistency score for a user.

        Score = (active_days_score * 0.4) + (streak_score * 0.3) + (completion_score * 0.3)

        Args:
            user: User object

        Returns:
            Consistency score (0-100)
        """
        active_days = self.completion_repo.get_active_days(
            user.id,
            self.config.LEADERBOARD_PERIOD_DAYS
        )
        active_days_score = (
            (active_days / self.config.LEADERBOARD_PERIOD_DAYS) *
            100 *
            self.config.LEADERBOARD_ACTIVE_DAYS_WEIGHT
        )

        streak_score = (
            min(user.current_streak / 30, 1.0) *
            100 *
            self.config.LEADERBOARD_STREAK_WEIGHT
        )

        completion_rate = self.goal_repo.get_completion_rate(
            user.id,
            self.config.LEADERBOARD_PERIOD_DAYS
        )
        completion_score = (
            completion_rate *
            100 *
            self.config.LEADERBOARD_COMPLETION_WEIGHT
        )

        total_score = active_days_score + streak_score + completion_score
        return round(total_score, 1)

    def get_leaderboard(
        self,
        target_score: float,
        timeline: TimelineGroup,
        limit: int = 100
    ) -> List[LeaderboardEntry]:
        """Get leaderboard for a group.

        Args:
            target_score: Target score threshold
            timeline: Timeline group
            limit: Maximum entries

        Returns:
            List of leaderboard entries
        """
        return self.leaderboard_repo.get_leaderboard(target_score, timeline, limit)
