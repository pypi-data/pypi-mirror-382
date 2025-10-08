"""Feather item used for flavor and potential crafting in Act1."""

from ...engine.Item import Item

class Feather(Item):
    """Lightweight byproduct item used for flavor and simple crafting."""

    def __init__(self) -> None:
        """Initialize the Feather item with name, description, and carry status."""
        super().__init__(
            name="feather",
            description=(
                "A soft white feather, likely from one of the chickens. It could be used for "
                "writing, crafting, or tickling."
            ),
            can_be_carried=True
        )
