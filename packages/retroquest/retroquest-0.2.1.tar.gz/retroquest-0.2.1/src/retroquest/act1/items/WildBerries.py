"""WildBerries: foraged berries used for flavor and potential future mechanics."""

from ...engine.Item import Item


class WildBerries(Item):
    """Foraged berries that may be edible but carry risk; currently flavor-only."""

    def __init__(self) -> None:
        super().__init__(
            name="wild berries",
            description=(
                "A handful of small, juicy berries. They look edible, but you can't be "
                "sure they're safe."
            ),
            short_name="berries",
            can_be_carried=True
        )
