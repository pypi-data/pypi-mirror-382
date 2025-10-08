"""Village Chapel room: reflective spiritual focal point."""

from ...engine.Room import Room
from ..items.Candle import Candle
from ..items.PrayerBook import PrayerBook
from ..characters.Priest import Priest

class VillageChapel(Room):
    """Quiet devotional site foreshadowing future moral/alignment systems.

    Narrative Role:
        Provides blessing ambience and contemplative tonal anchor.

    Key Mechanics:
        Static layout; hidden locket reference seeds optional future search reward.

    Story Flags:
        None currently.

    Contents:
        - Items: ``Candle``, ``PrayerBook``.
        - NPC: ``Priest``.

    Design Notes:
        Potential resurrection / penalty mitigation hub in later acts.
    """
    def __init__(self) -> None:
        """Initialize the Village Chapel with items and a resident priest NPC."""
        super().__init__(
            name="Village Chapel",
            description=(
                "A small stone chapel stands in quiet dignity, its stained glass windows "
                "casting rainbows across the worn pews. The air is cool and still, filled "
                "with the faint scent of candle wax and old parchment. A kindly priest tends "
                "to the altar, offering blessings and words of comfort. In the shadows, a "
                "hidden locket glimmers, waiting to be discovered."
            ),
            items=[Candle(), PrayerBook()],
            characters=[Priest()],
            exits={"north": "HiddenGlade", "east": "RoadToGreendale"}
        )
