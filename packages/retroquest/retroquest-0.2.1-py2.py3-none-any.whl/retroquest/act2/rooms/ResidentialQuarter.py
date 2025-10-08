"""Residential Quarter room for Act II; handles hidden library discovery."""

from ...engine.Room import Room
from ...engine.GameState import GameState
from ..characters.LocalCraftsmen import LocalCraftsmen
from ..characters.Families import Families
from ..Act2StoryFlags import (
    FLAG_ANCIENT_LIBRARY_ACCEPTED
)

class ResidentialQuarter(Room):
    """Residential Quarter room for Act II; handles hidden library discovery."""
    def __init__(self) -> None:
        super().__init__(
            name="Residential Quarter",
            description=(
                "Quiet streets lined with comfortable two-story homes, each with small gardens "
                "and neat workshops. Smoke rises from chimneys, and the sound of craftsmen at "
                "work echoes from nearby buildings. This is where Greendale's skilled artisans "
                "and middle-class citizens live and work. The atmosphere is peaceful and "
                "industrious."
            ),
            items=[],
            characters=[LocalCraftsmen(), Families()],
            exits={"south": "CastleCourtyard", "north": "HealersHouse"}
        )

    def search(self, game_state: GameState, _target: str = None) -> str:
        """Handle searching for the Hidden Library entrance.

        Parameters:
            game_state: Global state used to read/set library discovery flag.
            _target: Ignored placeholder for potential future targeted search.

        Returns:
            Narrative string describing discovery or repeat information.
        """
        if not game_state.get_story_flag(FLAG_ANCIENT_LIBRARY_ACCEPTED):
            game_state.set_story_flag(FLAG_ANCIENT_LIBRARY_ACCEPTED, True)
            # Add the secret passage exit when the library is discovered
            self.exits["secret_passage"] = "HiddenLibrary"
            # Get the Hidden Library room name for the message
            from ..rooms.HiddenLibrary import HiddenLibrary
            hidden_library = HiddenLibrary()
            return (
                f"[success]You search through the basement areas of the residential buildings. "
                f"Behind some old storage crates and forgotten furniture, you discover a "
                f"concealed entrance in the stone wall. A narrow tunnel leads underground to "
                f"what appears to "
                f"be an ancient chamber. You've found a secret passage to a "
                f"[location_name]{hidden_library.name}[/location_name]! "
                f"Use 'go secret_passage' to enter this mysterious repository.[/success]"
            )
        else:
            # Get the Hidden Library room name for the message
            from ..rooms.HiddenLibrary import HiddenLibrary
            hidden_library = HiddenLibrary()
            return (
                f"[info]You've already discovered the secret passage to the "
                f"{hidden_library.name}.[/info]"
            )
