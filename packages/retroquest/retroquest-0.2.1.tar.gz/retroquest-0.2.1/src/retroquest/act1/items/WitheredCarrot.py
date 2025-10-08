"""WitheredCarrot item that can be revived into a fresh carrot."""

from ...engine.Item import Item


class WitheredCarrot(Item):
    """A shriveled carrot that can be revived into a fresh carrot."""

    def __init__(self) -> None:
        """Initialize the withered carrot with its name and description."""
        super().__init__(
            name="withered carrot",
            description=(
                "A shriveled, orange carrot barely clinging to life. It looks edible, "
                "but only just."
            ),
            short_name="carrot",
            can_be_carried=True,
        )

    def revive(self) -> str:
        """Turn the withered carrot into a fresh carrot and return a message."""
        self.name = "fresh carrot"
        self.short_name = "carrot"
        self.description = (
            "A vibrant, healthy carrot, freshly revived. It looks delicious and "
            "full of nutrients."
        )
        return (
            "The [item_name]" + self.name.lower() + "[/item_name] looks vibrant and healthy!"
        )
