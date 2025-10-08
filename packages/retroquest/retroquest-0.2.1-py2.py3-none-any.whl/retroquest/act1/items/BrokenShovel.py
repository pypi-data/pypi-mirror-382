"""Broken shovel item: flavor tool hinting at future repair or crafting systems."""

from ...engine.Item import Item


class BrokenShovel(Item):
    """
    Derelict digging tool hinting at future repair or crafting systems.
    """

    def __init__(self) -> None:
        """Initialize the Broken Shovel item with name, description, and carry status."""
        super().__init__(
            name="broken shovel",
            description=(
                "A rusty, splintered shovel with a cracked wooden handle. It looks like it "
                "hasn't been used in years, but might still be useful for digging in soft "
                "earth."
            ),
            short_name="shovel",
            can_be_carried=True,
        )
