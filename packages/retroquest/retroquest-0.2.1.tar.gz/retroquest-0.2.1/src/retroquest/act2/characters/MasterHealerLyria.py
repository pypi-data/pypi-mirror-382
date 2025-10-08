"""Master Healer Lyria NPC — mentor for the Healer's Apprentice quest."""

from ...engine.Character import Character
from ...engine.GameState import GameState
from ..Act2StoryFlags import (
    FLAG_HEALERS_APPRENTICE_ACCEPTED,
    FLAG_HEALERS_APPRENTICE_COMPLETED,
)

class MasterHealerLyria(Character):
    """NPC mentor who teaches advanced healing and handles the apprenticeship quest."""

    def __init__(self) -> None:
        super().__init__(
            name="Master Healer Lyria",
            description=(
                "A wise and nurturing healer with graying hair and gentle eyes that seem to "
                "see right through to your magical potential. She wears simple robes adorned "
                "with healing herbs, and her hands are steady from years of tending to the "
                "sick and wounded. There's an aura of calm competence about her that inspires "
                "confidence in her abilities."
            ),
        )

    def talk_to(self, game_state: GameState) -> str:
        """Handle dialogue based on inventory and apprenticeship story flags."""

        # Check if player has healing herbs or crystal focus to give
        has_healing_herbs = game_state.has_item("Healing Herbs")
        has_crystal_focus = game_state.has_item("Crystal Focus")
        if not game_state.get_story_flag(FLAG_HEALERS_APPRENTICE_ACCEPTED):
            if has_crystal_focus:
                return (
                    "[success][character_name]Master Healer Lyria[/character_name] recognizes "
                    "your magical potential and notices the [item_name]Crystal Focus[/item_name] "
                    "you carry. 'That crystal focus! It's exactly what I need to help my "
                    "patients who are on the brink of death. If you're willing to give it to "
                    "me, I can use it to save lives and teach you advanced healing magic in "
                    "return.' Her eyes show both desperation and hope.[/success]"
                )
            elif has_healing_herbs:
                # First set the accepted flag to trigger the quest
                return (
                    "[success][character_name]Master Healer Lyria[/character_name] recognizes "
                    "your magical potential and says: 'I can see you have a natural gift for "
                    "healing magic. If you're willing to give me those [item_name]Healing "
                    "Herbs[/item_name] as proof of your commitment to the healing arts, I will "
                    "teach you advanced techniques.' She gestures to her collection of healing "
                    "supplies. '[/success]"
                )
            else:
                return (
                    "[character_name]Master Healer Lyria[/character_name]: Welcome to my house of "
                    "healing. I can sense magical potential in you, but I desperately need "
                    "help. I have patients on the brink of death who need more powerful "
                    "healing than I can provide alone. If you could bring me a "
                    "[item_name]Crystal Focus[/item_name] to amplify my magic, or some "
                    "[item_name]Healing Herbs[/item_name] to show your commitment to healing, I "
                    "will teach you advanced techniques."
                )
        elif game_state.get_story_flag(FLAG_HEALERS_APPRENTICE_COMPLETED):
            return (
                "[character_name]Master Healer Lyria[/character_name]: It's wonderful to see "
                "how far you've come with your healing abilities. You're truly a master of "
                "the healing arts now. Continue to use your gifts to help those in need."
            )
        else:
            return (
                "[character_name]Master Healer Lyria[/character_name]: I'm looking forward to "
                "teaching you advanced healing techniques. Please bring me a "
                "[item_name]Crystal Focus[/item_name] to help my dying patients, or some "
                "[item_name]Healing Herbs[/item_name] to show your commitment, so we can begin "
                "your training."
            )

    def give_item(self, game_state: GameState, item_object) -> str:
        """Handle giving items to Master Healer Lyria."""
        from ..items.CrystalFocus import CrystalFocus
        from ..items.HealingHerbs import HealingHerbs  # Import here to avoid circular imports

        if isinstance(item_object, CrystalFocus):
            # Remove Crystal Focus from inventory as it's given to Lyria
            game_state.remove_item_from_inventory("Crystal Focus")
            # Complete the quest and learn greater_heal spell
            game_state.set_story_flag(FLAG_HEALERS_APPRENTICE_COMPLETED, True)
            # Learn greater_heal spell
            from ..spells.GreaterHealSpell import GreaterHealSpell
            game_state.learn_spell(GreaterHealSpell())
            return (
                "[success][character_name]Master Healer Lyria[/character_name] accepts the "
                "[item_name]Crystal Focus[/item_name] with great relief. 'This is exactly what "
                "I needed! With this crystal focus, I can amplify my healing magic to treat "
                "patients on the brink of death.' She immediately begins using it to help her "
                "critically injured patients. 'Through your compassion and this magical aid, "
                "you've shown yourself ready for advanced training.' She teaches you the "
                "[spell_name]greater_heal[/spell_name] spell! 'You've truly earned the title of "
                "healer.'[/success]\n\n"
                "[quest_complete]Quest Complete: The Healer's Apprentice[/quest_complete]"
            )
        elif isinstance(item_object, HealingHerbs):
            # Check if apprentice quest is accepted but not completed
            game_state.set_story_flag(FLAG_HEALERS_APPRENTICE_ACCEPTED, True)
            # Remove healing herbs from inventory as they're given to Lyria
            game_state.remove_item_from_inventory("Healing Herbs")
            return (
                "[success][character_name]Master Healer Lyria[/character_name] accepts the "
                "[item_name]Healing Herbs[/item_name] with approval. 'Excellent! Your "
                "commitment shows you're ready to learn.' Through careful instruction, you "
                "master the [spell_name]greater_heal[/spell_name] spell! 'Use this knowledge "
                "wisely, young healer. You've successfully completed your apprenticeship.'"
                "[/success]"
            )
        else:
            # Default response for other items
            return (
                "[character_name]Master Healer Lyria[/character_name] seems to be too busy to "
                "receive any gifts from you at the moment."
            )
