#!/usr/bin/env python
"""Seed database with sample data for testing."""

import sys
import logging
from pathlib import Path
from datetime import datetime, timedelta
import random

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from leap_ielts.data.database import init_db
from leap_ielts.data.models import (
    User,
    Activity,
    ActivityCompletion,
    DailyGoal,
    ActivityType,
    SkillType,
    DifficultyLevel,
    TimelineGroup,
)
from leap_ielts.utils.logging import setup_logging
from leap_ielts.utils.config import get_config
from leap_ielts.core.services.user_service import UserService
from leap_ielts.core.services.activity_service import ActivityService


def main() -> None:
    """Seed database with sample data."""
    config = get_config()
    setup_logging(config)
    logger = logging.getLogger(__name__)

    try:
        logger.info("Initializing database...")
        db = init_db(config.SQLALCHEMY_DATABASE_URI)
        session = db.create_session()

        logger.info("Seeding sample data...")

        # Create sample users
        user_service = UserService(session)
        users = []

        for i in range(5):
            try:
                user = user_service.create_user(
                    username=f"student{i+1}",
                    email=f"student{i+1}@leapielts.local",
                    password="password123",
                    target_score=6.5 + (i * 0.3),
                    timeline=random.choice(list(TimelineGroup)).value
                )
                users.append(user)
                logger.info(f"Created user: student{i+1}")
            except Exception as e:
                logger.warning(f"Failed to create user: {e}")
                session.rollback()

        # Create sample activities
        activity_service = ActivityService(session)
        activities = []

        activity_configs = [
            # Reading activities
            ("Reading Comprehension - Academic", ActivityType.READING, SkillType.READING, DifficultyLevel.INTERMEDIATE, 10),
            ("Reading Practice - Multiple Choice", ActivityType.READING, SkillType.READING, DifficultyLevel.ADVANCED, 12),
            ("Reading Speed Building", ActivityType.READING, SkillType.READING, DifficultyLevel.BEGINNER, 8),

            # Writing activities
            ("Essay Writing - Task 1", ActivityType.WRITING, SkillType.WRITING, DifficultyLevel.INTERMEDIATE, 15),
            ("Essay Writing - Task 2", ActivityType.WRITING, SkillType.WRITING, DifficultyLevel.ADVANCED, 15),
            ("Writing Practice - Short Format", ActivityType.WRITING, SkillType.WRITING, DifficultyLevel.BEGINNER, 10),

            # Listening activities
            ("Listening - Conversation", ActivityType.LISTENING, SkillType.LISTENING, DifficultyLevel.BEGINNER, 8),
            ("Listening - Lecture", ActivityType.LISTENING, SkillType.LISTENING, DifficultyLevel.INTERMEDIATE, 10),
            ("Listening - Academic", ActivityType.LISTENING, SkillType.LISTENING, DifficultyLevel.ADVANCED, 12),

            # Speaking activities
            ("Speaking - Part 1 Interview", ActivityType.SPEAKING, SkillType.SPEAKING, DifficultyLevel.BEGINNER, 8),
            ("Speaking - Part 2 Cue Card", ActivityType.SPEAKING, SkillType.SPEAKING, DifficultyLevel.INTERMEDIATE, 10),
            ("Speaking - Part 3 Discussion", ActivityType.SPEAKING, SkillType.SPEAKING, DifficultyLevel.ADVANCED, 12),
        ]

        for title, act_type, skill, difficulty, duration in activity_configs:
            try:
                activity = activity_service.create_activity(
                    title=title,
                    activity_type=act_type,
                    skill=skill,
                    difficulty=difficulty,
                    duration_minutes=duration,
                    content=f"Sample content for {title}",
                    description=f"Practice activity for {skill.value}",
                    points_reward=max(10, duration)
                )
                activities.append(activity)
                logger.info(f"Created activity: {title}")
            except Exception as e:
                logger.warning(f"Failed to create activity: {e}")
                session.rollback()

        # Create sample completions with history
        logger.info("Creating activity completions...")

        for user in users:
            # Create 20-30 completions per user with varying scores
            num_completions = random.randint(20, 30)
            for j in range(num_completions):
                activity = random.choice(activities)
                score = random.uniform(50, 95)
                days_ago = random.randint(0, 30)

                try:
                    completion = activity_service.complete_activity(
                        user_id=user.id,
                        activity_id=activity.id,
                        score=score,
                        time_spent_minutes=activity.duration_minutes,
                    )

                    # Adjust completion date
                    completion.completed_at = datetime.utcnow() - timedelta(days=days_ago)
                    session.commit()

                except Exception as e:
                    logger.warning(f"Failed to create completion: {e}")
                    session.rollback()

            logger.info(f"Created {num_completions} completions for {user.username}")

        # Update user activity dates for streak simulation
        logger.info("Simulating streaks...")

        for user in users:
            # Set last activity to recent
            user.last_activity_date = datetime.utcnow() - timedelta(days=random.randint(0, 3))
            user.current_streak = random.randint(1, 15)
            user.longest_streak = max(user.current_streak, random.randint(15, 30))
            session.commit()
            logger.info(f"Updated {user.username} streak: {user.current_streak} days")

        # Create sample daily goals
        logger.info("Creating daily goals...")

        for user in users:
            for i in range(5):
                activity = random.choice(activities)
                try:
                    goal = DailyGoal(
                        user_id=user.id,
                        activity_id=activity.id,
                        assigned_date=datetime.utcnow() - timedelta(days=5-i),
                        target_skill=activity.skill,
                        skill_gap=2.0 - (user.get_skill_level(activity.skill)),
                        priority_score=random.uniform(5, 15),
                        completed=random.random() > 0.3,
                    )
                    if goal.completed:
                        goal.completed_at = goal.assigned_date + timedelta(hours=random.randint(2, 8))
                        goal.completion_score = random.uniform(60, 95)

                    session.add(goal)
                    session.commit()
                except Exception as e:
                    logger.warning(f"Failed to create goal: {e}")
                    session.rollback()

            logger.info(f"Created daily goals for {user.username}")

        logger.info("Database seeding completed successfully!")
        session.close()

    except Exception as e:
        logger.error(f"Database seeding failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
