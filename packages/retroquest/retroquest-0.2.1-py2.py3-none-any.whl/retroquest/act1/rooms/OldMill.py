"""Old Mill room: weathered structure with latent mechanical mystery."""

from ...engine.Room import Room
from ..items.SackOfFlour import SackOfFlour
from ..items.Mechanism import Mechanism

class OldMill(Room):
    """Aging industrial landmark hinting at future mechanical puzzle systems.

    Narrative Role:
        Provides tonal contrast (technology vs. rustic agriculture) and seeds the
        ``Mechanism`` object as a future interaction anchor.

    Key Mechanics:
        Static currently; ``Mechanism`` signals deferred puzzle or activation chain.

    Story Flags:
        None yet.

    Contents:
        - Items: ``SackOfFlour``, ``Mechanism``.
        - Characters: None.

    Design Notes:
        Could expand into crafting throughput, speed buffs, or timing-based events.
    """
    def __init__(self) -> None:
        """Initialize the Old Mill room and its static contents."""
        super().__init__(
            name="Old Mill",
            description=(
                "A creaky windmill towers above, its sails turning slowly in the breeze. Dusty "
                "gears and cobwebs fill the interior, and the scent of flour hangs in the air. "
                "Sunlight streams through broken windows, illuminating sacks of grain and a "
                "heavy millstone. Amidst the old workings, you notice a strange mechanism "
                "with levers and gears that doesn't quite seem to belong to the mill's "
                "original design."
            ),
            items=[SackOfFlour(), Mechanism()],
            characters=[],
            exits={"north": "AbandonedShed", "east": "Riverbank"}
        )
