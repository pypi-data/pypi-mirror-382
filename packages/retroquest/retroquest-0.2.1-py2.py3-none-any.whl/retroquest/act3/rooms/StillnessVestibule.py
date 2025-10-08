"""Stillness Vestibule room for Act 3."""

from ...engine.Room import Room
from ...engine.GameState import GameState
from ..items.EchoStones import EchoStones
from ..items.StillwaterPhial import StillwaterPhial
from ..items.QuietCharm import QuietCharm
from ..characters.SilenceKeeper import SilenceKeeper
from ..characters.WanderingPhantoms import WanderingPhantoms
from ..Act3StoryFlags import FLAG_ACT3_OATH_OF_STILLNESS_COMPLETED


class StillnessVestibule(Room):
    """A quiet chamber where hush falls over dark water pools."""

    def __init__(self) -> None:
        """Initialize Stillness Vestibule with description and exits."""
        super().__init__(
            name="Stillness Vestibule",
            description=(
                "A profound hush descends like a shroud over obsidian water pools that "
                "mirror the darkness above, their surfaces so still they seem frozen in "
                "time. Sound itself appears to be devoured by the ancient stone, as if "
                "the very walls hunger for silence. Three echo stones stand sentinel in "
                "a perfect triangle at the chamber's heart, their surfaces carved with "
                "mystical channels that seem to writhe in the dim light. These weathered "
                "monoliths pulse with an otherworldly energy, their carved conduits "
                "waiting to amplify sacred whispers and bind them to the fabric of "
                "reality itself. The air thrums with dormant power, heavy with the "
                "weight of forgotten rituals."
            ),
            items=[
                EchoStones(),
                StillwaterPhial(),
                QuietCharm()
            ],
            characters=[SilenceKeeper(), WanderingPhantoms()],
            exits={
                "north": "CollapsedGalleries",
                "west": "CavernMouth"
            },
        )

    def get_exits(self, game_state: GameState) -> dict[str, str]:
        """Return exits, opening path to Dragon's Hall after Oath completion."""
        exits = self.exits.copy()
        # Only allow east to Dragon's Hall after Oath of Stillness is completed
        if game_state.get_story_flag(FLAG_ACT3_OATH_OF_STILLNESS_COMPLETED):
            exits["east"] = "DragonsHall"
        return exits
