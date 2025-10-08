"""Dispel Spell (Act II)

Purpose:
    Advanced counter-magic used to neutralize hostile enchantments and complete the final
    stage of Elena's curse cure sequence when cast on her by invoking specialized character logic.

Acquisition:
    Learned via study after assisting the Spectral Librarian (post-mending of library wards).

Core Mechanics:
    - Generic success responses when used on arbitrary characters or items (flavor utility).
    - Special-case: Casting on BarmaidElena defers to her receive_dispel_final_cure(game_state
    method.

Design Notes:
    - Keeps cure logic centralized in the character class to avoid distributing narrative state
    here.
    - Future expansions (e.g., barrier removal) should branch via item or room markers rather than
    expanding conditionals inline.
"""

from ...engine.Spell import Spell
from ...engine.GameState import GameState
from ...engine.Character import Character

class DispelSpell(Spell):
    """Counter-magic spell for breaking enchantments and Elena's final cure phase.

    Purpose:
        Breaks hostile magical effects; when used on Elena triggers her final recovery
        method to complete the multi-step curse sequence.

    Mechanics:
        - ``cast_spell``: ambient cast, returns generic counter-magic flavor.
        - ``cast_on_character``: delegates to Elena's ``receive_dispel_final_cure`` if
          she is the target, else generic dispel narration.
        - ``cast_on_item``: flavor removal of latent enchantments.

    Design Notes:
        Narrative completion logic resides in the character to keep the spell lean and
        extensible for future barrier / ward interactions.
    """

    def __init__(self) -> None:
        super().__init__(
            name="dispel",
            description=(
                "A powerful counter-magic spell that can break magical barriers, "
                "dispel illusions, and counter enemy enchantments. This advanced "
                "magic requires deep understanding of magical theory and precise "
                "control."
            ),
        )

    def cast_spell(self, _game_state: GameState) -> str:
        name = self.get_name()
        return (
            f"[success]You cast [spell_name]{name}[/spell_name], sending out waves of "
            "counter-magic that neutralize hostile enchantments. The spell ripples "
            "through the air, ready to break magical barriers and curses, but finds "
            "no active magic to dispel nearby.[/success]"
        )

    def cast_on_character(self, game_state: GameState, target_character: Character) -> str:
        from ..characters.BarmaidElena import BarmaidElena  # Import here to avoid circular imports

        # Special handling for Elena's curse - final step
        if isinstance(target_character, BarmaidElena):
            # Check if Elena has the receive_dispel_final_cure method and call it
            return target_character.receive_dispel_final_cure(game_state)
        else:
            name = self.get_name()
            tname = target_character.get_name()
            return (
                f"[success]You cast [spell_name]{name}[/spell_name] on "
                f"[character_name]{tname}[/character_name]. Counter-magic flows "
                "around them, dispelling any minor enchantments and magical "
                "effects they may have been affected by.[/success]"
            )

    def cast_on_item(self, _game_state: GameState, target_item) -> str:
        # This could be used for breaking magical barriers or dispelling cursed items
        name = self.get_name()
        iname = target_item.get_name()
        return (
            f"[success]You cast [spell_name]{name}[/spell_name] on "
            f"[item_name]{iname}[/item_name]. Counter-magic flows through the "
            "item, neutralizing any magical enchantments or curses that may "
            "have been affecting it.[/success]"
        )
