"""Village Square room: central social/navigation hub with light utility items."""

from ...engine.Room import Room
from ..items.Bucket import Bucket
from ..items.OldNotice import OldNotice
from ..characters.Villager import Villager

class VillageSquare(Room):
    """Primary hub space supporting orientation and ambient world flavor.

    Narrative Role:
        Serves as stable return point and social backdrop establishing village life.

    Key Mechanics:
        Static, ungated; encourages free exploration without early friction.

    Story Flags:
        None.

    Contents:
        - Items: ``Bucket``, ``OldNotice``.
        - NPC: ``Villager``.

    Design Notes:
        Candidate for timed announcements or seasonal event layering later.
    """
    def __init__(self) -> None:
        """Initialize the Village Square with its ambient items and villagers."""
        super().__init__(
            name="Village Square",
            description=(
                "The heart of Willowbrook bustles with life. Cobblestone paths radiate from a "
                "mossy old well, and a weathered notice board stands nearby, covered in faded "
                "announcements. Children chase each other around market stalls, and the air is "
                "filled with laughter, gossip, and the scent of fresh bread. The square is a "
                "crossroads for villagers, travelers, and secrets alike."
            ),
            items=[Bucket(), OldNotice()],
            characters=[Villager()],
            exits={"west": "EliorsCottage", "north": "MirasHut", "east": "GeneralStore"}
        )
