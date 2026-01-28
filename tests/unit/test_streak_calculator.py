"""Tests for streak calculation algorithm."""

import pytest
from datetime import datetime, timedelta

from leap_ielts.data.models import User, TimelineGroup
from leap_ielts.core.algorithms.streak_calculator import StreakCalculator


def test_streak_increment_on_consecutive_days(db_session, config):
    """Test that streak increments on consecutive days."""
    user = User(
        username="testuser",
        email="test@test.local",
        target_score=7.0,
        preparation_timeline=TimelineGroup.MEDIUM_TERM,
        current_streak=5,
        last_activity_date=datetime.utcnow() - timedelta(days=1),
    )
    user.set_password("password123")
    db_session.add(user)
    db_session.commit()

    calculator = StreakCalculator(db_session, config)
    new_streak = calculator.update_streak(user)

    assert new_streak == 6


def test_streak_reset_on_gap(db_session, config):
    """Test that streak resets after gap > 2 days."""
    user = User(
        username="testuser",
        email="test@test.local",
        target_score=7.0,
        preparation_timeline=TimelineGroup.MEDIUM_TERM,
        current_streak=10,
        last_activity_date=datetime.utcnow() - timedelta(days=3),
    )
    user.set_password("password123")
    db_session.add(user)
    db_session.commit()

    calculator = StreakCalculator(db_session, config)
    new_streak = calculator.update_streak(user)

    assert new_streak == 1


def test_streak_weekend_recovery(db_session, config):
    """Test weekend recovery (Friday to Monday)."""
    # Set last activity to Friday
    friday = datetime.utcnow().replace(hour=12, minute=0, second=0, microsecond=0)
    # Find nearest Friday
    while friday.weekday() != 4:  # 4 = Friday
        friday -= timedelta(days=1)

    user = User(
        username="testuser",
        email="test@test.local",
        target_score=7.0,
        preparation_timeline=TimelineGroup.MEDIUM_TERM,
        current_streak=5,
        last_activity_date=friday,
    )
    user.set_password("password123")
    db_session.add(user)
    db_session.commit()

    # Move to Monday (if applicable)
    today = datetime.utcnow()
    if today.weekday() == 0 and (today.date() - friday.date()).days == 3:
        calculator = StreakCalculator(db_session, config)
        new_streak = calculator.update_streak(user)

        # Should use weekend recovery if enabled
        assert new_streak >= 5


def test_streak_milestones(db_session, config):
    """Test streak milestone detection."""
    for streak in [7, 14, 30]:
        user = User(
            username=f"testuser{streak}",
            email=f"test{streak}@test.local",
            target_score=7.0,
            preparation_timeline=TimelineGroup.MEDIUM_TERM,
            current_streak=streak,
        )
        user.set_password("password123")
        db_session.add(user)

    db_session.commit()

    calculator = StreakCalculator(db_session, config)

    # Test 7-day milestone
    user_7 = db_session.query(User).filter(User.username == "testuser7").first()
    milestones_7 = calculator.get_streak_milestones(user_7)
    assert milestones_7["week_milestone"] is True

    # Test 30-day milestone
    user_30 = db_session.query(User).filter(User.username == "testuser30").first()
    milestones_30 = calculator.get_streak_milestones(user_30)
    assert milestones_30["month_milestone"] is True
