"""Leaderboard repository for data access."""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from leap_ielts.data.models import LeaderboardEntry, TimelineGroup
from leap_ielts.data.repositories.base import BaseRepository


class LeaderboardRepository(BaseRepository[LeaderboardEntry]):
    """Repository for LeaderboardEntry model operations."""

    def __init__(self, session: Session):
        """Initialize leaderboard repository."""
        super().__init__(LeaderboardEntry, session)

    def get_leaderboard(
        self,
        target_score_group: float,
        timeline_group: TimelineGroup,
        limit: int = 100
    ) -> List[LeaderboardEntry]:
        """Get leaderboard entries for a group.

        Args:
            target_score_group: Target score group
            timeline_group: Timeline group
            limit: Maximum results

        Returns:
            List of leaderboard entries sorted by rank
        """
        return self.session.query(LeaderboardEntry).filter(
            LeaderboardEntry.target_score_group == target_score_group,
            LeaderboardEntry.timeline_group == timeline_group
        ).order_by(LeaderboardEntry.rank).limit(limit).all()

    def get_user_entry(
        self,
        user_id: int,
        target_score_group: float,
        timeline_group: TimelineGroup
    ) -> Optional[LeaderboardEntry]:
        """Get user's leaderboard entry for a group.

        Args:
            user_id: User ID
            target_score_group: Target score group
            timeline_group: Timeline group

        Returns:
            User's leaderboard entry or None
        """
        return self.session.query(LeaderboardEntry).filter(
            LeaderboardEntry.user_id == user_id,
            LeaderboardEntry.target_score_group == target_score_group,
            LeaderboardEntry.timeline_group == timeline_group
        ).first()

    def get_top_players(
        self,
        target_score_group: float,
        timeline_group: TimelineGroup,
        limit: int = 10
    ) -> List[LeaderboardEntry]:
        """Get top players in a leaderboard group.

        Args:
            target_score_group: Target score group
            timeline_group: Timeline group
            limit: Number of top players

        Returns:
            List of top players
        """
        return self.session.query(LeaderboardEntry).filter(
            LeaderboardEntry.target_score_group == target_score_group,
            LeaderboardEntry.timeline_group == timeline_group
        ).order_by(
            LeaderboardEntry.consistency_score.desc()
        ).limit(limit).all()

    def get_all_timeline_groups(self) -> List[TimelineGroup]:
        """Get all active timeline groups.

        Returns:
            List of timeline groups
        """
        results = self.session.query(
            LeaderboardEntry.timeline_group
        ).distinct().all()
        return [r[0] for r in results]

    def get_all_score_groups(self) -> List[float]:
        """Get all active score groups.

        Returns:
            List of score groups
        """
        results = self.session.query(
            LeaderboardEntry.target_score_group
        ).distinct().all()
        return [r[0] for r in results]

    def get_rank_change(
        self,
        user_id: int,
        target_score_group: float,
        timeline_group: TimelineGroup
    ) -> int:
        """Get user's rank change since last update.

        Args:
            user_id: User ID
            target_score_group: Target score group
            timeline_group: Timeline group

        Returns:
            Rank change (positive = improved, negative = declined)
        """
        entry = self.get_user_entry(user_id, target_score_group, timeline_group)
        if not entry or entry.previous_rank is None:
            return 0

        return entry.previous_rank - entry.rank

    def delete_old_entries(
        self,
        target_score_group: float,
        timeline_group: TimelineGroup
    ) -> int:
        """Delete old leaderboard entries for recalculation.

        Args:
            target_score_group: Target score group
            timeline_group: Timeline group

        Returns:
            Number of entries deleted
        """
        count = self.session.query(LeaderboardEntry).filter(
            LeaderboardEntry.target_score_group == target_score_group,
            LeaderboardEntry.timeline_group == timeline_group
        ).delete()
        self.session.flush()
        return count

    def get_user_all_entries(self, user_id: int) -> List[LeaderboardEntry]:
        """Get all leaderboard entries for a user.

        Args:
            user_id: User ID

        Returns:
            List of user's entries across all groups
        """
        return self.session.query(LeaderboardEntry).filter(
            LeaderboardEntry.user_id == user_id
        ).all()
