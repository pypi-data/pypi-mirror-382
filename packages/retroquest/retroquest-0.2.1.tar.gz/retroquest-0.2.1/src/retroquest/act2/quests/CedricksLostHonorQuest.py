"""CedricksLostHonorQuest: Quest to vindicate Sir Cedric by locating exonerating documents."""

from ...engine.Quest import Quest
from ...engine.GameState import GameState
from ..Act2StoryFlags import (
    FLAG_CEDRIKS_HONOR_ACCEPTED,
    FLAG_CEDRIKS_HONOR_COMPLETED,
    FLAG_READ_SQUIRES_DIARY,
    FLAG_EXAMINED_SECRET_DOCUMENTS,
)

class CedricksLostHonorQuest(Quest):
    """Quest to vindicate Sir Cedric by locating exonerating documents."""
    def __init__(self) -> None:
        super().__init__(
            name="Cedric's Lost Honor",
            description=(
                "Sir Cedric has been living under a cloud of disgrace due to false "
                "accusations of cowardice. Investigate the rumors about his past and "
                "find evidence to clear his name."
            ),
            completion=(
                "You have found the secret documents that prove Sir Cedric's innocence "
                "and restored his honor! The knight's reputation has been cleared, and "
                "he is grateful for your efforts to uncover the truth."
            )
        )
        self.squires_info_added = False
        self.documents_examined = False

    def check_trigger(self, game_state: GameState) -> bool:
        """Quest is triggered when the Training Master is talked to."""
        return game_state.get_story_flag(FLAG_CEDRIKS_HONOR_ACCEPTED)

    def check_completion(self, game_state: GameState) -> bool:
        """Quest is completed when the secret documents have been used to clear Cedric's name."""
        return game_state.get_story_flag(FLAG_CEDRIKS_HONOR_COMPLETED)

    def check_update(self, game_state: GameState) -> bool:
        """Refresh the quest description when new squire or document information exists."""
        updated = False
        self.description = (
            "Sir Cedric has been living under a cloud of disgrace due to false "
            "accusations of cowardice. Investigate the rumors about his past and "
            "find evidence to clear his name."
        )
        new_desc = ""
        # First update: when diary is read
        if game_state.get_story_flag(FLAG_READ_SQUIRES_DIARY):
            # Update the description to include information from the squires
            self.description = '[dim]' + self.description + '[/dim]'
            new_desc = (
                "\n\nAccording to the squires and their diary, secret documents from "
                "Heavensforth that would clear his name went missing when a merchant "
                "caravan was lost. Find these documents to restore his honor."
            )
            if not self.squires_info_added:
                updated = True
            self.squires_info_added = True

        # Second update: when secret documents are examined
        if game_state.get_story_flag(FLAG_EXAMINED_SECRET_DOCUMENTS):
            # Update the description to include information about finding the evidence
            self.description += '[dim]' + new_desc + '[/dim]'
            new_desc = (
                "\n\nYou have found the secret documents! The evidence clearly proves "
                "Sir Cedric's innocence - he was protecting civilians and following "
                "direct orders during the Battle of Thornfield Pass. Now you need "
                "to present this evidence to restore his honor."
            )
            if not self.documents_examined:
                updated = True
            self.documents_examined = True
        self.description += new_desc

        return updated
