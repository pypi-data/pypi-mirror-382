"""Heal spell for Act I — simple restorative magic for player and NPCs."""

from ...engine.Spell import Spell
from ...engine.GameState import GameState
from ...engine.Character import Character

class HealSpell(Spell):
    """Simple restorative spell for Act I; supports self-cast and targeted healing."""

    def __init__(self) -> None:
        super().__init__(
            "heal",
            "A restorative spell that mends wounds and alleviates ailments.",
        )

    def cast_spell(self, _game_state: GameState) -> str:
        """Cast the spell without a target (self-cast behavior)."""

        # Placeholder for future health logic (e.g., game_state.player.heal(20)).
        return (
            "[event]You cast [spell_name]heal[/spell_name] on yourself.[/event]\n"
            "A warm light envelops you, and you feel your wounds mending."
        )

    def cast_on_character(self, _game_state: GameState, target_character: Character) -> str:
        """Heal a target character and return the narrative describing the effect."""

        name = target_character.get_name()
        return (
            f"[event]You cast [spell_name]heal[/spell_name] on [character_name]{name}"
            "[/character_name].[/event]\n"
            "A warm light envelops "
            f"[character_name]{name}[/character_name] and the character seems a bit healthier."
        )
