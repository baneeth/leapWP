"""Custom exceptions for Leap IELTS system."""


class LeapException(Exception):
    """Base exception for Leap IELTS system."""

    pass


class UserNotFoundError(LeapException):
    """Raised when user cannot be found."""

    pass


class ActivityNotFoundError(LeapException):
    """Raised when activity cannot be found."""

    pass


class DuplicateUserError(LeapException):
    """Raised when trying to create duplicate user."""

    pass


class InvalidCredentialsError(LeapException):
    """Raised when credentials are invalid."""

    pass


class GoalAssignmentError(LeapException):
    """Raised when daily goal assignment fails."""

    pass


class StreakCalculationError(LeapException):
    """Raised when streak calculation fails."""

    pass


class SkillAnalysisError(LeapException):
    """Raised when skill analysis fails."""

    pass


class LeaderboardCalculationError(LeapException):
    """Raised when leaderboard calculation fails."""

    pass


class IncentiveUnlockError(LeapException):
    """Raised when incentive unlock fails."""

    pass
