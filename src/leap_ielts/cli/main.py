"""CLI entry point for Leap IELTS system."""

import click
import sys
from pathlib import Path

# Ensure proper imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from leap_ielts.utils.config import get_config
from leap_ielts.utils.logging import setup_logging
from leap_ielts.data.database import init_db


@click.group()
@click.pass_context
def cli(ctx):
    """Leap IELTS Engagement System - CLI Interface."""
    config = get_config()
    setup_logging(config)

    # Initialize database and add to context
    db = init_db(config.SQLALCHEMY_DATABASE_URI)
    ctx.ensure_object(dict)
    ctx.obj["db"] = db
    ctx.obj["config"] = config


@cli.command()
@click.pass_context
def init_db_cmd(ctx):
    """Initialize database with schema."""
    db = ctx.obj["db"]
    click.echo("Database initialized successfully")


@cli.group()
def user():
    """User management commands."""
    pass


@user.command("create")
@click.option("--username", prompt="Username", help="Username for new account")
@click.option("--email", prompt="Email", help="Email address")
@click.option("--password", prompt=True, hide_input=True, help="Password")
@click.option("--target-score", default=6.5, help="Target IELTS score")
@click.pass_context
def create_user(ctx, username, email, password, target_score):
    """Create a new user."""
    from leap_ielts.core.services.user_service import UserService

    db = ctx.obj["db"]
    session = db.create_session()

    try:
        user_service = UserService(session)
        user = user_service.create_user(
            username=username,
            email=email,
            password=password,
            target_score=target_score
        )
        session.commit()
        click.echo(click.style(f"✓ Created user: {user.username}", fg="green"))
    except Exception as e:
        session.rollback()
        click.echo(click.style(f"✗ Error: {e}", fg="red"))
    finally:
        session.close()


@user.command("list")
@click.pass_context
def list_users(ctx):
    """List all users."""
    from leap_ielts.data.models import User

    db = ctx.obj["db"]
    session = db.create_session()

    try:
        users = session.query(User).all()
        if not users:
            click.echo("No users found")
            return

        click.echo(f"\n{'ID':<5} {'Username':<20} {'Email':<30} {'Streak':<10}")
        click.echo("-" * 65)
        for user in users:
            click.echo(
                f"{user.id:<5} {user.username:<20} {user.email:<30} {user.current_streak:<10}"
            )
    finally:
        session.close()


@cli.group()
def activity():
    """Activity management commands."""
    pass


@activity.command("list")
@click.option("--skill", help="Filter by skill (reading/writing/listening/speaking)")
@click.pass_context
def list_activities(ctx, skill):
    """List activities."""
    from leap_ielts.core.services.activity_service import ActivityService
    from leap_ielts.data.models import SkillType

    db = ctx.obj["db"]
    session = db.create_session()

    try:
        activity_service = ActivityService(session)

        if skill:
            activities = activity_service.get_activities_by_skill(
                SkillType[skill.upper()]
            )
        else:
            activities = activity_service.get_all_activities()

        if not activities:
            click.echo("No activities found")
            return

        click.echo(f"\n{'ID':<5} {'Title':<35} {'Skill':<12} {'Duration':<10}")
        click.echo("-" * 62)
        for activity in activities[:20]:
            skill_name = activity.skill.value if activity.skill else "N/A"
            click.echo(
                f"{activity.id:<5} {activity.title[:35]:<35} "
                f"{skill_name:<12} {activity.duration_minutes}min"
            )

        if len(activities) > 20:
            click.echo(f"\n... and {len(activities) - 20} more activities")
    finally:
        session.close()


@cli.group()
def progress():
    """Progress tracking commands."""
    pass


@progress.command("summary")
@click.option("--user-id", type=int, prompt="User ID", help="User ID")
@click.pass_context
def progress_summary(ctx, user_id):
    """Show user progress summary."""
    from leap_ielts.core.services.progress_service import ProgressService

    db = ctx.obj["db"]
    config = ctx.obj["config"]
    session = db.create_session()

    try:
        progress_service = ProgressService(session, config)
        summary = progress_service.get_user_progress_summary(user_id)

        user = summary["user"]
        click.echo(f"\n=== Progress Summary for {user['username']} ===\n")

        click.echo(f"Target Score: {user['target_score']}")
        click.echo(f"Current Level: {user['engagement']['total_points']} points")
        click.echo(f"Total Activities: {user['engagement']['total_activities']}")

        click.echo(f"\nStreak Info:")
        click.echo(f"  Current: {summary['streak']['current_streak']} days")
        click.echo(f"  Longest: {summary['streak']['longest_streak']} days")
        click.echo(f"  At Risk: {summary['streak']['at_risk']}")

        click.echo(f"\nSkill Levels:")
        for skill, info in summary["skills"].items():
            click.echo(
                f"  {skill.capitalize()}: {info['current_level']}/9.0 "
                f"(target: {info['target_score']})"
            )

        if summary["incentives"]["unlocked"]:
            click.echo(f"\nUnlocked Incentives:")
            for incentive in summary["incentives"]["unlocked"]:
                click.echo(f"  ✓ {incentive}")

    except Exception as e:
        click.echo(click.style(f"✗ Error: {e}", fg="red"))
    finally:
        session.close()


if __name__ == "__main__":
    cli(obj={})
