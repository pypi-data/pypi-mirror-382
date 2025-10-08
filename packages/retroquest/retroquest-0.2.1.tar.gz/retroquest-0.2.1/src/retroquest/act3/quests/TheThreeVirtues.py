"""The Three Virtues quest class."""

from ...engine.GameState import GameState
from ...engine.Quest import Quest
from ..Act3StoryFlags import (
    FLAG_ACT3_CRYSTAL_OF_LIGHT_ACQUIRED,
    FLAG_ACT3_MAIN_COMPLETED,
    FLAG_ACT3_MAIN_STARTED,
    FLAG_ACT3_DRAGONS_SCALE_ACQUIRED,
)


class TheThreeVirtuesQuest(Quest):
    """Quest to prove Courage, Wisdom, and Selflessness to unlock the final ritual."""
    def __init__(self) -> None:
        """Initialize The Three Virtues quest with description."""
        super().__init__(
            name="The Three Virtues",
            description=(
                "Prove Courage, Wisdom, and Selflessness by recovering the three relics: "
                "the Crystal of Light, the Phoenix Feather, and the Dragon's Scale."
            ),
        )
        self._flag_state = {}

    def is_main(self) -> bool:
        """Return True as this is the main quest for Act III."""
        return True

    def check_trigger(self, game_state: GameState) -> bool:
        """Check if quest should trigger when Mira starts the main plan."""
        # Trigger when Mira has started the main plan in Act III
        return game_state.get_story_flag(FLAG_ACT3_MAIN_STARTED)

    def check_update(self, game_state: GameState) -> bool:
        """Update quest description based on acquired relics."""
        updated = False
        self.description = ''
        new_desc = (
                "Prove Courage, Wisdom, and Selflessness by recovering the three relics: "
                "the Crystal of Light, the Phoenix Feather, and the Dragon's Scale."
        )
        if game_state.get_story_flag(FLAG_ACT3_CRYSTAL_OF_LIGHT_ACQUIRED):
            if not self._flag_state.get(FLAG_ACT3_CRYSTAL_OF_LIGHT_ACQUIRED):
                self._flag_state[FLAG_ACT3_CRYSTAL_OF_LIGHT_ACQUIRED] = True
                updated = True
            self.description += '[dim]' + new_desc + '[/dim]'
            new_desc = (
                "\n\nYou have claimed the Crystal of Light; its steady brilliance answers "
                "your courage and steadies what the deep waters once denied. Sir "
                "Cedric bids you to press on—dark forces gather, and he needs allies "
                "skilled in magic to stand with him when the hour comes. "
            )

        # Add block for Phoenix Feather acquisition
        from ..Act3StoryFlags import FLAG_ACT3_PHOENIX_FEATHER_ACQUIRED
        if game_state.get_story_flag(FLAG_ACT3_PHOENIX_FEATHER_ACQUIRED):
            if not self._flag_state.get(FLAG_ACT3_PHOENIX_FEATHER_ACQUIRED):
                self._flag_state[FLAG_ACT3_PHOENIX_FEATHER_ACQUIRED] = True
                updated = True
            self.description += '[dim]' + new_desc + '[/dim]'
            new_desc = (
                "\n\nYou have obtained the Phoenix Feather. Its warmth pulses in your grasp, "
                "a living ember that refuses to die. The memory of fire and flight lingers, "
                "reminding you that hope can rise from ashes. The path ahead is clearer, "
                "but the final virtue remains. "
            )

        # Add block for Dragon's Scale acquisition
        if game_state.get_story_flag(FLAG_ACT3_DRAGONS_SCALE_ACQUIRED):
            if not self._flag_state.get(FLAG_ACT3_DRAGONS_SCALE_ACQUIRED):
                self._flag_state[FLAG_ACT3_DRAGONS_SCALE_ACQUIRED] = True
                updated = True
            self.description += '[dim]' + new_desc + '[/dim]'
            new_desc = (
                "\n\nYou have claimed the Dragon's Scale, its obsidian surface gleaming "
                "with ancient power. The dragon's wisdom echoes in your mind, a testament "
                "to the selflessness you have proven. With all three relics in hand, the "
                "final trial awaits—the Warding Rite that will determine the fate of all. "
            )
        self.description += new_desc
        return updated

    def check_completion(self, game_state: GameState) -> bool:
        """Check if quest is completed when Act 3 main completion flag is set."""
        # Completes when Act 3 main completed flag set elsewhere (e.g., after Warding Rite)
        return game_state.get_story_flag(FLAG_ACT3_MAIN_COMPLETED)
