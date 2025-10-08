"""Bucket item for water and environmental interactions."""

from ...engine.GameState import GameState
from .Well import Well
from ...engine.Item import Item


class Bucket(Item):
    """
    Early utility container that teaches players about combining items with environmental features.
    """

    def __init__(self) -> None:
        """Initialize the Bucket item with name, description, and carry status."""
        super().__init__(
            name="bucket",
            description=(
                "A sturdy wooden bucket with a rope handle. It's perfect for drawing water "
                "from a well or carrying supplies."
            ),
            can_be_carried=True
        )

    def use_with(self, _game_state: GameState, other_item: Item) -> str:
        """Use bucket with well to fill it, otherwise fail."""
        if isinstance(other_item, Well):
            if self.name == "bucket":  # Check if it's not already full
                self.name = "bucket (full)"
                self.description = (
                    "A sturdy wooden bucket with a rope handle. It is full of clear water "
                    "drawn from the well."
                )
                return (
                    "[event]You lower the [item_name]bucket[/item_name] into the "
                    "[item_name]well[/item_name] and draw it up, full of clear water.[/event]"
                )
            else:
                return (
                    "[failure]The [item_name]bucket[/item_name] is already full.[/failure]"
                )
        else:
            return (
                f"[failure]You can't seem to use the [item_name]bucket[/item_name] together "
                f"with [item_name]{other_item.get_name()}[/item_name]. Perhaps near something "
                f"with water?[/failure]"
            )
