"""Miners' Rescue quest for Caverns of Shadow (Act 3)."""
from ...engine.GameState import GameState
from ...engine.Quest import Quest
from ..Act3StoryFlags import (
    FLAG_ACT3_MINERS_RESCUE_STARTED,
    FLAG_ACT3_MINERS_RESCUE_COMPLETED,
)

class MinersRescue(Quest):
    """Rescue the trapped miners and secure the passage in the Caverns of Shadow."""
    def __init__(self) -> None:
        """Initialize the Miners' Rescue quest."""
        super().__init__(
            name="Miners' Rescue",
            description=(
                "Collapsed Galleries have trapped people behind tons of stone. "
                "You must find a way to free them."
            ),
            completion=(
                "You stabilized the collapse and led the miners to safety. The route to the inner "
                "caverns is now open."
            ),
        )
        self.stabilized = False
        self.rescued = False


    def check_trigger(self, game_state: GameState) -> bool:
        """Trigger when the overseer starts the rescue (flag set)."""
        return game_state.get_story_flag(FLAG_ACT3_MINERS_RESCUE_STARTED)

    def check_completion(self, game_state: GameState) -> bool:
        """Complete when collapse is stabilized and miners have been escorted."""
        # For now, check for a story flag or both items used and miners rescued
        return game_state.get_story_flag(FLAG_ACT3_MINERS_RESCUE_COMPLETED)

    def is_main(self) -> bool:
        """Return False as this is a side quest."""
        return False
