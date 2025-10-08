"""Fortress Entrance room for Act 3."""

from ...engine.Room import Room
from ..items.FortressGates import FortressGates


class FortressEntrance(Room):
    """A blackstone bastion rising from a shattered ridge with gate sigils."""
    def __init__(self) -> None:
        """Initialize Fortress Entrance with description and exits."""
        super().__init__(
            name="Entrance to Malakar's Fortress",
            description=(
                "A blackstone bastion rises from a shattered ridge; gate sigils pulse "
                "like a heartbeat behind iron lattices. The air tastes of cold metal and "
                "distant thunder. The massive gates loom ahead, wreathed in shadow and "
                "bound with eldritch wards."
            ),
            items=[FortressGates()],
            characters=[],
            exits={},
        )
