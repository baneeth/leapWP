"""SQLAlchemy ORM models for Leap IELTS system."""

from datetime import datetime, timedelta
from typing import Optional, List
from enum import Enum

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Boolean, ForeignKey,
    Enum as SQLEnum, Text, Table, UniqueConstraint, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash

Base = declarative_base()


class SkillType(str, Enum):
    """IELTS skill types."""

    READING = "reading"
    WRITING = "writing"
    LISTENING = "listening"
    SPEAKING = "speaking"


class ActivityType(str, Enum):
    """Activity types in the system."""

    READING = "reading"
    WRITING = "writing"
    LISTENING = "listening"
    SPEAKING = "speaking"
    MOCK_TEST = "mock_test"
    VOCABULARY = "vocabulary"


class DifficultyLevel(str, Enum):
    """Activity difficulty levels."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class TimelineGroup(str, Enum):
    """Preparation timeline groups."""

    SHORT_TERM = "short_term"  # 1-4 weeks
    MEDIUM_TERM = "medium_term"  # 5-12 weeks
    LONG_TERM = "long_term"  # 13+ weeks


class IncentiveType(str, Enum):
    """Types of incentives."""

    CAREER_COUNSELING_T1 = "career_counseling_tier_1"
    CAREER_COUNSELING_T2 = "career_counseling_tier_2"
    PREMIUM_CONTENT = "premium_content"
    GROUP_PRIORITY = "group_priority"


class GroupSessionStatus(str, Enum):
    """Status of group sessions."""

    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


# Association table for group session participants
group_session_participants = Table(
    "group_session_participants",
    Base.metadata,
    Column("group_session_id", Integer, ForeignKey("group_session.id"), primary_key=True),
    Column("user_id", Integer, ForeignKey("user.id"), primary_key=True),
)


class User(Base):
    """User profile and statistics."""

    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)

    # IELTS Profile
    target_score = Column(Float, default=6.5)  # 0.0-9.0
    preparation_timeline = Column(
        SQLEnum(TimelineGroup),
        default=TimelineGroup.MEDIUM_TERM
    )
    current_level = Column(Float, default=0.0)  # 0.0-9.0

    # Skill levels (0.0-9.0)
    reading_level = Column(Float, default=0.0)
    writing_level = Column(Float, default=0.0)
    listening_level = Column(Float, default=0.0)
    speaking_level = Column(Float, default=0.0)

    # Engagement metrics
    total_points = Column(Integer, default=0)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    last_activity_date = Column(DateTime)
    total_activities = Column(Integer, default=0)

    # Relationships
    activity_completions = relationship(
        "ActivityCompletion",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select"
    )
    daily_goals = relationship(
        "DailyGoal",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select"
    )
    streak_history = relationship(
        "StreakHistory",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select"
    )
    skill_progress = relationship(
        "SkillProgress",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select"
    )
    leaderboard_entries = relationship(
        "LeaderboardEntry",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select"
    )
    incentive_unlocks = relationship(
        "IncentiveUnlock",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select"
    )
    group_sessions = relationship(
        "GroupSession",
        secondary=group_session_participants,
        back_populates="participants",
        lazy="select"
    )

    __table_args__ = (
        Index("idx_user_target_timeline", "target_score", "preparation_timeline"),
    )

    def set_password(self, password: str) -> None:
        """Hash and set user password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify password against hash."""
        return check_password_hash(self.password_hash, password)

    def get_skill_level(self, skill: SkillType) -> float:
        """Get current skill level."""
        skill_map = {
            SkillType.READING: self.reading_level,
            SkillType.WRITING: self.writing_level,
            SkillType.LISTENING: self.listening_level,
            SkillType.SPEAKING: self.speaking_level,
        }
        return skill_map.get(skill, 0.0)

    def set_skill_level(self, skill: SkillType, level: float) -> None:
        """Set skill level (clamped to 0.0-9.0)."""
        clamped = max(0.0, min(9.0, level))
        if skill == SkillType.READING:
            self.reading_level = clamped
        elif skill == SkillType.WRITING:
            self.writing_level = clamped
        elif skill == SkillType.LISTENING:
            self.listening_level = clamped
        elif skill == SkillType.SPEAKING:
            self.speaking_level = clamped

    def __repr__(self) -> str:
        return f"<User {self.username} (streak={self.current_streak})>"


class Activity(Base):
    """IELTS practice activities."""

    __tablename__ = "activity"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    activity_type = Column(SQLEnum(ActivityType), nullable=False)
    skill = Column(SQLEnum(SkillType), nullable=False)
    difficulty = Column(SQLEnum(DifficultyLevel), nullable=False)
    duration_minutes = Column(Integer, nullable=False)  # 5-60
    points_reward = Column(Integer, default=10)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    completions = relationship(
        "ActivityCompletion",
        back_populates="activity",
        cascade="all, delete-orphan",
        lazy="select"
    )

    __table_args__ = (
        Index("idx_activity_type_difficulty", "activity_type", "difficulty"),
    )

    def __repr__(self) -> str:
        return f"<Activity {self.title} ({self.skill.value})>"


class ActivityCompletion(Base):
    """Records of activity completions by users."""

    __tablename__ = "activity_completion"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    activity_id = Column(Integer, ForeignKey("activity.id"), nullable=False)
    completed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    score = Column(Float, nullable=False)  # 0-100
    points_earned = Column(Integer, nullable=False)
    time_spent_minutes = Column(Integer)
    notes = Column(Text)

    # Relationships
    user = relationship("User", back_populates="activity_completions", lazy="select")
    activity = relationship("Activity", back_populates="completions", lazy="select")

    __table_args__ = (
        Index("idx_completion_user_date", "user_id", "completed_at"),
    )

    def __repr__(self) -> str:
        return f"<Completion user={self.user_id} score={self.score}>"


class DailyGoal(Base):
    """Daily goal assignments for users."""

    __tablename__ = "daily_goal"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    activity_id = Column(Integer, ForeignKey("activity.id"), nullable=False)
    assigned_date = Column(DateTime, nullable=False, index=True)
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime)
    completion_score = Column(Float)

    # Assignment metadata
    target_skill = Column(SQLEnum(SkillType), nullable=False)
    skill_gap = Column(Float, nullable=False)
    priority_score = Column(Float, nullable=False)

    # Relationships
    user = relationship("User", back_populates="daily_goals", lazy="select")

    __table_args__ = (
        Index("idx_daily_goal_user_date", "user_id", "assigned_date"),
    )

    def __repr__(self) -> str:
        return f"<DailyGoal user={self.user_id} date={self.assigned_date.date()}>"


class StreakHistory(Base):
    """Streak tracking and history."""

    __tablename__ = "streak_history"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    streak_count = Column(Integer, nullable=False)
    streak_started = Column(DateTime, nullable=False)
    streak_ended = Column(DateTime)
    broken_on = Column(DateTime)
    recovery_used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="streak_history", lazy="select")

    def __repr__(self) -> str:
        return f"<StreakHistory user={self.user_id} count={self.streak_count}>"


class SkillProgress(Base):
    """Temporal skill level tracking."""

    __tablename__ = "skill_progress"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    skill = Column(SQLEnum(SkillType), nullable=False)
    previous_level = Column(Float, nullable=False)
    new_level = Column(Float, nullable=False)
    adjustment = Column(Float, nullable=False)
    recent_scores = Column(Text)  # JSON: recent activity scores
    trigger_count = Column(Integer)  # Completions for this skill
    recorded_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="skill_progress", lazy="select")

    def __repr__(self) -> str:
        return f"<SkillProgress user={self.user_id} {self.skill.value}={self.new_level}>"


class LeaderboardEntry(Base):
    """Leaderboard rankings by consistency."""

    __tablename__ = "leaderboard_entry"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    target_score_group = Column(Float, nullable=False)  # Grouped score range
    timeline_group = Column(SQLEnum(TimelineGroup), nullable=False)
    rank = Column(Integer)
    previous_rank = Column(Integer)
    consistency_score = Column(Float, nullable=False)
    active_days = Column(Integer, nullable=False)
    current_streak = Column(Integer, nullable=False)
    goal_completion_rate = Column(Float, nullable=False)
    period_days = Column(Integer, default=30)
    calculated_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="leaderboard_entries", lazy="select")

    __table_args__ = (
        Index("idx_leaderboard_group_rank", "target_score_group", "timeline_group", "rank"),
    )

    def __repr__(self) -> str:
        return f"<LeaderboardEntry user={self.user_id} rank={self.rank}>"


class GroupSession(Base):
    """Speaking practice group sessions."""

    __tablename__ = "group_session"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(
        SQLEnum(GroupSessionStatus),
        default=GroupSessionStatus.SCHEDULED,
        nullable=False
    )
    scheduled_at = Column(DateTime, nullable=False)
    started_at = Column(DateTime)
    ended_at = Column(DateTime)
    target_skill = Column(SQLEnum(SkillType), default=SkillType.SPEAKING)
    min_participants = Column(Integer, default=2)
    max_participants = Column(Integer, default=6)
    host_id = Column(Integer, ForeignKey("user.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    participants = relationship(
        "User",
        secondary=group_session_participants,
        back_populates="group_sessions",
        lazy="select"
    )

    def participant_count(self) -> int:
        """Get number of participants."""
        return len(self.participants) if self.participants else 0

    def __repr__(self) -> str:
        return f"<GroupSession {self.title} ({self.status.value})>"


class IncentiveUnlock(Base):
    """Records of incentive unlocks."""

    __tablename__ = "incentive_unlock"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    incentive_type = Column(SQLEnum(IncentiveType), nullable=False)
    criteria_met = Column(Text)  # JSON: which criteria triggered unlock
    unlocked_at = Column(DateTime, default=datetime.utcnow)
    claimed_at = Column(DateTime)

    # Relationships
    user = relationship("User", back_populates="incentive_unlocks", lazy="select")

    __table_args__ = (
        UniqueConstraint("user_id", "incentive_type", name="unique_user_incentive"),
    )

    def __repr__(self) -> str:
        return f"<IncentiveUnlock user={self.user_id} {self.incentive_type.value}>"
