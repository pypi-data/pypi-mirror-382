"""RareFlower Item

Narrative Role:
Collectible from a secluded area (hidden glade), hinting at gentle mystical
undercurrents in Act I and potential later alchemical or ritual value.

Key Mechanics / Interactions:
- Portable (`can_be_carried=True`).
- Currently inert beyond description; may become a reagent or quest turn-in.

Story Flags (Sets / Reads):
(none) – Discovery not yet tracked globally.

Progression Effects:
- Encourages exploratory play and attention to secluded locations.

Design Notes:
- Can serve as an early barter or offering item if economy/ritual systems expand.

"""

from ...engine.Item import Item

class RareFlower(Item):
    """
    Collectible flower from a secluded area, hinting at mystical undercurrents and future value.
    """

    def __init__(self) -> None:
        """Initialize the Rare Flower item with name, description, and carry status."""
        super().__init__(
            name="rare flower",
            description="A delicate, radiant flower found only in this hidden glade. "
            + "Its petals shimmer with a faint magical glow.",
            short_name="flower",
            can_be_carried=True
        )
