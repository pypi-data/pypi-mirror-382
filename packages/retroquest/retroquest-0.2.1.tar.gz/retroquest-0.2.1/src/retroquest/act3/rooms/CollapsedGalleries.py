"""CollapsedGalleries room for the miners' rescue sequence in Act 3."""
from ...engine.Room import Room
from ...engine.GameState import GameState
from ..items.FallenRock import FallenRock
from ..Act3StoryFlags import FLAG_ACT3_MINERS_RESCUE_COMPLETED


class CollapsedGalleries(Room):
    """Room where miners are trapped behind a collapsed passage in Act 3."""

    def __init__(self) -> None:
        """Initialize Collapsed Galleries with rescue items, miners, and exits."""
        super().__init__(
            name="Collapsed Galleries",
            description=(
                "Ancient passages lie strangled by fallen stone, their throats choked with "
                "the weight of ages. Dust motes drift like restless spirits in the stagnant "
                "air, and shadows pool in the broken archways where starlight once danced. "
                "The walls bear scars of some long-forgotten catastrophe, and you sense the "
                "presence of those who await deliverance from this tomb of earth and shadow. "
                "A palpable tension hangs in the darkness, as if the very stones remember "
                "their violent collapse."
            ),
            items=[FallenRock()],
            characters=[],
            exits={
                "south": "StillnessVestibule",
                "east": "EchoChambers",
                "west": "ToolCache"
            },
        )

    def get_exits(self, game_state: GameState) -> dict[str, str]:
        """Hide east exit until the miners' rescue is completed."""
        exits = dict(self.exits)
        if not game_state.get_story_flag(FLAG_ACT3_MINERS_RESCUE_COMPLETED):
            exits.pop("east", None)
        return exits
