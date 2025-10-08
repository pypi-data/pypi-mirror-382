"""Revive spell for restoring life to withered plants and small creatures."""

from ...engine.Spell import Spell
from ...engine.GameState import GameState
from ...engine.Item import Item
from ...engine.Character import Character
from ..items.WitheredCarrot import WitheredCarrot

class ReviveSpell(Spell):
    """Restore life to withered plants or recently deceased small creatures."""
    def __init__(self) -> None:
        description = (
            "A potent spell that can restore life to withered plants or even recently "
            "deceased small creatures."
        )
        super().__init__("revive", description)

    def cast_spell(self, game_state: GameState) -> str:
        """Cast without a target: check gating then prompt for a target."""

        if not game_state.get_story_flag("magic_fully_unlocked"):
            return (
                "[event]You focus your will, a faint warmth spreads from your fingertips, "
                "but nothing happens. It feels like the magic is just out of reach.[/event]"
            )

        return "[failure]What do you want to cast [spell_name]revive[/spell_name] on?[/failure]"

    def cast_on_item(self, game_state: GameState, target_item: Item) -> str:
        """Attempt to revive an item; delegate to the item's revive logic when present."""

        if not game_state.get_story_flag("magic_fully_unlocked"):
            return (
                "[event]You focus your will, a faint warmth spreads from your fingertips, "
                "but nothing happens. It feels like the magic is just out of reach.[/event]"
            )

        if isinstance(target_item, WitheredCarrot):
            # The WitheredCarrot is revived in place (inventory or room).
            # revive() returns a short message describing the transformation.
            revival_message = target_item.revive()

            return (
                "[event]You channel the life-giving energy into the "
                "[item_name]Withered Carrot[/item_name].[/event]\n"
            ) + revival_message

        name = target_item.get_name()
        return (
            f"[failure]You can't revive [item_name]{name}[/item_name].[/failure]"
        )

    def cast_on_character(self, game_state: GameState, target_character: Character) -> str:
        """Casting on characters is not supported in Act I; always fails for living targets."""

        if not game_state.get_story_flag("magic_fully_unlocked"):
            return (
                "[event]You focus your will, a faint warmth spreads from your fingertips, "
                "but nothing happens. It feels like the magic is just out of reach.[/event]"
            )

        name = target_character.get_name()
        return (
            f"[failure]You can't revive [character_name]{name}[/character_name]. "
            "They are very much alive![/failure]"
        )
