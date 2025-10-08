"""Reinforced Braces item for Miners' Rescue quest."""
from ...engine.Item import Item
from ...engine.GameState import GameState


class ReinforcedBraces(Item):
    """Heavy iron braces for stabilizing collapsed tunnels."""

    def __init__(self) -> None:
        """Initialize Reinforced Braces."""
        super().__init__(
            name="Reinforced Braces",
            description="Heavy iron braces used to shore up unstable rock walls.",
            short_name="braces",
            can_be_carried=True,
        )

    def use_with(self, game_state: GameState, other_item: Item) -> str:
        """Handle using reinforced braces with other items."""
        from .FallenRock import FallenRock
        if isinstance(other_item, FallenRock):
            # Delegate to FallenRock's use_with method
            return other_item.use_with(game_state, self)
        return (
            f"[info]You can't use the reinforced braces with the "
            f"{other_item.get_name()}.[/info]"
        )
