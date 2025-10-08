from enum import Enum
from typing import List, Dict


class GuardianMood(Enum):
    """Enum representing different mood states of the Guardian."""

    ECSTATIC = "ecstatic"
    HAPPY = "happy"
    CONTENT = "content"
    SAD = "sad"
    WORRIED = "worried"


class Guardian:
    """Represents the Guardian that reflects user's habit performance."""

    def __init__(self, name: str = "Guardian", species: str = "Dragon"):
        """Initializes a new Guardian.

        Args:
            name: The Guardian's name (default: "Guardian")
            species: The Guardian's species (default: "Dragon")
        """
        self.name = name
        self.species = species
        self.current_mood = GuardianMood.CONTENT

    def calculate_mood(self, habits_data: List[Dict]) -> GuardianMood:
        """Calculates mood based on habit completion data.

        Args:
            habits_data: List of dictionaries containing habit analytics
                        Each dict should have 'completion_rate' and 'current_streak' keys

        Returns:
            GuardianMood enum value representing the calculated mood
        """
        if not habits_data:
            self.current_mood = GuardianMood.WORRIED
            return GuardianMood.WORRIED

        # Calculate average completion rate and streak status
        avg_completion = sum(h["completion_rate"] for h in habits_data) / len(
            habits_data
        )
        active_streaks = sum(1 for h in habits_data if h["current_streak"] > 0)
        streak_percentage = active_streaks / len(habits_data) if habits_data else 0

        # Update current mood based on performance
        if avg_completion >= 90 and streak_percentage == 1.0:
            self.current_mood = GuardianMood.ECSTATIC
        elif avg_completion >= 70:
            self.current_mood = GuardianMood.HAPPY
        elif avg_completion >= 50:
            self.current_mood = GuardianMood.CONTENT
        elif avg_completion >= 30:
            self.current_mood = GuardianMood.SAD
        else:
            self.current_mood = GuardianMood.WORRIED

        return self.current_mood

    # The following "artworks" are AI-generated for now
    # and will be updated in the future
    def get_ascii_art(self) -> str:
        """Returns ASCII art based on current mood.

        Returns:
            String containing ASCII art representation of the Guardian
        """
        art = {
            GuardianMood.ECSTATIC: r"""
    /\   /\
   (  O O  )
  <  \___/  >
   \   ^   /""",
            GuardianMood.HAPPY: r"""
    /\   /\
   (  ^.^  )
  <  \___/  >
   \  ~~~  /""",
            GuardianMood.CONTENT: r"""
    /\   /\
   (  -.-  )
  <  \___/  >
   \  ---  /""",
            GuardianMood.SAD: r"""
    /\   /\
   (  -..-  )
  <  \___/  >
   \  vvv  /""",
            GuardianMood.WORRIED: r"""
    /\   /\
   (  o.o  )
  <  \___/  >
   \  ~~~  /""",
        }

        return art.get(self.current_mood, art[GuardianMood.CONTENT])

    def get_mood_message(self) -> str:
        """Gets a message based on the Guardian's current mood.

        Returns:
            String with a mood-appropriate message
        """
        messages = {
            GuardianMood.ECSTATIC: f"{self.name} is absolutely thrilled with your consistency!",
            GuardianMood.HAPPY: f"{self.name} is happy to see your progress!",
            GuardianMood.CONTENT: f"{self.name} is content with your efforts.",
            GuardianMood.SAD: f"{self.name} looks a bit sad. Some habits need attention.",
            GuardianMood.WORRIED: f"{self.name} is worried about your habits. Time to get back on track!",
        }

        return messages.get(
            self.current_mood, f"{self.name} is feeling {self.current_mood.value}."
        )

    def __str__(self) -> str:
        """String representation of the Guardian."""
        return f"{self.species} named {self.name} (Mood: {self.current_mood.value})"
