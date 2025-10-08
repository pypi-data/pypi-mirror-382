"""Rope item used for climbing, tying, and mechanical interactions."""

from ...engine.Item import Item
from ...engine.GameState import GameState

class Rope(Item):
    """Early shop item used for mechanical or traversal interactions."""

    def __init__(self) -> None:
        """Initialize the Rope item with name and description."""
        super().__init__(
            name="rope",
            description=(
                "A long, sturdy coil of rope. Useful for climbing, tying, or "
                "hauling things."
            )
        )

    def prevent_pickup(self) -> str:
        """Shopkeeper prevents taking the rope unless it has been purchased."""
        if not self.can_be_carried_flag:
            name_html = f"[item_name]{self.get_name()}[/item_name]"
            return (
                "[character_name]Shopkeeper[/character_name] quickly steps over. "
                "[dialogue]'Hold on there, friend! That "
                + name_html
                + (
                    " is merchandise, not a free sample. If you want it, "
                    "you'll need to buy it proper-like.'[/dialogue]"
                )
            )
        return ""

    def use_with(self, game_state: 'GameState', other_item: Item) -> str:
        """Delegate to Mechanism's use_with if applicable, otherwise fallback."""
        from .Mechanism import Mechanism
        if isinstance(other_item, Mechanism):
            return other_item.use_with(game_state, self)
        return super().use_with(game_state, other_item)
