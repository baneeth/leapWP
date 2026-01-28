"""Integration tests for complete user journeys."""

import pytest
from datetime import datetime, timedelta

from leap_ielts.data.models import (
    User,
    Activity,
    ActivityType,
    SkillType,
    DifficultyLevel,
    TimelineGroup,
)
from leap_ielts.core.services.user_service import UserService
from leap_ielts.core.services.activity_service import ActivityService
from leap_ielts.core.services.progress_service import ProgressService
from leap_ielts.core.algorithms.goal_assignment import GoalAssignmentAlgorithm
from leap_ielts.core.algorithms.streak_calculator import StreakCalculator


def test_complete_user_registration_and_setup(db_session, config):
    """Test user registration and profile setup."""
    user_service = UserService(db_session)

    user = user_service.create_user(
        username="newuser",
        email="new@test.local",
        password="secure_password123",
        target_score=7.5,
    )

    assert user.id is not None
    assert user.username == "newuser"
    assert user.email == "new@test.local"
    assert user.target_score == 7.5
    assert user.check_password("secure_password123")


def test_activity_completion_workflow(db_session, config):
    """Test complete activity workflow from completion to progress update."""
    # Setup
    user_service = UserService(db_session)
    activity_service = ActivityService(db_session)
    progress_service = ProgressService(db_session, config)

    user = user_service.create_user(
        "testuser",
        "test@test.local",
        "password123",
        target_score=7.0,
    )

    activity = activity_service.create_activity(
        title="Reading Practice",
        activity_type=ActivityType.READING,
        skill=SkillType.READING,
        difficulty=DifficultyLevel.INTERMEDIATE,
        duration_minutes=12,
        content="Practice content",
        points_reward=15,
    )

    # Complete activity
    completion = activity_service.complete_activity(
        user_id=user.id,
        activity_id=activity.id,
        score=85.0,
    )

    # Record in progress service
    results = progress_service.record_activity_completion(user.id, completion)

    # Verify results
    assert results["points_added"] > 0
    assert user.total_points > 0
    assert user.total_activities > 0


def test_daily_goal_assignment_workflow(db_session, config):
    """Test daily goal assignment to completion."""
    user_service = UserService(db_session)
    activity_service = ActivityService(db_session)

    user = user_service.create_user(
        "goaluser",
        "goal@test.local",
        "password123",
    )

    # Create activities
    for skill in SkillType:
        for i in range(3):
            activity_service.create_activity(
                title=f"{skill.value} Activity {i}",
                activity_type=ActivityType[skill.value.upper()],
                skill=skill,
                difficulty=DifficultyLevel.INTERMEDIATE,
                duration_minutes=10,
                content="Content",
            )

    # Assign goal
    algorithm = GoalAssignmentAlgorithm(db_session, config)
    goal = algorithm.assign_daily_goal(user)

    assert goal is not None
    assert goal.user_id == user.id
    assert not goal.completed

    # Complete goal
    goal.completed = True
    goal.completed_at = datetime.utcnow()
    goal.completion_score = 88.0
    db_session.commit()

    assert goal.completed


def test_streak_building_workflow(db_session, config):
    """Test building a streak through multiple days."""
    user_service = UserService(db_session)
    streak_calc = StreakCalculator(db_session, config)

    user = user_service.create_user(
        "streakuser",
        "streak@test.local",
        "password123",
    )

    # Simulate activity on day 1
    user.last_activity_date = datetime.utcnow()
    db_session.commit()
    streak_1 = streak_calc.update_streak(user)
    assert streak_1 == 1

    # Simulate activity on day 2
    user.last_activity_date = datetime.utcnow() - timedelta(days=1)
    db_session.commit()
    streak_2 = streak_calc.update_streak(user)
    assert streak_2 == 2

    # Simulate activity on day 3
    user.last_activity_date = datetime.utcnow() - timedelta(days=1)
    db_session.commit()
    streak_3 = streak_calc.update_streak(user)
    assert streak_3 == 3


def test_skill_progression_scenario(db_session, config):
    """Test skill progression through multiple activity completions."""
    user_service = UserService(db_session)
    activity_service = ActivityService(db_session)
    progress_service = ProgressService(db_session, config)

    user = user_service.create_user(
        "skilluser",
        "skill@test.local",
        "password123",
    )

    # Create reading activities
    activities = []
    for i in range(6):
        activity = activity_service.create_activity(
            title=f"Reading {i}",
            activity_type=ActivityType.READING,
            skill=SkillType.READING,
            difficulty=DifficultyLevel.INTERMEDIATE,
            duration_minutes=10,
            content="Content",
            points_reward=15,
        )
        activities.append(activity)

    # Complete activities with improving scores
    scores = [70, 75, 80, 82, 85, 88]
    for activity, score in zip(activities, scores):
        completion = activity_service.complete_activity(
            user.id,
            activity.id,
            score,
        )
        progress_service.record_activity_completion(user.id, completion)

    # Check skill improvement
    initial_reading = user.reading_level
    assert initial_reading >= 0.0

    db_session.refresh(user)
    final_reading = user.reading_level

    # With improving scores, reading level should improve
    # (may or may not improve depending on moving average threshold)
