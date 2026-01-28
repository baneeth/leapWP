# Leap IELTS Engagement System

A professional Python-based IELTS preparation engagement system with advanced algorithms for goal assignment, streak tracking, leaderboard ranking, and skill progress analysis. Features both CLI and web interfaces for interactive learning and progress tracking.

## Features

- **Daily Goal Assignment**: Intelligent algorithm that targets skill gaps and encourages consistent practice
- **Streak Tracking**: Multi-day streak tracking with weekend recovery support
- **Skill Progress Analysis**: Adaptive skill level tracking based on recent performance
- **Leaderboard Rankings**: Consistency-focused rankings grouped by target score and timeline
- **Group Sessions**: Speaking practice sessions with participant matching
- **Incentive System**: Unlock career counseling and premium content based on achievement
- **Dual Interface**: Professional CLI (Click/Rich) and web interface (Flask/Jinja2)

## Technology Stack

- **Backend**: Flask 3.x, SQLAlchemy ORM, SQLite
- **CLI**: Click, Rich formatting
- **Web**: Flask blueprints, Jinja2 templates
- **Scheduling**: APScheduler for background tasks
- **Testing**: pytest with 80%+ coverage
- **Code Quality**: black, flake8, mypy, type hints

## Project Structure

```
D:\leapWP\
├── src/leap_ielts/
│   ├── core/                      # Business logic (framework-independent)
│   │   ├── algorithms/            # Core algorithms
│   │   │   ├── goal_assignment.py       # Daily goal selection
│   │   │   ├── streak_calculator.py     # Streak tracking
│   │   │   ├── leaderboard_ranker.py    # Consistency ranking
│   │   │   ├── skill_analyzer.py        # Skill progress
│   │   │   └── incentive_manager.py     # Unlock criteria
│   │   ├── services/              # Business services
│   │   └── domain/                # Domain models & enums
│   ├── data/                      # Data layer
│   │   ├── models.py              # SQLAlchemy models
│   │   ├── database.py            # DB initialization
│   │   └── repositories/          # Repository pattern
│   ├── web/                       # Flask web interface
│   │   ├── app.py                 # Application factory
│   │   ├── blueprints/            # Route handlers
│   │   └── templates/             # Jinja2 templates
│   ├── cli/                       # Click CLI interface
│   │   ├── main.py                # CLI entry point
│   │   └── commands/              # Command groups
│   └── utils/                     # Shared utilities
├── tests/                         # Test suite
├── data/                          # Runtime data
│   ├── database/                  # SQLite file
│   ├── content/                   # Activity content
│   └── logs/                      # Application logs
├── scripts/                       # Setup and utility scripts
└── docs/                          # Documentation
```

## Installation

### Prerequisites
- Python 3.10+
- pip

### Setup

1. Clone or extract the project
2. Navigate to project directory:
   ```bash
   cd D:\leapWP
   ```

3. Create and activate virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

4. Install dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

5. Copy environment file:
   ```bash
   copy .env.example .env
   ```

6. Initialize database:
   ```bash
   python scripts/setup_db.py
   ```

7. (Optional) Seed sample data:
   ```bash
   python scripts/seed_data.py
   ```

## Usage

### Web Interface

Start the Flask development server:
```bash
flask run
```

Navigate to http://localhost:5000

### CLI Interface

Access the CLI:
```bash
python -m leap_ielts.cli.main
```

Or with direct commands:
```bash
leap-cli user create
leap-cli activity list
leap-cli goal show
leap-cli streak status
```

## Core Algorithms

### Daily Goal Assignment

Targets the weakest skill based on:
- Skill gaps (difference from target score)
- Recency penalties (days since last practice)
- Rotation constraints (avoid same skill repeatedly)
- Activity filtering (5-15 minute duration)

### Streak Calculation

- Tracks consecutive active days
- Supports weekend recovery (Friday→Monday)
- Records streak history and milestones
- Resets on gaps > 2 days

### Leaderboard Ranking

Consistency-based scoring:
- Active Days Score: 40% (days active / period)
- Streak Score: 30% (current streak normalized)
- Goal Completion: 30% (completed / assigned)

Grouped by target score and timeline for fair comparison.

### Skill Progress Analysis

Adaptive skill tracking using:
- Recent performance averaging
- Moving average calculation (70% current, 30% adjustment)
- Score-to-adjustment mapping
- Clamped changes (±0.5 per update)

### Incentive Unlocking

Criteria for achievement unlocks:
- Career Counseling Tier 1: 7-day streak OR 30 activities OR 500 points
- Career Counseling Tier 2: 30-day streak OR 100 activities OR 2000 points
- Premium Content: 14-day streak AND all skills 5+ times
- Group Priority: 5+ sessions, avg participation > 70%

## Testing

Run all tests with coverage:
```bash
pytest tests/ -v --cov=src/leap_ielts --cov-report=html
```

Run specific test file:
```bash
pytest tests/unit/test_goal_assignment.py -v
```

Run integration tests:
```bash
pytest tests/integration/ -v
```

## Code Quality

Check code style:
```bash
black src/ tests/ --check
flake8 src/ tests/
mypy src/
pylint src/
```

Format code:
```bash
black src/ tests/
```

## Database

SQLite database stored at: `data/database/leap_ielts.db`

Critical indexes for performance are automatically created on initialization.

## Development

This project uses:
- **Type hints** for all function signatures
- **Google-style docstrings** for public methods
- **Repository pattern** for data access
- **Service layer** for business logic encapsulation
- **Custom exceptions** for error handling

## Configuration

Edit `.env` file for settings:
- `FLASK_ENV`: development or production
- `DATABASE_URL`: SQLite path
- `SCHEDULER_ENABLED`: Enable background scheduling
- `LOG_LEVEL`: DEBUG, INFO, WARNING, ERROR

## Performance

Optimized with:
- Database indexes on frequently queried columns
- Caching for leaderboard calculations
- Efficient query patterns using repositories
- Connection pooling with SQLAlchemy

## License

MIT License

## Author

Student Developer
