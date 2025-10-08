"""Millstone fragment item: heavy chunk from the old mill's grinding wheel."""
from ...engine.Item import Item

class MillstoneFragment(Item):
    """Chunk of stone broken from the old mill's grinding wheel."""

    def __init__(self) -> None:
        """Initialize the Millstone Fragment item with name, description, and carry status."""
        super().__init__(
            name="millstone fragment",
            description=(
                "A chunk of stone broken from the old mill's grinding wheel. It's heavy "
                "and rough, but could be useful for repairs or as a tool."
            ),
            short_name="fragment",
            can_be_carried=True
        )
