"""Protective enchantments item for Act 2 (environmental barrier)."""

from ...engine.Item import Item
from ..Act2StoryFlags import FLAG_MENDED_LIBRARY_ENCHANTMENTS
from ...engine.GameState import GameState

class ProtectiveEnchantments(Item):
    """Static environmental magical barriers protecting restricted library texts."""
    def __init__(self) -> None:
        super().__init__(
            name="protective enchantments",
            short_name="enchantments",
            description=(
                "Shimmering magical barriers that surround the most valuable texts in the "
                "ancient library. These enchantments appear damaged by time, with flickering "
                "energy and weak points that suggest they need repair. The ancient magic that "
                "protects this knowledge requires restoration before the texts can be safely "
                "accessed."
            ),
            can_be_carried=False,
        )

    def examine(self, game_state: GameState) -> str:
        if game_state.get_story_flag(FLAG_MENDED_LIBRARY_ENCHANTMENTS):
            return (
                "The [item_name]protective enchantments[/item_name] now glow steadily with "
                "restored power. The magical barriers around the most valuable texts have "
                "been successfully repaired, allowing access to the ancient knowledge within."
            )
        else:
            return (
                "The [item_name]protective enchantments[/item_name] flicker weakly, showing clear "
                "signs of damage from the passage of time. These ancient magical barriers "
                "need to be repaired with restoration magic before they can properly protect "
                "the library's most precious texts."
            )

    def use_item(self, _game_state: GameState) -> str:
        """Use the protective enchantments (not directly usable)."""
        return (
            "[info]The protective enchantments are magical barriers, not something you "
            "can use directly.[/info]"
        )
