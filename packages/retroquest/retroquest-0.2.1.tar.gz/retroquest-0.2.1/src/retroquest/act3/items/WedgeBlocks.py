"""Wedge Blocks item for Miners' Rescue quest."""
from ...engine.Item import Item
from ...engine.GameState import GameState


class WedgeBlocks(Item):
    """Tapered wooden blocks for prying and stabilizing rockfalls."""

    def __init__(self) -> None:
        """Initialize Wedge Blocks."""
        super().__init__(
            name="Wedge Blocks",
            description="Tapered wooden blocks used to pry and stabilize fallen rock.",
            short_name="wedges",
            can_be_carried=True,
        )

    def use_with(self, game_state: GameState, other_item: Item) -> str:
        """Handle using wedge blocks with other items."""
        from .FallenRock import FallenRock
        if isinstance(other_item, FallenRock):
            # Delegate to FallenRock's use_with method
            return other_item.use_with(game_state, self)
        return (
            f"[info]You can't use the wedge blocks with the "
            f"{other_item.get_name()}.[/info]"
        )
