"""Barmaid (Elena) NPC definition.

Role:
    Central afflicted character for "The Innkeeper's Daughter" quest. Provides a
    staged recovery arc that tutorializes multi-step magical intervention.

Recovery Sequence (state booleans):
    1. ``receive_greater_heal`` -> sets ``elena_initial_healing`` (stabilization)
    2. ``receive_crystal_water_purification`` -> sets ``elena_purified`` (cleansing)
    3. ``receive_dispel_final_cure`` -> sets quest completion flag

Story Flags:
    - ``FLAG_KNOWS_ELENA_CURSE`` (awareness / quest trigger)
    - ``FLAG_INNKEEPERS_DAUGHTER_COMPLETED`` (full cure)

Design Notes:
    Each phase updates description to give visual feedback and contextual next
    steps, reinforcing player understanding of layered magical problem solving.
"""

from ...engine.Character import Character
from ...engine.GameState import GameState
from ..Act2StoryFlags import FLAG_KNOWS_ELENA_CURSE, FLAG_INNKEEPERS_DAUGHTER_COMPLETED

class BarmaidElena(Character):
    """Afflicted NPC central to the Innkeeper's Daughter quest and multi-step cure."""
    def __init__(self) -> None:
        super().__init__(
            name="barmaid elena",
            description=(
                "A young woman who moves slowly and appears weakened by some "
                "affliction. Dark circles under her eyes and a pale complexion "
                "suggest she is suffering from a magical curse."
            ),
        )
        self.elena_initial_healing = False
        self.elena_purified = False

    def talk_to(self, game_state: GameState) -> str:
        if game_state.get_story_flag(FLAG_INNKEEPERS_DAUGHTER_COMPLETED):
            name = self.get_name()
            return (
                f"[character_name]{name}[/character_name]: *beaming with health and vitality* "
                "Oh, thank you so much! I feel like I'm alive again! The curse is "
                "completely gone, and I owe you my life. My father is so grateful - "
                "he insists you take our family's sacred charm as a token of our "
                "eternal gratitude. You are truly a hero!"
            )
        elif self.elena_purified:
            name = self.get_name()
            return (
                f"[character_name]{name}[/character_name]: *glowing with pure energy* "
                "I feel so much cleaner now! The blessed water has washed away the "
                "dark corruption that was clinging to my soul. The curse is almost "
                "gone - I can sense just a few dark tendrils remaining. One powerful "
                "dispelling spell should shatter the last of this evil enchantment!"
            )
        elif self.elena_initial_healing:
            name = self.get_name()
            return (
                f"[character_name]{name}[/character_name]: *looking much better but still "
                "weak* The healing magic has given me strength! I can feel the curse's "
                "grip weakening, but it's still there, clinging to me. I think you'll "
                "need to purify the dark magic with blessed water and then cast a "
                "powerful dispelling spell to break it completely."
            )
        elif not game_state.get_story_flag(FLAG_KNOWS_ELENA_CURSE):
            game_state.set_story_flag(FLAG_KNOWS_ELENA_CURSE, True)
            name = self.get_name()
            return (
                f"[character_name]{name}[/character_name]: *coughs weakly* Hello, traveler. "
                "I apologize for my appearance... I've been cursed by a dark wizard who "
                "passed through town weeks ago. The curse grows stronger each day, "
                "draining my life force. My father searches desperately for a cure, but "
                "I fear only someone with powerful magical abilities could break such "
                "dark magic."
            )
        else:
            return (
                f"[character_name]{self.get_name()}[/character_name]: *weakly* Have you found "
                "a way to break the curse? I can feel my strength fading more each day..."
            )

    def receive_greater_heal(self) -> str:
        """Handle receiving the greater_heal spell as the first step of the cure.
        """
        if self.elena_initial_healing:
            return "Elena is already strengthened by your healing magic."

        # Set the flag and update Elena's condition
        self.elena_initial_healing = True

        # Update Elena's description to show improvement
        self.description = (
            "A young woman who appears to be recovering from a serious affliction. "
            "While still pale and bearing signs of magical corruption, the healing "
            "magic has restored some of her strength and vitality. Her eyes show "
            "hope for the first time in weeks."
        )

        # Get spell name for display
        from ..spells.GreaterHealSpell import GreaterHealSpell
        greater_heal_spell = GreaterHealSpell()
        spell_name = greater_heal_spell.get_name()

        return (
            f"[success]You cast [spell_name]{spell_name}[/spell_name] on Elena, "
            "channeling powerful healing energy into her weakened form. The golden "
            "light battles against the dark tendrils of the curse, and while it cannot "
            "break the enchantment completely, it significantly strengthens Elena's "
            "life force. She gasps as color returns to her cheeks and she stands a "
            "little straighter.\n\n"
            "The healing has made her strong enough to endure the final steps of the "
            "cure, but the curse still clings to her. Now you'll need to purify her "
            "and dispel the curse.[/success]"
        )

    def receive_crystal_water_purification(
        self, game_state: GameState
    ) -> str:  # game_state kept for interface consistency
        """Handle using crystal-clear water on Elena as the second step of the cure"""
        if self.elena_purified:
            return "Elena has already been purified with the crystal-clear water."

        if not self.elena_initial_healing:
            return (
                "Elena is too weak from the curse. You need to heal her "
                "before attempting purification."
            )

        # Check if player has crystal-clear water
        if not game_state.has_item("crystal-clear water"):
            return "You need [item_name]crystal-clear water[/item_name] to purify Elena."

        # Use the crystal-clear water and set the purification flag
        self.elena_purified = True

        # Update Elena's description to show purification
        self.description = (
            "A young woman who radiates a faint, pure light. The blessed water has "
            "cleansed away much of the dark corruption, leaving her looking almost "
            "healthy. Her skin has a subtle luminous quality and her eyes are bright "
            "with hope, though traces of the curse still linger."
        )

        return (
            "[success]You carefully pour the [item_name]crystal-clear water[/item_name] "
            "over Elena. The blessed water sparkles with divine light as it touches "
            "her skin, and dark shadows begin to steam away like smoke. Elena gasps "
            "as the corrupting influence of the curse is washed from her body and "
            "soul. The water glows brighter, purifying every drop of dark magic it "
            "touches.\n\n"
            "As the last of the water drips away, Elena stands straighter, her skin "
            "glowing with a faint, pure radiance. The curse's hold on her has been "
            "greatly weakened by the purification. Now only a powerful dispelling "
            "spell remains to shatter the last remnants of the dark enchantment.[/success]"
        )

    def receive_dispel_final_cure(
        self, game_state: GameState
    ) -> str:  # game_state kept for interface consistency
        """Handle casting dispel spell on Elena as the final step to complete the cure"""
        if game_state.get_story_flag(FLAG_INNKEEPERS_DAUGHTER_COMPLETED):
            return "Elena has already been completely cured of her curse."

        if not self.elena_purified:
            return (
                "Elena needs to be purified with crystal-clear water before the "
                "curse can be dispelled. The dark magic is still too strong to "
                "break with dispelling alone."
            )

        # Complete the cure and set the quest completion flag
        game_state.set_story_flag(FLAG_INNKEEPERS_DAUGHTER_COMPLETED, True)

        # Update Elena's description to show complete healing
        self.description = (
            "A vibrant young woman who radiates health and vitality. Her eyes "
            "sparkle with life, and her complexion glows with natural beauty. "
            "She moves with grace and energy, completely free from the dark curse "
            "that once plagued her. She looks at you with deep gratitude and joy."
        )

        # Get spell name for display
        from ..spells.DispelSpell import DispelSpell
        dispel_spell = DispelSpell()
        dispel_name = dispel_spell.get_name()

        return (
            f"[success]You cast [spell_name]{dispel_name}[/spell_name] on Elena, "
            "channeling powerful counter-magic into the remaining curse fragments. "
            "The spell tears through the last dark tendrils like lightning, "
            "shattering the evil enchantment completely. Elena cries out in relief "
            "as the final traces of the curse dissolve into nothingness.\n\n"
            "She stands tall and straight, her skin glowing with perfect health. "
            "The curse that has tormented her for weeks is finally broken! Elena "
            "looks at you with tears of joy, completely free at last. The three-step "
            "healing process - greater heal, purification, and dispelling - has "
            "worked perfectly to save her life.[/success]"
        )
