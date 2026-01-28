# Quick Start Guide - Leap IELTS

## Installation (5 minutes)

```bash
cd D:\leapWP

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Copy environment file
copy .env.example .env

# Initialize database
python scripts/setup_db.py

# (Optional) Load sample data
python scripts/seed_data.py
```

## Running the Web Application

```bash
flask run
```

Visit http://localhost:5000

### Demo Credentials (if seeded)
- Username: `student1`
- Password: `password123`

## Running the CLI

```bash
# View all users
python -m leap_ielts.cli.main user list

# View activities
python -m leap_ielts.cli.main activity list

# View user progress
python -m leap_ielts.cli.main progress summary --user-id 1

# Create new user
python -m leap_ielts.cli.main user create
```

## Key Features Implemented

### 1. Daily Goal Assignment
Intelligently assigns goals targeting weakest skills, with smart rotation and recency penalties.

### 2. Streak Tracking
Multi-day streak tracking with weekend recovery support. Milestones at 7, 14, and 30 days.

### 3. Skill Progress Analysis
Adaptive skill level tracking (0.0-9.0) using moving averages and recent performance.

### 4. Leaderboard Rankings
Consistency-based rankings combining:
- Active days (40%)
- Current streak (30%)
- Goal completion rate (30%)

### 5. Incentive Unlocks
Auto-detect when users reach:
- Career Counseling Tier 1
- Career Counseling Tier 2
- Premium Content
- Group Priority Status

## Project Structure

```
D:\leapWP\
├── src/leap_ielts/
│   ├── core/algorithms/          # 5 core algorithms
│   ├── core/services/            # 3+ service classes
│   ├── data/models.py            # 9 SQLAlchemy models
│   ├── data/repositories/        # 6 repositories
│   ├── web/app.py                # Flask app
│   ├── cli/main.py               # CLI commands
│   └── utils/                    # Config & logging
├── tests/                        # Unit & integration tests
├── scripts/                      # Setup & seed scripts
└── data/database/                # SQLite database
```

## Running Tests

```bash
# All tests
pytest tests/ -v --cov=src/leap_ielts

# Specific test file
pytest tests/unit/test_goal_assignment.py -v

# Coverage report
pytest tests/ --cov=src/leap_ielts --cov-report=html
```

## Code Quality

```bash
# Format code
black src/ tests/

# Lint
flake8 src/ tests/

# Type check
mypy src/
```

## Common Tasks

### Add Activity
```python
from leap_ielts.core.services.activity_service import ActivityService
from leap_ielts.data.models import ActivityType, SkillType, DifficultyLevel

service = ActivityService(session)
activity = service.create_activity(
    title="Reading Practice",
    activity_type=ActivityType.READING,
    skill=SkillType.READING,
    difficulty=DifficultyLevel.INTERMEDIATE,
    duration_minutes=12,
    content="Practice content here"
)
```

### Record Completion
```python
completion = service.complete_activity(
    user_id=1,
    activity_id=1,
    score=85.0,
    time_spent_minutes=12
)
```

### Assign Daily Goal
```python
from leap_ielts.core.algorithms.goal_assignment import GoalAssignmentAlgorithm

algorithm = GoalAssignmentAlgorithm(session)
goal = algorithm.assign_daily_goal(user)
```

### Get Progress Summary
```python
from leap_ielts.core.services.progress_service import ProgressService

service = ProgressService(session)
summary = service.get_user_progress_summary(user_id=1)
```

## Key Data Models

- **User**: Profile, targets, skill levels, engagement metrics
- **Activity**: Exercises with type, skill, difficulty, points
- **ActivityCompletion**: Score records with timestamp
- **DailyGoal**: Assigned daily practice goal
- **StreakHistory**: Streak tracking and recovery records
- **SkillProgress**: Temporal skill level history
- **LeaderboardEntry**: Consistency-based ranking
- **IncentiveUnlock**: Achievement milestone
- **GroupSession**: Speaking practice sessions

## Architecture Highlights

- **Repository Pattern**: Clean data access abstraction
- **Service Layer**: Business logic encapsulation
- **Core Algorithms**: Framework-independent implementations
- **Type Hints**: Full type coverage for IDE support
- **Error Handling**: Custom exception hierarchy
- **Logging**: Structured logging throughout

## Deployment Checklist

- [ ] Generate secure SECRET_KEY
- [ ] Configure DATABASE_URL for production DB
- [ ] Set FLASK_ENV=production
- [ ] Enable HTTPS/SSL
- [ ] Configure logging to file
- [ ] Set up APScheduler for background tasks
- [ ] Create database backups
- [ ] Monitor error logs

## Troubleshooting

### Database Issues
```bash
# Reset database (deletes all data)
python scripts/setup_db.py

# Reseed sample data
python scripts/seed_data.py
```

### Import Errors
- Ensure `.venv\Scripts\activate` is run
- Verify `pip install -e ".[dev]"` completed
- Check `PYTHONPATH` includes `src/`

### Test Failures
- Use in-memory SQLite for testing
- Check conftest.py fixtures
- Run `pytest --tb=short` for clearer output

## Next Steps

1. Explore the web interface at http://localhost:5000
2. Create a test user via the registration form
3. Complete some activities to build engagement
4. Check the CLI for progress reporting
5. Review IMPLEMENTATION_GUIDE.md for deeper understanding
6. Explore test files for usage examples

## Support

- Check README.md for overview
- See IMPLEMENTATION_GUIDE.md for technical details
- Review docstrings in source code
- Examine test files for examples
- Check comments in algorithm files

---

**Built with:** Flask 3.x, SQLAlchemy 2.x, Click, Rich
**Status:** Production-ready with extensible architecture
