"""Bless spell for Act 3, capable of sanctifying items like echo stones."""

from ...engine.Spell import Spell
from ...engine.GameState import GameState
from ...engine.Character import Character
from ...engine.Item import Item


class BlessSpell(Spell):
    """Divine incantation granting protection and sanctifying power."""

    def __init__(self) -> None:
        """Initialize BlessSpell with enhanced capabilities for Act 3."""
        desc = (
            "A divine incantation that offers protection and strength, and can "
            "sanctify sacred items for ritual purposes."
        )
        super().__init__("bless", desc)

    def cast_spell(self, game_state: GameState) -> str:
        """Cast bless on self."""
        game_state.set_story_flag("journey_bless_completed", True)
        return (
            "[event]You cast [spell_name]bless[/spell_name] on yourself.[/event]\n"
            "Your resolve is strengthened, and you feel more prepared for the "
            "challenges that lie ahead on your journey."
        )

    def cast_on_character(self, _game_state: GameState, target_character: Character) -> str:
        """Cast bless on a character."""
        name = target_character.get_name()
        return (
            f"[event]You cast [spell_name]bless[/spell_name] on "
            f"[character_name]{name}[/character_name].[/event]\n"
            "A divine light surrounds "
            f"[character_name]{name}[/character_name], and they seem "
            "strengthened and more resolute."
        )

    def cast_on_item(self, game_state: GameState, target_item: Item) -> str:
        """Cast bless on an item (new functionality for Act 3)."""
        # Check if the item has a receive_spell method
        if hasattr(target_item, 'receive_spell'):
            return target_item.receive_spell("bless", game_state)
        else:
            name = target_item.get_name()
            return (
                f"[failure]The [spell_name]bless[/spell_name] spell has no effect on "
                f"[item_name]{name}[/item_name].[/failure]"
            )
