"""A prismatic lantern used to illuminate underwater passages."""
from ...engine.GameState import GameState
from ...engine.Item import Item


class PrismLantern(Item):
    """A prismatic lantern used to illuminate underwater passages."""

    def __init__(self) -> None:
        """Initialize Prism Lantern with description and properties."""
        super().__init__(
            name="Prism Lantern",
            description=(
                "A faceted lantern of glass ribs and brass, made to scatter light "
                "into clear paths."
            ),
            short_name="lantern",
            can_be_carried=True,
        )

    def use_with(self, game_state: GameState, other_item: Item) -> str:
        """Handle using the lantern with another item."""
        from .LanternBracket import LanternBracket
        if isinstance(other_item, LanternBracket):
            return game_state.current_room.mount_lantern(game_state)
        return super().use_with(game_state, other_item)
