"""Sir Cedric character for Act 3."""

from ...engine.Character import Character
from ...engine.GameState import GameState
from ..Act3StoryFlags import (
    FLAG_ACT3_MAIN_STARTED,
    FLAG_ACT3_CRYSTAL_OF_LIGHT_ACQUIRED,
    FLAG_ACT3_VOW_OF_COURAGE_MADE,
)


class SirCedric(Character):
    """A steadfast knight who aids the player in their quest against Malakar."""

    def __init__(self) -> None:
        """Initialize Sir Cedric with description."""
        super().__init__(
            name="sir cedric",
            description=(
                "Armor tempered, eyes steady—Cedric stands ready for the trials. "
                "His presence is a quiet promise."
            ),
        )

    def talk_to(self, game_state: GameState) -> str:
        """Return appropriate dialogue based on quest progress and location.

        The response varies depending on whether the main quest has started,
        which site the party currently occupies, and whether key flags like
        the Crystal acquisition and the Vow of Courage have been set.
        """
        # If the main quest hasn't started, direct the player to Mira.
        if not game_state.get_story_flag(FLAG_ACT3_MAIN_STARTED):
            return (
                "[character_name]Sir Cedric[/character_name]: If we're to take the "
                "fight to Malakar, speak with [character_name]Mira[/character_name]. "
                "She understands the rites and the way to begin."
            )

        # Main quest active: tailor replies to location and state.
        room_name = game_state.current_room.name

        # Tidal Causeway: advice about the Crystal and the vow
        if room_name == "Tidal Causeway":
            if not game_state.get_story_flag(
                FLAG_ACT3_CRYSTAL_OF_LIGHT_ACQUIRED
            ):
                return (
                    "[character_name]Sir Cedric[/character_name]: The tide tests "
                    "the brave. Stand strong with Mira—speak your vow before the "
                    "guardian and let courage steady your hand."
                )
            if not game_state.get_story_flag(FLAG_ACT3_VOW_OF_COURAGE_MADE):
                return (
                    "[character_name]Sir Cedric[/character_name]: The Crystal is "
                    "ours. When you are ready, make your vow to bind its power; "
                    "I will stand with you."
                )
            return (
                "[character_name]Sir Cedric[/character_name]: Your vow has been "
                "spoken. Let us press onward—Mira will open the circle when you "
                "are prepared."
            )

        # Default reply when the main quest is active
        return (
            "[character_name]Sir Cedric[/character_name]: The path is set. "
            "Courage, Wisdom, Selflessness—name them with your deeds, and we "
            "will see this through."
        )
