"""StillwaterPhial item for the Stillness Vestibule in Act 3."""
from ...engine.Item import Item


class StillwaterPhial(Item):
    """A vial of eerily still water from the vestibule pools."""

    def __init__(self) -> None:
        """Initialize StillwaterPhial as a collectible item."""
        super().__init__(
            name="stillwater phial",
            description=(
                "A crystal vial containing water so still it seems solid. The "
                "liquid captures and holds reflections that shouldn't be there."
            ),
            can_be_carried=True,
            short_name="phial",
        )
