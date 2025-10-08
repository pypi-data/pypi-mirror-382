
"""Dull kitchen knife item, could be sharpened for future use."""

from ...engine.Item import Item

class DullKnife(Item):
    """
    Dull kitchen knife item, could be sharpened for future use.
    """

    def __init__(self) -> None:
        """Initialize the Dull Knife item with name, description, and carry status."""
        super().__init__(
            name="dull knife",
            description="A small kitchen knife with a dull blade."
            + " It won't cut much, but could be sharpened.",
            short_name="knife",
            can_be_carried=True
        )
