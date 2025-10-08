"""Basic matches used to ignite candles and lanterns in Act I."""

from ...engine.Item import Item
from ...engine.GameState import GameState

class Matches(Item):
    """
    Basic ignition source enabling illumination and ritual flavor actions.
    """

    def __init__(self) -> None:
        """Initialize the Matches item with name and description."""
        super().__init__(
            name="matches",
            description=(
                "A small box of matches. Useful for lighting fires, candles, or lanterns."
            ),
        )

    def prevent_pickup(self) -> str:
        """Shopkeeper prevents taking the matches unless they've been purchased."""
        if not self.can_be_carried_flag:
            return (
                "[character_name]Shopkeeper[/character_name] quickly steps over. "
                "[dialogue]'Hold on there, friend! That "
                f"[item_name]{self.get_name()}[/item_name] is merchandise, not a free sample. "
                "If you want it, you'll need to buy it proper-like.'[/dialogue]"
            )
        return ""  # Allow pickup if can_be_carried is True

    def use_with(self, game_state: 'GameState', other_item: Item) -> str:
        """Delegate to Candle's use_with if applicable, otherwise fallback."""
        from .Candle import Candle
        if isinstance(other_item, Candle):
            return other_item.use_with(game_state, self)
        return super().use_with(game_state, other_item)
