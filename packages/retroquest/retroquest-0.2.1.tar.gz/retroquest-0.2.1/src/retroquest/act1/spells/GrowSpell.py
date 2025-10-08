"""Grow spell that encourages plants to flourish."""

from ...engine.Spell import Spell
from ...engine.GameState import GameState
from ...engine.Item import Item

class GrowSpell(Spell):
    """Spell that encourages plants to flourish; delegates growth to items."""

    def __init__(self) -> None:
        desc = "A nature spell that encourages plants to flourish."
        super().__init__("grow", desc)

    def cast_spell(self, _game_state: GameState) -> str:
        return (
            "[event]You cast [spell_name]grow[/spell_name].[/event]\n"
            "The nearby plants seem to respond with vibrant energy, "
            "but nothing else happens."
        )

    def cast_on_item(self, game_state: GameState, target_item: Item) -> str:
        return target_item.grow(game_state)
