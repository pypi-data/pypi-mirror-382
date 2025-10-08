"""A small, decorative shell found in the Sunken Ruins; carriable but unused."""
from ...engine.Item import Item


class PolishedShell(Item):
    """A smooth shell polished by tides; can be picked up but has no special use."""

    def __init__(self) -> None:
        """Initialize a Polished Shell item."""
        super().__init__(
            name="Polished Shell",
            description=(
                "A small, iridescent shell smoothed by long tides. It's pretty and "
                "shines in the moonlight."
            ),
            short_name="shell",
            can_be_carried=True,
        )
