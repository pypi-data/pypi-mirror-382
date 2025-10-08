"""Stick item used for basic interactions and combinations."""

from ...engine.Item import Item


class Stick(Item):
    """A simple stick useful for poking, walking, or combining with tools."""

    def __init__(self) -> None:
        """Initialize the stick item with name and description."""
        super().__init__(
            name="stick",
            description=(
                "A sturdy stick, perfect for walking, poking, or perhaps as a makeshift "
                "weapon."
            ),
            can_be_carried=True,
        )

    def use_with(self, game_state, other_item: Item) -> str:
        """Delegate interactions when combined with another item when applicable.

        If the other item is a `MagneticFishingRod` delegate the action to it so
        the rod can implement the correct combined behavior.
        """
        from .MagneticFishingRod import MagneticFishingRod
        if isinstance(other_item, MagneticFishingRod):
            return other_item.use_with(game_state, self)
        return super().use_with(game_state, other_item)
