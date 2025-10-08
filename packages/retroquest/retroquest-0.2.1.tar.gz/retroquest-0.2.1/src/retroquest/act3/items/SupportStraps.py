"""Support Straps item for Miners' Rescue quest."""
from ...engine.Item import Item
from ...engine.GameState import GameState

class SupportStraps(Item):
    """Strong hemp straps for securing braces and debris."""
    def __init__(self) -> None:
        super().__init__(
            name="Support Straps",
            description="Strong hemp straps for binding braces and hauling debris.",
            short_name="straps",
            can_be_carried=True,
        )

    def use_with(self, game_state: GameState, other_item: "Item") -> str:
        """Handle using support straps with other items."""
        from .FallenRock import FallenRock
        if isinstance(other_item, FallenRock):
            return other_item.use_with(game_state, self)
        return f"[info]You can't use the Support Straps with {other_item.get_name()}.[/info]"
