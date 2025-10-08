"""Village Well room: mystical utility hub foreshadowing purification systems."""

from ...engine.Room import Room
from ..items.Well import Well

class VillageWell(Room):
    """Central atmospheric structure hinting at latent magical interactions.

    Narrative Role:
        Provides quiet mystical anchor and geometric convergence for paths.

    Key Mechanics:
        Static now; ``Well`` item reserved for future verbs (draw, purify, scry).

    Story Flags:
        None currently.

    Contents:
        - Item: ``Well``.
        - Characters: None.

    Design Notes:
        Potential site for divination, wishes, or spirit encounters.
    """
    def __init__(self) -> None:
        """Initialize the Village Well and its quiet, mystical presence."""
        super().__init__(
            name="Village Well",
            description=(
                "An old stone well stands at the village's center, its stones worn smooth "
                "by countless hands. The water below glimmers with a crystalline clarity, "
                "and the air is cool and damp. Moss creeps up the sides, and a frayed rope "
                "hangs nearby. The well seems to whisper secrets to those who listen closely."
            ),
            items=[Well()],
            characters=[],
            exits={"west": "VegetableField", "east": "BlacksmithsForge", "south": "AbandonedShed"}
        )
