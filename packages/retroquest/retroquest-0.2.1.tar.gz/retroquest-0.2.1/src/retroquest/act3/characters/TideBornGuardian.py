"""TideBornGuardian character for Act 3."""
from ...engine.Character import Character
from ...engine.GameState import GameState
from ..Act3StoryFlags import (
    FLAG_ACT3_VOW_OF_COURAGE_MADE,
)

class TideBornGuardian(Character):
    """The Tide-Born Guardian: a figure of gathered waters and ward-sigils."""

    def __init__(self) -> None:
        """Initialize Tide-Born Guardian with description."""
        super().__init__(
            name="Tide-Born Guardian",
            description=(
                "A figure of gathered waters and ward-sigils, its form rippling "
                "with the tide's breath."
            ),
        )

    def talk_to(self, _game_state: GameState) -> str:
        """Return dialogue asking for vow when talking to the guardian."""
        return (
            "[dialogue]The guardian's voice is the hush of a turning tide: 'Name "
            "what you will not abandon.'[/dialogue]"
        )

    def say_to(self, words: str, game_state: GameState) -> str:
        """Handle the vow of courage when saying specific words to the guardian."""
        w = words.strip().lower()
        if w == "myself":
            game_state.set_story_flag(FLAG_ACT3_VOW_OF_COURAGE_MADE, True)
            return (
                "[success]The waters draw back as if breathing in. Your vow anchors "
                "the chamber's heart, and the relic heeds your courage. You may now "
                "take the [item_name]Crystal of Light[/item_name].[/success]"
            )
        return (
            "[dialogue]The tide listens, then falls quiet. That is not the vow the "
            "guardian will bind to.[/dialogue]"
        )
