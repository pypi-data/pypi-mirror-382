"""Echoes of the Hidden Bond storytelling quest class."""

from ...engine.GameState import GameState
from ...engine.Quest import Quest
from ..Act3StoryFlags import (
    FLAG_ACT3_ECHOES_QUEST_STARTED,
    FLAG_ACT3_SEA_SEALED_LETTER_READ,
    FLAG_ACT3_CHARRED_INSCRIPTION_READ,
    FLAG_ACT3_DRAGONS_MEMORY_RECEIVED,
    FLAG_ACT3_ECHOES_QUEST_COMPLETED,
)


class EchoesOfTheHiddenBondQuest(Quest):
    """Storytelling quest to discover the truth about Elior's parents and their ward."""

    def __init__(self) -> None:
        """Initialize the Echoes of the Hidden Bond quest with description."""
        super().__init__(
            name="Echoes of the Hidden Bond",
            description=(
                "Your parents once walked these same paths in their own desperate "
                "search for the three relics. As you face the trials they faced, "
                "you may discover traces of their passage—fragments of their story "
                "left behind in the depths, heights, and shadows where they sought "
                "to forge a protection that would outlast their own lives.\n\n"
                "○ In the depths where courage is tested, echoes of the past linger.\n"
                "○ On the heights where wisdom burns, their words may still echo.\n"
                "○ In the shadows where secrets are kept, their choices may still resonate.\n"
            ),
            completion=(
                "The three testimonies have revealed the truth: Elior's parents, "
                "once apprentices to Malakar, defied their master to protect their "
                "son. Through sacrifice and ancient wards, they hid Elior from "
                "Malakar's sight, ensuring he would grow strong enough to face "
                "the darkness when the time came."
            ),
        )
        self._discoveries = {}

    def is_main(self) -> bool:
        """Return False as this is a storytelling side quest."""
        return False

    def check_trigger(self, game_state: GameState) -> bool:
        """Check if quest should trigger when Mira gives the keepsake note."""
        # For now, trigger immediately when Act III main quest starts
        # In a full implementation, this would trigger when Mira gives a keepsake note
        return game_state.get_story_flag(FLAG_ACT3_ECHOES_QUEST_STARTED)

    def check_update(self, game_state: GameState) -> bool:
        """Check if quest description should update based on discoveries."""
        updated = False

        # Build dynamic description based on discoveries
        base_desc = (
            "[dim]Your parents once walked these same paths in their own desperate "
            "search for the three relics. As you face the trials they faced, "
            "you may discover traces of their passage.[/dim]"
        )

        discoveries = []

        # Check Sea-Sealed Letter
        if game_state.get_story_flag(FLAG_ACT3_SEA_SEALED_LETTER_READ):
            if not self._discoveries.get('sea_letter'):
                self._discoveries['sea_letter'] = True
                updated = True
            discoveries.append(
                "✓ Depths of the Sunken Ruins: You found traces of your parents' "
                "first passage, revealing their past as Malakar's apprentices and "
                "the moment they chose to defy him."
            )
        else:
            discoveries.append(
                "[dim]○ In the depths where courage is tested, echoes of the past linger.[/dim]"
            )

        # Check Charred Inscription
        if game_state.get_story_flag(FLAG_ACT3_CHARRED_INSCRIPTION_READ):
            if not self._discoveries.get('charred_inscription'):
                self._discoveries['charred_inscription'] = True
                updated = True
            discoveries.append(
                "✓ Heights of Mount Ember: You discovered your parents' words "
                "burned into stone, describing the protective ward they forged "
                "through fire and sacrifice."
            )
        else:
            discoveries.append(
                "[dim]○ On the heights where wisdom burns, their words may still echo.[/dim]"
            )

        # Check Dragon's Memory
        if game_state.get_story_flag(FLAG_ACT3_DRAGONS_MEMORY_RECEIVED):
            if not self._discoveries.get('dragons_memory'):
                self._discoveries['dragons_memory'] = True
                updated = True
            discoveries.append(
                "✓ Shadows of the Caverns: The ancient dragon shared memories "
                "of your parents' final act, naming them and the completion of "
                "their ward."
            )
        else:
            discoveries.append(
                "[dim]○ In the shadows where sacrifice dwells, ancient memories await.[/dim]"
            )

        # Update description with current progress
        self.description = base_desc + "\n\n" + "\n".join(discoveries)

        return updated

    def check_completion(self, game_state: GameState) -> bool:
        """Check if quest is completed when all three testimonies are found."""
        all_found = (
            game_state.get_story_flag(FLAG_ACT3_SEA_SEALED_LETTER_READ) and
            game_state.get_story_flag(FLAG_ACT3_CHARRED_INSCRIPTION_READ) and
            game_state.get_story_flag(FLAG_ACT3_DRAGONS_MEMORY_RECEIVED)
        )

        if all_found and not game_state.get_story_flag(FLAG_ACT3_ECHOES_QUEST_COMPLETED):
            game_state.set_story_flag(FLAG_ACT3_ECHOES_QUEST_COMPLETED, True)
            return True

        return False
