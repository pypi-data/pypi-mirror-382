
"""Valuable silver ring with gemstone, reward for solving the well puzzle."""
from ...engine.Item import Item

class ShinyRing(Item):
    """
    Valuable silver ring with gemstone, reward for solving the well puzzle.
    """

    def __init__(self) -> None:
        """Initialize the Shiny Ring item with name, description, and carry status."""
        super().__init__(
            name="shiny ring",
            short_name="ring",
            description=(
                "A beautiful silver ring with a small, sparkling gemstone. "
                "It looks quite valuable."
            ),
            can_be_carried=True
        )
