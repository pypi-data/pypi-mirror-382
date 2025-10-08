"""Plump river fish item used as food or a gift in Act1."""
from ...engine.Item import Item

class Fish(Item):
    """A plump river fish item that can be carried."""

    def __init__(self) -> None:
        """Initialize the Fish item with name, description, and carry status."""
        super().__init__(
            name="fish",
            description="A plump river fish. It looks fresh and would make a good"
            + " meal or perhaps a gift.",
            can_be_carried=True
        )
