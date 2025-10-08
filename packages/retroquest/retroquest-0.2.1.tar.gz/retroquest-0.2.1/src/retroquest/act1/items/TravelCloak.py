
"""Heavy, hooded cloak made for travel, offering warmth and protection from the elements."""
from ...engine.Item import Item

class TravelCloak(Item):
    """
    Heavy, hooded cloak made for travel, offering warmth and protection from the elements.
    """

    def __init__(self) -> None:
        """Initialize the Travel Cloak item with name, description, and carry status."""
        super().__init__(
            name="travel cloak",
            description=(
                "A heavy, hooded cloak made for travel. It offers warmth and protection from "
                "the elements."
            ),
            short_name="cloak",
            can_be_carried=True
        )
