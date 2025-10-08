"""Miners character for the Collapsed Galleries rescue sequence."""
from ...engine.Character import Character
from ...engine.GameState import GameState
from ..Act3StoryFlags import FLAG_ACT3_MINERS_RESCUE_COMPLETED


class Miners(Character):
    """Trapped miners awaiting rescue in the collapsed galleries."""

    def __init__(self) -> None:
        """Initialize the Miners character."""
        super().__init__(
            name="miners",
            description=(
                "A group of miners trapped behind the fallen rock, their voices "
                "echoing faintly through the debris."
            )
        )

    def talk_to(self, game_state: GameState) -> str:
        """Handle talking to the miners for rescue completion."""
        # Since miners are only added to the room after passage is freed,
        # they can be rescued immediately when talked to
        if not game_state.get_story_flag(FLAG_ACT3_MINERS_RESCUE_COMPLETED):
            game_state.set_story_flag(FLAG_ACT3_MINERS_RESCUE_COMPLETED, True)
            return (
                "The lead miner steps forward, dust-covered but relieved: "
                "[dialogue]'Thank the gods you found us. When that section collapsed this "
                "morning, we thought we were done for. The whole ceiling came down like "
                "thunder—trapped us behind tons of rock with barely any air.'[/dialogue]\n\n"
                "Another miner adds, voice shaking: [dialogue]'We could hear you working "
                "on the other side, but we didn't dare hope. Those braces you placed "
                "saved our lives—without them, the whole tunnel would've come down on "
                "our heads.'[/dialogue]\n\n"
                "The lead miner nods gratefully: [dialogue]'We can't thank you enough, "
                "Elior. Now that the immediate danger's passed, we'll get to work "
                "reinforcing this whole section. These old caverns need proper support "
                "beams before anyone else ventures through. The route to the Echo "
                "Chambers is open, but we'll make sure it stays that way.'[/dialogue]\n\n"
                "[event]The miners begin setting up additional supports as you prepare "
                "to continue your journey.[/event]"
            )
        return (
            "The miners look up from their work, tools in hand: [dialogue]'Still "
            "here, Elior? We're making good progress on these support beams. "
            "The passage to the Echo Chambers is secure now—you can head east "
            "whenever you're ready. We'll keep working to make sure these old "
            "caverns are safe for future travelers.'[/dialogue]"
        )
