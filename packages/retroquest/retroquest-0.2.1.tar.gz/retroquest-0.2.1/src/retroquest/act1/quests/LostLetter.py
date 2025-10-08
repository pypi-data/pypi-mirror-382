from ...engine.Quest import Quest
from ...engine.GameState import GameState
from ..Act1StoryFlags import (
    FLAG_FOUND_LOST_LETTER,
    FLAG_ASKED_GRANDMOTHER_ABOUT_LETTER
)
from typing import Any

# The Lost Letter Quest - Steps to Completion
# 1. The player searches the floorboard in Elior's Cottage and finds the faded letter.
# 2. The game sets FLAG_FOUND_LOST_LETTER to indicate the letter has been found.
# 3. The letter item is given to the player and can be examined.
# 4. The player talks to Grandmother about the letter, triggering special dialogue.
# 5. The game sets FLAG_ASKED_GRANDMOTHER_ABOUT_LETTER after the conversation.
# 6. Optionally, a clue or follow-up quest is unlocked by this letter.
# 7. The quest is now complete and connects to the main story thread.

class LostLetterQuest(Quest):
    def __init__(self) -> None:
        super().__init__(
            name="The Lost Letter",
            description=(
                "While cleaning Elior’s cottage, you discover a faded letter hidden beneath a floorboard. "
                "The letter is addressed to your grandmother and mentions a secret your parents were investigating before they vanished."
            ),
            completion="You have uncovered a clue about your parents' fate. The letter hints at a mystery that will unfold in future acts."
        )

    def check_trigger(self, game_state: GameState) -> bool:
        # Triggered when the player searches the floorboard in Elior's Cottage
        return game_state.get_story_flag(FLAG_FOUND_LOST_LETTER)

    def check_completion(self, game_state: GameState) -> bool:
        # Completed when the player talks to Grandmother about the letter
        return game_state.get_story_flag(FLAG_ASKED_GRANDMOTHER_ABOUT_LETTER)
