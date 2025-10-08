"""Mend Spell (Act II)

Purpose:
    Foundational utility spell enabling repair of damaged objects and—critically—restoration
    of the Hidden Library's protective enchantments to prove scholarly worthiness.

Acquisition:
    Granted by the Local Craftsmen after demonstrating civic helpfulness. The
    reward is given for actions like assisting elderly residents in the town.

Core Mechanics:
    - Generic repair flavor for any item whose description contains 'broken' or 'damaged'.
        - Special-case: Casting on ProtectiveEnchantments (Hidden Library) sets
            FLAG_MENDED_LIBRARY_ENCHANTMENTS.

Story Flags:
    - Sets: FLAG_MENDED_LIBRARY_ENCHANTMENTS (first successful repair of protective wards).
    - Reads: Same flag to ensure idempotent subsequent messaging.

Design Notes:
        - Uses deferred import of ProtectiveEnchantments to avoid cyclic dependency
            with room and item definitions.
        - Keeps broad text matching simple. Future refinement could introduce an
            interface (Repairable) rather than using string parsing heuristics.
"""

from ...engine.Spell import Spell
from ..Act2StoryFlags import FLAG_MENDED_LIBRARY_ENCHANTMENTS
from ...engine.GameState import GameState
from ...engine.Item import Item

class MendSpell(Spell):
    """Utility repair spell with special handling for library protective wards.

    Purpose:
        Provides baseline repair functionality and advances Hidden Library ward
        restoration when used on protective enchantments.

    Mechanics:
        - Ambient ``cast_spell``: flavor if nothing repairable nearby.
        - ``cast_on_item``: sets ward flag when target is ProtectiveEnchantments.
        - Fallback heuristic repairs any item whose description contains 'broken' or
          'damaged'.

    Design Notes:
        Uses string matching instead of an interface; may later evolve to a dedicated
        Repairable protocol if repair targets diversify.
    """

    def __init__(self) -> None:
        super().__init__(
            name="mend",
            description=(
                "A basic repair spell that can fix broken objects, torn clothing, and "
                "minor damage to items. This fundamental magic is essential for any "
                "aspiring mage."
            ),
        )

    def cast_spell(self, _game_state: GameState) -> str:
        name = self.get_name()
        return (
            f"[success]You cast [spell_name]{name}[/spell_name] into the air. The spell "
            "shimmers briefly, looking for something to repair, but finds nothing "
            "that needs mending nearby.[/success]"
        )

    def cast_on_item(self, game_state: GameState, target_item: Item) -> str:
        from ..items.ProtectiveEnchantments import ProtectiveEnchantments
        # Special handling for protective enchantments in Hidden Library
        if isinstance(target_item, ProtectiveEnchantments):
            if not game_state.get_story_flag(FLAG_MENDED_LIBRARY_ENCHANTMENTS):
                game_state.set_story_flag(FLAG_MENDED_LIBRARY_ENCHANTMENTS, True)
                name = self.get_name()
                iname = target_item.get_name()
                return (
                    f"[success]You cast [spell_name]{name}[/spell_name] on the damaged "
                    f"[item_name]{iname}[/item_name]. The magical barriers flicker and "
                    "stabilize as your repair magic restores their integrity. The "
                    "shimmering barriers around the most valuable texts now glow "
                    "steadily. You have proven your worthiness and respect for "
                    "ancient knowledge.[/success]"
                )
            else:
                iname = target_item.get_name()
                return (
                    f"[info]The [item_name]{iname}[/item_name] have already been repaired "
                    "and are functioning properly.[/info]"
                )
        # Check if the item can be repaired (this is the original implementation)
        elif (
            "broken" in target_item.get_description().lower()
            or "damaged" in target_item.get_description().lower()
        ):
            name = self.get_name()
            iname = target_item.get_name()
            return (
                f"[success]You cast [spell_name]{name}[/spell_name] on "
                f"[item_name]{iname}[/item_name]. The magical energy flows through the "
                "item, repairing damage and restoring it to working condition![/success]"
            )
        else:
            name = self.get_name()
            iname = target_item.get_name()
            return (
                f"[info]You cast [spell_name]{name}[/spell_name] on "
                f"[item_name]{iname}[/item_name], but it doesn't appear to need any "
                "repairs. The spell has no effect.[/info]"
            )
