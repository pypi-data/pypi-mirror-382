"""Miner's Key item for unlocking supply crates in Tool Cache."""

from ...engine.Item import Item
from ...engine.GameState import GameState

class MinersKey(Item):
    """A sturdy iron key used by the mine overseer."""
    def __init__(self) -> None:
        super().__init__(
            name="Miner's Key",
            description="A heavy iron key, pitted with age, used to open the supply crates.",
            short_name="key",
            can_be_carried=True,
        )

    def use_with(self, game_state: GameState, other_item: Item):
        """Delegate to SupplyCrate's use_with if used with a SupplyCrate."""
        from .SupplyCrate import SupplyCrate
        if isinstance(other_item, SupplyCrate):
            return other_item.use_with(game_state, self)
        return super().use_with(game_state, other_item)
