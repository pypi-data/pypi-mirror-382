"""Purify spell for Act 3."""

from ...engine.Character import Character
from ...engine.GameState import GameState
from ...engine.Item import Item
from ...engine.Spell import Spell
from ..items.WardingPillars import WardingPillars


class PurifySpell(Spell):
    """Act III variant of Purify, customized for Sunken Ruins interactions."""
    def __init__(self) -> None:
        """Initialize Purify spell with description and behavior."""
        super().__init__(
            name="purify",
            description=(
                "A cleansing rite tuned to salt and stone; it scours sea-grit and "
                "wakes dormant ward-glyphs."
            ),
        )

    def cast_spell(self, _game_state: GameState) -> str:
        """Cast purify spell providing cleansing aura."""
        # Act III version has no global gating; it always responds with a cleansing aura
        return (
            f"[event]You cast [spell_name]{self.get_name()}[/spell_name].[/event]\n"
            "A brine-bright clarity flows from your hands, cutting through the mire."
        )

    def cast_on_item(self, game_state: GameState, target_item: Item) -> str:
        """Cast purify on target item, with special handling for warding pillars."""
        # Special handling for the warding pillars in the Outer Wards
        if isinstance(target_item, WardingPillars):
            return target_item.purify(game_state)
        return (
            f"[event]You cast [spell_name]{self.get_name()}[/spell_name] on "
            f"[item_name]{target_item.get_name()}[/item_name].[/event]\n"
            "Saltlight skims its surface, though nothing more changes."
        )

    def cast_on_character(self, _game_state: GameState, target_character: Character) -> str:
        """Cast purify on target character to provide cleansing calm."""
        return (
            f"[event]You cast [spell_name]{self.get_name()}[/spell_name] on "
            f"[character_name]{target_character.get_name()}[/character_name].[/event]\n"
            "A cleansing calm settles, washing away lingering dread."
        )
