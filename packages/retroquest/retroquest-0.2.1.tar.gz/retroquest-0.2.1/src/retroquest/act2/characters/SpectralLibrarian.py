"""Spectral Librarian (Act II)

Role:
        Guardian spirit of the ancient library, adjudicating the player's worthiness to access
        deeper lore (heritage revelation + Dispel spell) contingent on respectful restoration
        of protective enchantments.

Gating & Flow:
        - Requires FLAG_MENDED_LIBRARY_ENCHANTMENTS True to transition from neutral gatekeeper
            to friendly benefactor.
        - On first successful post-mend interaction: sets FLAG_SPECTRAL_LIBRARIAN_FRIENDLY,
            places Crystal Focus item, and grants contextual lore plus access to learn Dispel.

Story Flags:
        - Reads: FLAG_MENDED_LIBRARY_ENCHANTMENTS, FLAG_SPECTRAL_LIBRARIAN_FRIENDLY
        - Sets: FLAG_SPECTRAL_LIBRARIAN_FRIENDLY

Rewards:
        - Item: CrystalFocus added to current room (player must still pick it up, reinforcing
            interaction).
        - Knowledge: Heritage exposition + unlocking path for Dispel (spell learned via study,
            not immediate grant here).

Design Notes:
        - Spell objects are instantiated inline to obtain names for narrative clarity without
            premature acquisition.
        - Maintains single state transition ensuring idempotent follow-up dialogue.
        - If additional library depth is added later, consider branching on new flags while
            retaining this baseline friendly state as prerequisite.
"""

from ...engine.Character import Character
from ...engine.GameState import GameState
from ..Act2StoryFlags import (
    FLAG_MENDED_LIBRARY_ENCHANTMENTS,
    FLAG_SPECTRAL_LIBRARIAN_FRIENDLY
)

class SpectralLibrarian(Character):
    """Ghostly guardian NPC who controls access to the library's deeper lore."""
    def __init__(self) -> None:
        super().__init__(
            name="Spectral Librarian",
            description=(
                "A ghostly figure who appears to be the eternal guardian of this ancient library. "
                "Their ethereal form shimmers with a soft blue light. Ancient wisdom gleams in "
                "their otherworldly eyes. They wear the robes of a scholar from ages past. Their "
                "presence emanates both knowledge and protective purpose. This spirit has "
                "watched over these texts for countless years, ensuring only the worthy gain "
                "access to the deepest secrets."
            ),
        )

    def talk_to(self, game_state: GameState) -> str:
        # Check if player has mended the protective enchantments first
        mended_enchantments = game_state.get_story_flag(FLAG_MENDED_LIBRARY_ENCHANTMENTS)
        if not game_state.get_story_flag(FLAG_SPECTRAL_LIBRARIAN_FRIENDLY):
            if mended_enchantments:
                game_state.set_story_flag(FLAG_SPECTRAL_LIBRARIAN_FRIENDLY, True)
                # Add Crystal Focus to the room for player to take
                from ..items.CrystalFocus import CrystalFocus
                crystal_focus = CrystalFocus()
                game_state.current_room.add_item(crystal_focus)
                # Get spell names
                from ..spells.MendSpell import MendSpell
                from ..spells.DispelSpell import DispelSpell
                mend_spell = MendSpell()
                dispel_spell = DispelSpell()
                mend_name = mend_spell.get_name()
                dispel_name = dispel_spell.get_name()
                crystal_name = crystal_focus.get_name()
                return (
                    f"[success][character_name]{self.get_name()}[/character_name]: 'Ah, you have "
                    "repaired the protective enchantments with your "
                    f"[spell_name]{mend_name}[/spell_name] "
                    "spell. This shows both magical ability and respect for ancient "
                    "knowledge. I shall reveal what you seek.' The spirit's eyes glow "
                    "brighter as they speak: 'Your bloodline traces back to the ancient "
                    "mages of Willowbrook, those who were chosen to guard against the "
                    "rising darkness. Malakar's interest in your village was no "
                    "coincidence - he seeks to corrupt or destroy the magical heritage "
                    "that flows through your veins.' They gesture to the ancient texts: '"
                    f"Study these tomes to learn the [spell_name]{dispel_name}[/spell_name] "
                    f"spell, and take this [item_name]{crystal_name}[/item_name] to "
                    "enhance your abilities. Your destiny as one of the Chosen is "
                    "beginning to unfold.'[/success]"
                )
            else:
                return (
                    f"[character_name]{self.get_name()}[/character_name]: 'Welcome, "
                    f"seeker of knowledge. "
                    "I am the eternal guardian of this repository. The protective enchantments "
                    "around the most valuable texts have been damaged by time. Prove your "
                    "worthiness by repairing them, and I shall share the knowledge you "
                    "seek about your heritage and destiny.'"
                )
        else:
            # Get spell name
            from ..spells.DispelSpell import DispelSpell
            dispel_spell = DispelSpell()
            return (
                f"[character_name]{self.get_name()}[/character_name]: 'You have proven yourself "
                f"worthy and learned what this library can teach. The knowledge of your "
                f"bloodline and the [spell_name]{dispel_spell.get_name()}[/spell_name] spell "
                "will serve you well in the challenges ahead. Remember: you are part of "
                "an ancient lineage chosen to stand against the darkness. Use this "
                "knowledge wisely.'"
            )

    def examine(self, _game_state: GameState) -> str:
        return (
            f"The [character_name]{self.get_name()}[/character_name] appears to be a scholar from "
            "ancient times, their ethereal form bound to this library by duty and purpose. "
            "They radiate wisdom accumulated over centuries of guarding these precious texts. "
            "There's something both melancholy and noble about their eternal vigil."
        )
