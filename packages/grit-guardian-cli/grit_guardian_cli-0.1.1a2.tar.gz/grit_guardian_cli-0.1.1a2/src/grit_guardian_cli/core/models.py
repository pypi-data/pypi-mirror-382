from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from enum import Enum


class Periodicity(Enum):
    """Enum for habit periodicity options."""

    DAILY = "daily"
    WEEKLY = "weekly"


@dataclass
class Habit:
    """Represents a habit with its properties and completion history."""

    id: Optional[int]
    name: str
    task: str
    periodicity: Periodicity
    created_at: datetime
    completions: List[datetime] = field(default_factory=list)

    def __post_init__(self):
        """Validates habit data after initialization."""
        if not self.name or not self.name.strip():
            raise ValueError(
                "Habit name cannot be empty"
            )  # Invdalid for empty or whitespace value

        if not self.task or not self.task.strip():
            raise ValueError("Habit task cannot be empty")

        # Ensure periodicity is a Periodicity enum instance
        if isinstance(self.periodicity, str):
            try:
                self.periodicity = Periodicity(self.periodicity)
            except ValueError:
                raise ValueError(
                    f"Invalid periodicity: {self.periodicity}. Must be 'daily' or 'weekly'"
                )

        # Ensure created_at is not in the future
        if self.created_at > datetime.now():
            raise ValueError("Creation date cannot be in the future")

    @classmethod
    def from_db_row(cls, row: dict) -> "Habit":
        """Creates a Habit instance from a database row dictionary."""
        return cls(
            id=row.get("id"),
            name=row["name"],
            task=row["task"],
            periodicity=Periodicity(row["periodicity"]),
            created_at=row["created_at"],
            completions=[],
        )

    def add_completion(self, completion_date: Optional[datetime] = None) -> None:
        """Adds a completion record for this habit."""
        if completion_date is None:
            completion_date = datetime.now()

        if completion_date > datetime.now():
            raise ValueError("Completion date cannot be in the future")

        self.completions.append(completion_date)
        # Keep completions sorted by date (most recent first)
        self.completions.sort(reverse=True)

    def get_streak(self) -> int:
        """Calculates current streak based on periodicity."""
        # Return 0 if no completions
        if not self.completions:
            return 0

        streak = 0
        today = datetime.now().date()

        if self.periodicity == Periodicity.DAILY:
            # For daily habits, check consecutive days
            expected_date = today
            for completion in self.completions:
                completion_date = completion.date()
                if completion_date == expected_date:
                    streak += 1
                    expected_date = (
                        expected_date.replace(day=expected_date.day - 1)
                        if expected_date.day > 1
                        else expected_date.replace(
                            month=expected_date.month - 1, day=31
                        )
                    )
                elif completion_date < expected_date:
                    break

        elif self.periodicity == Periodicity.WEEKLY:
            # For weekly habits, check consecutive weeks
            current_week = today.isocalendar()
            for completion in self.completions:
                completion_week = completion.date().isocalendar()
                if (
                    current_week[0] == completion_week[0]
                    and current_week[1] - completion_week[1] == streak
                ):
                    streak += 1

                else:
                    break

        return streak

    def is_completed_today(self) -> bool:
        """Checks if the habit has been completed today."""
        if not self.completions:
            return False

        today = datetime.now().date()
        return any(completion.date() == today for completion in self.completions)

    def is_completed_this_week(self) -> bool:
        """Checks if the habit has been completed this week."""
        if not self.completions:
            return False

        current_week = datetime.now().date().isocalendar()
        return any(
            completion.date().isocalendar()[:2] == current_week[:2]
            for completion in self.completions
        )
