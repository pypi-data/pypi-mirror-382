"""Unlock spell for Act 3."""

from ...engine.GameState import GameState
from ...engine.Item import Item
from ...engine.Spell import Spell
from ..items.Locker import Locker


class UnlockSpell(Spell):
    """A deft sigil that loosens fused pins and grudging clasps."""

    def __init__(self) -> None:
        """Initialize Unlock spell with description."""
        super().__init__(
            name="unlock",
            description="A deft sigil that loosens fused pins and grudging clasps.",
        )

    def cast_on_item(self, game_state: GameState, target_item: Item) -> str:
        """Cast unlock spell on target item, specifically handling lockers."""
        if isinstance(target_item, Locker):
            return target_item.unlock(game_state)
        return (
            f"[failure]You cast [spell_name]{self.get_name()}[/spell_name] on "
            f"[item_name]{target_item.get_name()}[/item_name], but no lock "
            "yields.[/failure]"
        )
