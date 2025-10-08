"""Bless spell providing a simple protective boon."""

from ...engine.Spell import Spell
from ...engine.GameState import GameState
from ...engine.Character import Character

class BlessSpell(Spell):
    """Divine incantation granting temporary protection and strength to a target."""

    def __init__(self) -> None:
        desc = (
            "A divine incantation that offers protection and strength to the caster."
        )
        super().__init__("bless", desc)

    def cast_spell(self, game_state: GameState) -> str:
        game_state.set_story_flag("journey_bless_completed", True)
        return (
            "[event]You cast [spell_name]bless[/spell_name] on yourself.[/event]\n"
            "Your resolve is strengthened, and you feel more prepared for the "
            "challenges that lie ahead on your journey."
        )

    def cast_on_character(self, _game_state: GameState, target_character: Character) -> str:
        name = target_character.get_name()
        return (
            f"[event]You cast [spell_name]bless[/spell_name] on "
            f"[character_name]{name}[/character_name].[/event]\n"
            "A divine light surrounds "
            f"[character_name]{name}[/character_name], and they seem "
            "strengthened and more resolute."
        )
