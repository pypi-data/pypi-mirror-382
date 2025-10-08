"""Forest Path room: dynamic description corridor with removable vine obstacle."""

from ...engine.Room import Room
from ..items.Vines import Vines
from ..items.Bush import Bush  # Import Bush
from ...engine.GameState import GameState

class ForestPath(Room):
    """Wilderness traversal space demonstrating environment-as-item state.

    Narrative Role:
        Introduces light environmental obstruction pattern (vines) and adaptive text.

    Key Mechanics:
        - ``get_description()`` checks for ``Vines`` presence to choose wording.
        - Items double as state toggles (no flag required yet).

    Story Flags:
        None (state embodied by item presence).

    Contents:
        - Items: ``Vines`` (removable), ``Bush`` (flavor / future forage).
        - Characters: None.

    Design Notes:
        Could later externalize transformation into a reusable description state mixin.
    """
    def __init__(self) -> None:
        """Initialize the Forest Path room with its items and exits."""
        super().__init__(
            name="Forest Path",
            description=(
                "A winding path snakes into the heart of the woods, dappled sunlight "
                "flickering through the canopy above. A section of the path is blocked by "
                "thick, thorny vines. The air is alive with the scent of pine and wildflowers, "
                "and the ground is soft with moss and fallen leaves. Birds flit between "
                "branches, and the occasional snap of a twig hints at unseen creatures "
                "nearby. The path feels ancient, as if it remembers every footstep that has "
                "ever passed this way."
            ),
            items=[Vines(), Bush()],  # Add Bush to items
            characters=[],
            # HG is South.
            exits={"north": "Riverbank", "south": "HiddenGlade"}
        )

    # reserved for future conditional text
    def get_description(self, _game_state: GameState) -> str:
        """Return an adaptive description depending on whether vines remain present."""
        # Check if vines are still present (i.e., not cut)
        if any(isinstance(item, Vines) for item in self.items):
            return self.description  # Original description with vines
        else:
            # Return a description indicating the vines are cut and the alcove is accessible
            return (
                "A winding path snakes into the heart of the woods, dappled sunlight "
                "flickering through the canopy above. Where thick vines once blocked a "
                "small alcove, they now lie cut, revealing the opening. The air is alive "
                "with the scent of pine and wildflowers, and the ground is soft with "
                "moss and fallen leaves. Birds flit between branches, and the occasional "
                "snap of a twig hints at unseen creatures nearby. The path feels ancient, "
                "as if it remembers every footstep that has ever passed this way."
            )
