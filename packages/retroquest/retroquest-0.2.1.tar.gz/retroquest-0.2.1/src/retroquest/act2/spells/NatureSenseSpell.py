"""Nature Sense Spell (Act II)

Purpose:
    Sensory amplification magic revealing hidden natural presences and
    detecting boundaries.
    Casting in the right place can spawn a Water Nymphs encounter in
    Whispering Glade on first use.

Core Mechanics:
    - First cast in WhisperingGlade: adds WaterNymphs NPC to room and returns discovery narration.
    - Subsequent casts in Glade: informational reminder.
    - Contextual flavor for forest / enchanted / transition zones; generic elsewhere.

State Tracking:
        - nature_sense_used (instance boolean) prevents duplicate spawning.
            This ensures idempotent narrative on subsequent casts.

Design Notes:
        - Maintains self-contained spawn logic instead of pushing into the room to
            keep the causal link (spell -> appearance) explicit.
    - If more spawn-capable spells emerge, consider abstracting a Summoning/Reveal interface.
"""

from ...engine.Spell import Spell
from ...engine.GameState import GameState
from ..characters.WaterNymphs import WaterNymphs

class NatureSenseSpell(Spell):
    """Reveals hidden natural presences and spawns water nymphs in Whispering Glade.

    Purpose:
        Enhances environmental perception and triggers first-time summoning of Water
        Nymphs in the appropriate mystical location.

    Mechanics:
        - First cast in Whispering Glade: spawns WaterNymphs, sets internal usage flag.
        - Subsequent casts: contextual sensory feedback only.
        - Keyword-based room classification (forest / enchanted / transition) shapes
          flavor output.

    Design Notes:
        Keeps spawn logic local to maintain clear causal link (spell -> appearance). A
        future generic Reveal/Summon framework could unify similar mechanics.
    """

    def __init__(self) -> None:
        super().__init__(
            name="nature_sense",
            description=(
                "A druidic spell that enhances your connection to the natural world. "
                "When cast, it allows you to sense the life force of plants and "
                "animals around you, detect hidden paths through forests, and "
                "understand the subtle warnings that nature provides about dangers "
                "ahead. This ancient magic was once commonly known among those who "
                "lived in harmony with the wilderness."
            )
        )
        self.nature_sense_used = False

    def cast_spell(self, game_state: GameState) -> str:
        # Deferred import to avoid circular imports
        from ..rooms.WhisperingGlade import WhisperingGlade
        # Special handling for Whispering Glade
        if isinstance(game_state.current_room, WhisperingGlade):
            if not self.nature_sense_used:
                self.nature_sense_used = True
                # Add the Water Nymphs to the room when first cast
                game_state.current_room.characters.append(WaterNymphs())
                name = self.get_name()
                return (
                    f"[spell_effect]You cast [spell_name]{name}[/spell_name] and extend "
                    "your awareness throughout the glade. Immediately, you "
                    "sense magical presences by the stream - graceful forms of "
                    "living water and moonlight. The water nymphs reveal "
                    "themselves, shimmering into visibility as they recognize "
                    "your magical sensitivity and respect for the natural "
                    "world.[/spell_effect]"
                )
            else:
                name = self.get_name()
                return (
                    f"[info]Your [spell_name]{name}[/spell_name] reveals the familiar "
                    "presence of the water nymphs by the sacred stream, their forms "
                    "visible and welcoming.[/info]"
                )
        elif (
            "forest" in game_state.current_room.name.lower()
            or "enchanted" in game_state.current_room.name.lower()
        ):
            # In forest areas, provide enhanced sensory information
            name = self.get_name()
            return (
                f"[success]You cast [spell_name]{name}[/spell_name] and feel your awareness "
                "expand throughout the surrounding forest. The whisper of leaves "
                "speaks of safe passages, the rustle of small creatures warns of "
                "predators, and the very air reveals the health of the woodland. "
                "You sense several hidden paths that wind through the trees, offering "
                "safer routes through the wilderness.[/success]"
            )
        elif "transition" in game_state.current_room.name.lower():
            # In transition areas, help detect magical boundaries
            name = self.get_name()
            return (
                f"[success]You cast [spell_name]{name}[/spell_name] and feel the magical "
                "boundaries that separate different realms. The spell reveals the ebb "
                "and flow of natural energy, showing you where the civilized world "
                "ends and wilder magics begin. You can sense the ancient protections "
                "woven into the very landscape.[/success]"
            )
        else:
            # In other areas, provide general nature awareness
            name = self.get_name()
            return (
                f"[info]You cast [spell_name]{name}[/spell_name] and feel a subtle "
                "connection to the natural world around you. While there isn't much "
                "wilderness here, you gain a better understanding of the living "
                "things in this area and their relationship to the environment.[/info]"
            )
