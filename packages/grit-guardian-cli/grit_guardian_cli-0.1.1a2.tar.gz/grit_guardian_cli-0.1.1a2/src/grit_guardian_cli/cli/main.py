import re
import click
from functools import wraps  # Decorator factory to apply updates to wrapper function
from grit_guardian_cli.core.habit_tracker import HabitTracker
from grit_guardian_cli.persistence.database_manager import DatabaseManager
from grit_guardian_cli.ui.ui import GritUI
from grit_guardian_cli.analytics.analytics import identify_struggled_habits

_tracker = None


# Lazy loading the DatabaseManager instance to prevent initializing
# before test fixtures can patch the database path
def get_tracker():
    """Gets or creates the HabitTracker instance."""
    global _tracker
    if _tracker is None:
        db_manager = DatabaseManager()
        _tracker = HabitTracker(db_manager)
    return _tracker


def handle_error(func):
    """Decorator to handle errors consistently in theme"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            GritUI.show_error(str(e))
            return False

    return wrapper


@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    """🏰 Grit Guardian - Your Quest Companion"""
    if ctx.invoked_subcommand is None:
        GritUI.show_banner()
        GritUI.show_help_menu()


@main.command()
@click.argument("name")
@click.argument("task")
@click.argument("periodicity", type=click.Choice(["daily", "weekly"]))
@handle_error
def add(name, task, periodicity):
    """⚔️ Accept a new quest (add habit)."""

    # Business logic
    habit = get_tracker().add_habit(name, task, periodicity)

    # UI presentation
    # click.echo(f"{habit.name} has been inscribed in your Quest Log")
    GritUI.show_quest_added(habit.name, habit.task, habit.periodicity.value)

    return True


@main.command()
@handle_error
def list():
    """📜 View your Quest Log (list habits)."""
    # Business logic
    habits = get_tracker().list_habits()

    # UI presentation
    if not habits:
        GritUI.show_no_quests_message()

    GritUI.show_quest_log(habits)

    return True


@main.command()
@click.argument("name")
@handle_error
def delete(name):
    """🗡️ Abandon a quest (delete habit)."""
    # Confirmation
    if GritUI.confirm_quest_abandonment(name):
        # Business logic
        get_tracker().delete_habit(name)

        # UI presentation
        GritUI.show_quest_abandoned(name)
        return True
    return False


@main.command()
@click.argument("name")
@handle_error
def complete(name):
    """✅ Complete a quest (mark habit as done)."""
    # Business logic
    result = get_tracker().complete_habit(name)

    # UI presentation
    GritUI.show_quest_completed(result)

    # Show guardian reaction if available
    guardian = get_tracker().get_guardian()
    if guardian:
        GritUI.show_guardian_reaction(guardian)

    return True


@main.command()
@handle_error
def status():
    """🏰 View today's quest status."""
    # Business logic
    status = get_tracker().get_status()

    # UI presentation
    GritUI.show_daily_status(status)
    return True


@main.command()
@handle_error
def streaks():
    """🔥 View your Hall of Heroic Deeds (streaks)."""
    # Business logic
    streaks_data = get_tracker().get_streaks()

    # Calculate total stats
    total_current_streak = sum(s["current_streak"] for s in streaks_data)
    avg_completion_rate = sum(s["completion_rate"] for s in streaks_data) / len(
        streaks_data
    )

    GritUI.show_streaks(streaks_data, total_current_streak, avg_completion_rate)
    return True


@main.command()
@handle_error
def weekly():
    """📅 View Weekly Quest Chronicle."""
    # Business logic
    habits = get_tracker().list_habits()
    if not habits:
        GritUI.show_no_quests_message()
        return

    # UI presentation
    GritUI.show_weekly_progress(habits)
    return True


@main.command()
@click.option("--since", default=30, help="Days to analyze")
@handle_error
def struggled(since):
    """⚔️ View quests requiring renewed focus."""
    # Business logic
    habits = get_tracker().list_habits()
    struggled_habits = identify_struggled_habits(habits, since)

    # UI presentation
    GritUI.show_struggled_habits_alternative(struggled_habits, since)
    return True


@main.command()
def guardian():
    """View your Guardian's status"""
    guardian = get_tracker().get_guardian()
    GritUI.show_guardian(guardian)


@main.command()
@handle_error
def init():
    """🌟 Awaken your Guardian and begin your journey"""
    # Check if already initialized
    if get_tracker().list_habits():
        GritUI.show_already_initialized()
        return True

    # Business logic
    success = get_tracker().initialize_sample_data()

    if success:
        # UI presentation
        GritUI.show_initialization()

        # Show sample habits
        habits = get_tracker().list_habits()
        GritUI.show_sample_quests(habits)

        # Show initial guardian
        guardian = get_tracker().get_guardian()
        GritUI.show_guardian(guardian)
        GritUI.show_get_started()
    else:
        GritUI.show_error("Failed to awaken Guardian")

    return success


if __name__ == "__main__":
    main()
