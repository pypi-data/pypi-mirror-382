from datetime import datetime, timedelta, date
from typing import TYPE_CHECKING, List, Dict, Any

# Avoid circular imports
# https://docs.python.org/3/library/typing.html#typing.TYPE_CHECKING
if TYPE_CHECKING:
    from grit_guardian_cli.core.models import Habit


def calculate_streak(completions: List[datetime], periodicity: str) -> int:
    """Calculates current streak for a habit.

    Args:
        completions: List of completion datetime objects
        periodicity: Either 'daily' or 'weekly'

    Returns:
        Current streak count
    """
    if not completions:
        return 0

    sorted_completions = sorted(completions, reverse=True)
    streak = 0

    if periodicity == "daily":
        expected_date = datetime.now().date()
        for completion in sorted_completions:
            if completion.date() == expected_date:
                streak += 1
                expected_date -= timedelta(days=1)
            elif completion.date() < expected_date:
                break

    elif periodicity == "weekly":
        current_week = datetime.now().date().isocalendar()
        current_year, current_week_num = current_week[0], current_week[1]

        for completion in sorted_completions:
            completion_week = completion.date().isocalendar()
            completion_year, completion_week_num = (
                completion_week[0],
                completion_week[1],
            )

            # Check if completion is in the expected week
            expected_week_num = current_week_num - streak
            expected_year = current_year

            # Handle year boundary
            if expected_week_num <= 0:
                expected_year -= 1
                # Get number of weeks in previous year
                last_day_of_year = date(expected_year, 12, 31)
                expected_week_num = (
                    last_day_of_year.isocalendar()[1] + expected_week_num
                )

            if (
                completion_year == expected_year
                and completion_week_num == expected_week_num
            ):
                streak += 1
            elif completion_year < expected_year or (
                completion_year == expected_year
                and completion_week_num < expected_week_num
            ):
                break

    return streak


def calculate_longest_streak(completions: List[datetime], periodicity: str) -> int:
    """Finds the longest streak ever achieved.

    Uses a functional approach to calculate streaks.

    Args:
        completions: List of completion datetime objects
        periodicity: Either 'daily' or 'weekly'

    Returns:
        Longest streak count
    """
    if not completions:
        return 0

    sorted_completions = sorted(completions)

    if periodicity == "daily":
        # Group completions by date
        dates = [c.date() for c in sorted_completions]
        unique_dates = sorted(set(dates))

        if not unique_dates:
            return 0

        # Use functional approach to find consecutive date groups
        def date_difference(d1: date, d2: date) -> int:
            return (d2 - d1).days

        # Create groups of consecutive dates
        streaks = []
        current_streak = [unique_dates[0]]

        for i in range(1, len(unique_dates)):
            if date_difference(unique_dates[i - 1], unique_dates[i]) == 1:
                current_streak.append(unique_dates[i])
            else:
                streaks.append(len(current_streak))
                current_streak = [unique_dates[i]]

        streaks.append(len(current_streak))
        return max(streaks) if streaks else 0

    elif periodicity == "weekly":
        # Group completions by week
        weeks = [
            (c.date().isocalendar()[0], c.date().isocalendar()[1])
            for c in sorted_completions
        ]
        unique_weeks = sorted(set(weeks))

        if not unique_weeks:
            return 0

        # Find consecutive week groups
        streaks = []
        current_streak = 1

        for i in range(1, len(unique_weeks)):
            prev_year, prev_week = unique_weeks[i - 1]
            curr_year, curr_week = unique_weeks[i]

            # Check if weeks are consecutive
            if curr_year == prev_year and curr_week == prev_week + 1:
                current_streak += 1
            elif curr_year == prev_year + 1 and prev_week >= 52 and curr_week == 1:
                # Handle year boundary
                current_streak += 1
            else:
                streaks.append(current_streak)
                current_streak = 1

        streaks.append(current_streak)
        return max(streaks) if streaks else 0

    return 0


def get_completion_rate(
    habit_created: datetime, completions: List[datetime], periodicity: str
) -> float:
    """Calculates percentage of successful completions.

    Args:
        habit_created: When the habit was created
        completions: List of completion datetime objects
        periodicity: Either 'daily' or 'weekly'

    Returns:
        Completion rate as a percentage (0.0 to 100.0)
    """
    if habit_created > datetime.now():
        return 0.0

    # Calculate expected completions
    days_since_creation = (datetime.now() - habit_created).days + 1

    if periodicity == "daily":
        expected_completions = days_since_creation
        # Count unique completion dates
        unique_completion_dates = len(set(c.date() for c in completions))
        actual_completions = unique_completion_dates

    elif periodicity == "weekly":
        # Calculate weeks since creation
        weeks_since_creation = days_since_creation // 7
        if days_since_creation % 7 > 0:
            weeks_since_creation += 1

        expected_completions = weeks_since_creation
        # Count unique completion weeks
        unique_weeks = set(
            (c.date().isocalendar()[0], c.date().isocalendar()[1]) for c in completions
        )
        actual_completions = len(unique_weeks)

    else:
        return 0.0

    if expected_completions == 0:
        return 0.0

    rate = (actual_completions / expected_completions) * 100.0
    # Cap at 100% (in case of multiple completions per period)
    return min(rate, 100.0)


def get_habit_analytics(
    habit_name: str, created_at: datetime, completions: List[datetime], periodicity: str
) -> Dict[str, Any]:
    """Gets analytics for a single habit.

    Args:
        habit_name: Name of the habit
        created_at: When the habit was created
        completions: List of completion datetime objects
        periodicity: Either 'daily' or 'weekly'

    Returns:
        Dictionary containing all analytics metrics
    """
    return {
        "name": habit_name,
        "current_streak": calculate_streak(completions, periodicity),
        "longest_streak": calculate_longest_streak(completions, periodicity),
        "completion_rate": get_completion_rate(created_at, completions, periodicity),
        "total_completions": len(completions),
        "days_since_creation": (datetime.now() - created_at).days,
    }


def generate_weekly_view(habits: List["Habit"]) -> str:
    """Generates ASCII table for weekly progress.

    Args:
        habits: List of Habit objects to display

    Returns:
        String containing formatted ASCII table
    """
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())

    # Build header
    header = "Habit".ljust(20) + " | "
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    header += " | ".join(days)

    separator = "-" * len(header)

    rows = [header, separator]

    for habit in habits:
        row = habit.name[:20].ljust(20) + " | "

        for day_offset in range(7):
            check_date = week_start + timedelta(days=day_offset)

            if check_date > today:
                row += " - "
            elif any(c.date() == check_date for c in habit.completions):
                row += " ✓ "
            else:
                row += " ✗ "

            if day_offset < 6:
                row += " | "

        rows.append(row)

    return "\n".join(rows)


def calculate_expected_completions(habit: "Habit", since_date: datetime) -> int:
    """Calculates expected number of completions for a habit since a given date.

    Args:
        habit: Habit object
        since_date: Date to calculate from

    Returns:
        Expected number of completions
    """
    # Make sure we're comparing datetime objects
    if isinstance(since_date, date) and not isinstance(since_date, datetime):
        since_date = datetime.combine(since_date, datetime.min.time())

    # Use the later of habit creation or since_date
    start_date = max(habit.created_at, since_date)
    days_elapsed = (datetime.now() - start_date).days + 1

    if habit.periodicity.value == "daily":
        return days_elapsed
    elif habit.periodicity.value == "weekly":
        # Calculate weeks, including partial weeks
        weeks = days_elapsed // 7
        if days_elapsed % 7 > 0:
            weeks += 1
        return weeks

    return 0


def identify_struggled_habits(habits: List["Habit"], days: int = 30) -> List[Dict]:
    """Finds habits with low completion rates in given period.

    Args:
        habits: List of Habit objects to analyze
        days: Number of days to look back (default: 30)

    Returns:
        List of dictionaries with struggling habit information
    """
    cutoff_date = datetime.now() - timedelta(days=days)

    struggled = []
    for habit in habits:
        # Filter completions to the time period
        recent_completions = [c for c in habit.completions if c >= cutoff_date]
        expected = calculate_expected_completions(habit, cutoff_date)

        if expected > 0:
            rate = len(recent_completions) / expected
            if rate < 0.5:  # Less than 50% completion
                struggled.append(
                    {
                        "name": habit.name,
                        "completion_rate": rate,
                        "missed": expected - len(recent_completions),
                    }
                )

    return sorted(struggled, key=lambda x: x["completion_rate"])
