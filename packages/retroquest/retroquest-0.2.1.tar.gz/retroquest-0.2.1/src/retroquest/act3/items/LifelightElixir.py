"""Lifelight Elixir created from the three relics in Act 3."""

from ...engine.Item import Item


class LifelightElixir(Item):
    """A powerful elixir created from the three virtues that can save King Alden."""

    def __init__(self) -> None:
        """Initialize the Lifelight Elixir."""
        super().__init__(
            name="Lifelight Elixir",
            description=(
                "A shimmering elixir that seems to contain liquid starlight. "
                "Threads of crystal clarity, phoenix flame, and draconic essence "
                "swirl within the glass vial. This potion pulses with the combined "
                "power of courage, wisdom, and selflessness—the three virtues "
                "needed to counter Malakar's dark ritual and save King Alden's life."
            ),
            can_be_carried=True,
            short_name="elixir"
        )
