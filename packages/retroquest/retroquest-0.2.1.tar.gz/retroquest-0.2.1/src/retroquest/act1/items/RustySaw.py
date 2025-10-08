"""RustySaw item: an old rusty saw for cutting soft materials."""

from ...engine.Item import Item


class RustySaw(Item):
    """Old, rusty saw with a worn wooden handle, useful for cutting soft materials."""

    def __init__(self) -> None:
        """Initialize the Rusty Saw item with name, description, and carry status."""
        super().__init__(
            name="rusty saw",
            description=(
                "An old, rusty saw with a worn wooden handle. It looks like it could still cut "
                "through something soft, but might break on anything tough."
            ),
            short_name="saw",
            can_be_carried=True
        )
