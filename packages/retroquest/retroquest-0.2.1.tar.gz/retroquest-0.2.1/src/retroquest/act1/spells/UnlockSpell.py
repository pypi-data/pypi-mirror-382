"""Unlock spell used to open simple magical or mundane locks."""

from ...engine.Spell import Spell
from ...engine.GameState import GameState
from ...engine.Item import Item
from ...engine.Character import Character
# Ensure MysteriousBox is imported
from ..items.MysteriousBox import MysteriousBox

class UnlockSpell(Spell):
    """Spell that attempts to open locks, magical or mundane, by focused intent."""

    def __init__(self) -> None:
        description = (
            "A spell that can open magically sealed or complex mundane locks."
        )
        super().__init__("unlock", description)
    def cast_spell(self, _game_state: GameState) -> str:
        """Handle casting without an explicit target: prompt for an object to unlock."""
        return (
            "[failure]You cast [spell_name]unlock[/spell_name] into the air, but magic requires a "
            "target to focus on. What do you wish to unlock?[/failure]"
        )

    def cast_on_item(self, game_state: GameState, target_item: Item) -> str:
        """Attempt to unlock an item; delegate to the item's unlock logic when present."""

        # The game's find_item handles locating items; here we only test type and delegate.
        if isinstance(target_item, MysteriousBox):
            return target_item.unlock(game_state)

        name = target_item.get_name()
        return (
            f"[failure]You cast [spell_name]unlock[/spell_name] on [item_name]{name}[/item_name], "
            f"but it seems to lack any locks or magical seals to open.[/failure]"
        )

    def cast_on_character(self, _game_state: GameState, target_character: Character) -> str:
        """Casting on characters always fails; characters are not unlockable objects."""

        name = target_character.get_name()
        return (
            f"[failure]You can't unlock [character_name]{name}[/character_name]. They are not a "
            "locked object![/failure]"
        )
