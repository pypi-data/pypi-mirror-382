"""Fortress Gates item for Act 3."""

from ...engine.Item import Item
from ...engine.GameState import GameState
from ..Act3StoryFlags import FLAG_ACT3_FORTRESS_GATES_EXAMINED


class FortressGates(Item):
    """The massive gates of Malakar's fortress, bound with eldritch wards."""

    def __init__(self) -> None:
        """Initialize the fortress gates."""
        super().__init__(
            name="fortress gates",
            short_name="gates",
            description=(
                "Massive blackened iron gates tower above, carved with sigils that "
                "writhe and pulse with dark energy. Beyond the lattice, malevolent "
                "corridors stretch into shadow."
            ),
            can_be_carried=False
        )

    def examine(self, game_state: GameState) -> str:
        """Handle examining the fortress gates."""
        if not game_state.get_story_flag(FLAG_ACT3_FORTRESS_GATES_EXAMINED):
            game_state.set_story_flag(FLAG_ACT3_FORTRESS_GATES_EXAMINED, True)
            return (
                "[event]You examine the massive gates that tower above you.[/event] "
                "Their blackened iron is carved with sigils that seem to writhe in "
                "the corner of your vision. Beyond the lattice, you glimpse corridors "
                "that pulse with malevolent energy. This is the threshold of Malakar's "
                "domain—where King Alden is held captive and the kingdom's fate will "
                "be decided. The three relics in your possession pulse with protective "
                "power, ready to shield you from the sorcerer's influence. "
                "[bold]Act III is complete.[/bold] The final confrontation awaits."
            )
        else:
            return (
                "[event]You examine the fortress gates.[/event] The gates stand "
                "ready to be breached. The weight of destiny presses down as you "
                "prepare for the final assault."
            )
