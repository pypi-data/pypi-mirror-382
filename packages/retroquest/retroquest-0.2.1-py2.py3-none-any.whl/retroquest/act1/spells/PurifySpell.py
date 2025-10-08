"""Purify spell for cleansing environmental corruption."""

from ...engine.Spell import Spell
from ...engine.GameState import GameState
from ...engine.Item import Item
from ...engine.Character import Character
from ..items.Well import Well

class PurifySpell(Spell):
    """Cleansing spell that removes impurities from items or environments."""

    def __init__(self) -> None:
        desc = (
            "A cleansing spell that removes impurities from water or other "
            "substances."
        )
        super().__init__("purify", desc)

    def cast_spell(self, game_state: GameState) -> str:
        if not game_state.get_story_flag("magic_fully_unlocked"):
            return (
                f"[event]You attempt to cast [spell_name]{self.get_name()}[/spell_name], "
                "but the magic fizzles out, achieving nothing.[/event]\n"
                "It feels like the magic is just out of reach."
            )
        return (
            f"[event]You cast [spell_name]{self.get_name()}[/spell_name].[/event]\n"
            "A cleansing energy flows from your hands."
        )

    def cast_on_item(self, game_state: GameState, target_item: Item) -> str:
        if not game_state.get_story_flag("magic_fully_unlocked"):
            return (
                f"[event]You attempt to cast [spell_name]{self.get_name()}[/spell_name], "
                "but the magic fizzles out, achieving nothing.[/event]\n"
                "It feels like the magic is just out of reach."
            )
        if isinstance(target_item, Well):
            return target_item.purify(game_state)
        name = target_item.get_name()
        return (
            f"[event]You cast [spell_name]{self.get_name()}[/spell_name] on "
            f"[item_name]{name}[/item_name].[/event]\n"
            "A cleansing energy flows from your hands, but nothing else "
            "seems to happen."
        )

    def cast_on_character(self, game_state: GameState, target_character: Character) -> str:
        if not game_state.get_story_flag("magic_fully_unlocked"):
            return (
                f"[event]You attempt to cast [spell_name]{self.get_name()}[/spell_name], "
                "but the magic fizzles out, achieving nothing.[/event]\n"
                "It feels like the magic is just out of reach."
            )

        name = target_character.get_name()
        return (
            f"[event]You cast [spell_name]{self.get_name()}[/spell_name] on "
            f"[character_name]{name}[/character_name].[/event]\n"
            "A cleansing energy flows around "
            f"{name}, purifying their spirit and lifting any negative influences."
        )
