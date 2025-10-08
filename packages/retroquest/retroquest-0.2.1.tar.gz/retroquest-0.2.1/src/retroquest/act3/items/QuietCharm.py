"""QuietCharm item for the Stillness Vestibule in Act 3."""
from ...engine.Item import Item


class QuietCharm(Item):
    """A charm that maintains peaceful silence."""

    def __init__(self) -> None:
        """Initialize QuietCharm as a collectible item."""
        super().__init__(
            name="quiet charm",
            description=(
                "A small amulet carved from pale stone, inscribed with symbols "
                "that seem to dampen sound. It feels warm to the touch and "
                "emanates a sense of tranquility."
            ),
            can_be_carried=True,
            short_name="charm",
        )
