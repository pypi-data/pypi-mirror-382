"""Riverbank room: tranquil edge location introducing fishing ambience."""

from ...engine.Room import Room
from ..items.SmoothStone import SmoothStone
from ..items.River import River  # Import River
from ..characters.Fisherman import Fisherman

class Riverbank(Room):
    """Serene natural boundary space foreshadowing fishing gameplay loops.

    Narrative Role:
        Establishes contemplative pacing and resource gathering potential.

    Key Mechanics:
        Static now; ``Fisherman`` NPC forms future tutorial or quest hub.

    Story Flags:
        None currently.

    Contents:
        - Items: ``SmoothStone``, ``River``.
        - NPC: ``Fisherman``.

    Design Notes:
        Time-of-day or seasonal variants could later deepen atmosphere.
    """
    def __init__(self) -> None:
        super().__init__(
            name="Riverbank",
            description=(
                "A gentle river flows past the village. Reeds sway along the banks, and "
                "the air is alive with the hum of insects. A weathered fisherman sits "
                "nearby, humming a quiet tune. The riverbank is peaceful, a place where "
                "time seems to slow and worries drift away."
            ),
            items=[SmoothStone(), River()],
            characters=[Fisherman()],
            exits={"west": "OldMill", "south": "ForestPath"}
        )
