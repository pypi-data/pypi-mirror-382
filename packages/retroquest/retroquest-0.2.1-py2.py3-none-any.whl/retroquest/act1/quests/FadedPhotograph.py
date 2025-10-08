from ...engine.Quest import Quest
from ...engine.GameState import GameState
from ..Act1StoryFlags import FLAG_FOUND_PHOTO, FLAG_READ_PHOTO_MESSAGE, FLAG_TALKED_TO_GRANDMOTHER_ABOUT_PHOTO
from typing import Any

# The Faded Photograph Quest - Steps to Completion
# 1. The player finds the photograph in Elior's cottage (e.g., searching the attic or a hidden drawer), which sets FLAG_FOUND_PHOTO.
# 2. The photograph item is given to the player and can be examined.
# 3. The player examines/reads the back of the photograph, setting FLAG_READ_PHOTO_MESSAGE.
# 4. The photograph contains a hidden message or puzzle (required for quest completion).
# 5. The player talks to Grandmother about the photograph, triggering special dialogue.
# 6. After the dialogue, FLAG_TALKED_TO_GRANDMOTHER_ABOUT_PHOTO is set.

class FadedPhotographQuest(Quest):
    def __init__(self) -> None:
        super().__init__(
            name="The Faded Photograph",
            description=(
                "Your grandmother is often seen gazing at an old photograph. If you ask her about it, she shares a memory of your parents and gives you the photo, which has a cryptic message on the back."
            ),
            completion="You have received the photograph and discovered a cryptic message, deepening the mystery of your parents' fate."
        )

    def check_trigger(self, game_state: GameState) -> bool:
        # Triggered when the player finds the photograph
        return game_state.get_story_flag(FLAG_FOUND_PHOTO)

    def check_completion(self, game_state: GameState) -> bool:
        # Completed when the player finishes the dialogue with Grandmother about the photograph
        return game_state.get_story_flag(FLAG_TALKED_TO_GRANDMOTHER_ABOUT_PHOTO)
