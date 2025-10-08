from typing import List, Optional, Dict, Any
from datetime import datetime

from grit_guardian_cli.guardian.guardian import Guardian
from grit_guardian_cli.persistence.database_manager import DatabaseManager
from .models import Habit, Periodicity
from grit_guardian_cli.analytics.analytics import (
    calculate_streak,
    calculate_longest_streak,
    get_completion_rate,
)


class HabitNotFoundError(Exception):
    """Raised when a habit is not found in the database."""

    pass


class HabitAlreadyExistsError(Exception):
    """Raised when trying to create a habit with a name that already exists."""

    pass


# Does not interact with SQLite directly instead uses DatabaseManager
# Implementation has to respect SQLite's data types
class HabitTracker:
    """Service layer that orchestrates habit operations between CLI and database."""

    def __init__(self, db_manager: DatabaseManager):
        """Initializes the habit tracker with a database manager.

        Args:
            db_manager: DatabaseManager instance for persistence operations
        """
        self.db = db_manager  # To use DatabaseManager's methods
        self.guardian = Guardian()  # Initialize the Grid Guardian pet

    def add_habit(self, name: str, task: str, periodicity: str) -> Habit:
        """Creates a new habit and saves it to the database.

        Args:
            name: Unique name for the habit
            task: Description of the task
            periodicity: Either 'daily' or 'weekly'

        Returns:
            The created Habit instance

        Raises:
            HabitAlreadyExistsError: If a habit with the same name already exists
            ValueError: If inputs are invalid
        """
        # Validatye inputs
        if not name or not name.strip():  # Invalid for empty or only-whitespace inputs
            raise ValueError("Habit name cannot be empty")

        if not task or not task.strip():
            raise ValueError("Habit task cannot be empty")

        # Validate periodicity
        try:
            periodicity_enum = Periodicity(periodicity.lower())
        except ValueError:
            raise ValueError(
                f"Invalid periodicity: {periodicity}. Must be 'daily' or 'weekly'"
            )

        # Check if habit already exists
        existing_habit = self.db.get_habit_by_name(name)
        if existing_habit:
            raise HabitAlreadyExistsError(
                f"A habit with the name '{name}' already exists"
            )

        # Create habit in database
        try:
            habit_id = self.db.create_habit(name, task, periodicity_enum.value)

            # Create and return Habit instance
            habit = Habit(
                id=habit_id,
                name=name,
                task=task,
                periodicity=periodicity_enum,
                created_at=datetime.now(),
                completions=[],
            )

            return habit

        except Exception as e:
            raise ValueError(f"Failed to create habit: {str(e)}")

    def list_habits(self) -> List[Habit]:
        """Fetches all habits with their completion history.

        Returns:
            List of Habit instances with completion data
        """
        habits_data = self.db.get_habits()
        habits = []

        for habit_row in habits_data:
            # Create Habit instance from database row
            habit = Habit.from_db_row(habit_row)

            # Fetch completions for this habit
            if habit_row["total_completions"] > 0:
                completions = self.db.get_completions(habit.name)
                habit.completions = completions

            habits.append(habit)

        return habits

    def get_habit(self, name: str) -> Optional[Habit]:
        """Gets a specific habit by name.

        Args:
            name: The habit name to retrieve

        Returns:
            Habit instance of None if not found
        """
        habit_data = self.db.get_habit_by_name(name)
        if not habit_data:
            return None

        habit = Habit.from_db_row(habit_data)

        # Fetch completions
        completions = self.db.get_completions(name)
        habit.completions = completions

        return habit

    def delete_habit(self, name: str) -> bool:
        """Deletes a habit and all its completions.

        Args:
            name: The habit name to delete

        Returns:
            True if deleted, False if not found

        Raises:
            HabitNotFoundError: If the habit doesn't exist
        """
        # Check if habits exists
        if not self.db.get_habit_by_name(name):
            raise HabitNotFoundError(f"Habit '{name}' not found")

        # Delete from database (cascades to completions)
        return self.db.delete_habit(name)

    def complete_habit(
        self, name: str, completion_date: Optional[datetime] = None
    ) -> bool:
        """Marks a habit as completed.

        Args:
            name: The habit name to complete
            completion_date: Optional completion date (defaults to now)

        Returns:
            True if successful

        Raises:
            HabitNotFoundError: If the habit doesn't exist
            ValueError: If completion date is invalid
        """
        # Verify habit exists
        habit = self.get_habit(name)
        if not habit:
            raise HabitNotFoundError(f"Habit '{name}' not found")

        # Check if already completed today (for daily habits)
        if habit.periodicity == Periodicity.DAILY and habit.is_completed_today():
            raise ValueError(f"Habit '{name}' has already been completed today")

        # Check if already completed this week (for weekly habits)
        if habit.periodicity == Periodicity.WEEKLY and habit.is_completed_this_week():
            raise ValueError(f"Habit '{name}' has already been completed this week")

        try:
            # Add completion to database
            self.db.add_completion(name, completion_date)
            return True

        except ValueError as e:
            # Re-raise with more context
            raise ValueError(f"Failed to complete habit '{name}: {str(e)}")

    def get_habit_streak(self, name: str) -> int:
        """Get the current streak for a habit.

        Args:
            name: The habit name

        Returns:
            Current streak count

        Raises:
            HabitNotFoundError: If the habit doesn't exist
        """
        habit = self.get_habit(name)
        if not habit:
            raise HabitNotFoundError(f"Habit '{name}' not found")

        return habit.get_streak()

    def get_statistics(self) -> dict:
        """Gets overall statistics about habits and completions.

        Returns:
            Dictionary with various statistics
        """
        stats = self.db.get_stats()

        # Add additional stats
        habits = self.list_habits()

        # Calculate total strak across all habits
        total_streak = sum(habit.get_streak() for habit in habits)

        # Find habit with longest streak
        longest_streak_habit = None
        longest_streak = 0
        for habit in habits:
            streak = habit.get_streak()
            if streak > longest_streak:
                longest_streak = streak
                longest_streak_habit = habit.name

        stats.update(
            {
                "total_streak": total_streak,
                "longest_streak": longest_streak,
                "longest_streak_habit": longest_streak_habit,
                "active_habits": len([h for h in habits if h.get_streak() > 0]),
            }
        )

        return stats

    def get_status(self) -> Dict[str, Any]:
        """Gets today's habit status - pending and completed habits.

        Returns:
            Dictionary with pending, completed, and total habit counts
        """
        habits = self.list_habits()
        today_pending = []
        today_completed = []

        for habit in habits:
            if habit.periodicity == Periodicity.DAILY:
                if habit.is_completed_today():
                    today_completed.append(habit)
                else:
                    today_pending.append(habit)
            elif habit.periodicity == Periodicity.WEEKLY:
                if habit.is_completed_this_week():
                    today_completed.append(habit)
                else:
                    today_pending.append(habit)

        return {
            "pending": today_pending,
            "completed": today_completed,
            "total": len(habits),
        }

    def get_streaks(self) -> List[Dict[str, Any]]:
        """Gets streak analytics for all habits.

        Returns:
            List of dictionaries containing streak data for each habit
        """
        habits = self.list_habits()
        return [
            {
                "name": habit.name,
                "current_streak": calculate_streak(
                    habit.completions, habit.periodicity.value
                ),
                "longest_streak": calculate_longest_streak(
                    habit.completions, habit.periodicity.value
                ),
                "completion_rate": get_completion_rate(
                    habit.created_at, habit.completions, habit.periodicity.value
                ),
            }
            for habit in habits
        ]

    def get_guardian(self) -> Guardian:
        """Get the Guardian with its current mood based on habits performance.

        Returns:
            Guardian instance with updated mood
        """
        # Get streak data to calculate Guardian mood
        streaks_data = self.get_streaks()

        # Update Guardian mood based on current performance
        self.guardian.calculate_mood(streaks_data)

        return self.guardian

    def initialize_sample_data(self) -> bool:
        """Seed database with sample habits if empty.

        Returns:
            True if sample data was created, False if habits already exist
        """
        # Check if there are already habits
        if self.list_habits():
            return False  # Already has habits

        sample_habits = [
            ("Save the Princess", "Read for 15 minutes", "daily"),
            ("Slay a Dragon", "Physical activity for 30 minutes", "daily"),
            ("Plan your Quest", "Review and plan upcoming week", "weekly"),
            ("Learn Magic", "Spend time learning a new skill", "daily"),
        ]

        # Create each sample habit
        for name, task, periodicity in sample_habits:
            try:
                self.add_habit(name, task, periodicity)
            except Exception as e:
                # If any habit fails to create, log but continue
                print(f"Warning: Failed to create habit '{name}': {e}")
                continue

        return True
