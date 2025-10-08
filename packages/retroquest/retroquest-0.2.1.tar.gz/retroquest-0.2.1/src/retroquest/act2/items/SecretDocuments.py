"""SecretDocuments: evidence item used to prove Sir Cedric's innocence."""

from typing import TYPE_CHECKING
from ...engine.Item import Item
from ..Act2StoryFlags import FLAG_READ_SQUIRES_DIARY, FLAG_EXAMINED_SECRET_DOCUMENTS

if TYPE_CHECKING:
    from ...engine.GameState import GameState

class SecretDocuments(Item):
    """Secret documents containing evidence that proves Sir Cedric's innocence."""

    def __init__(self) -> None:
        super().__init__(
            name="secret documents",
            description=(
                "A sealed envelope containing important legal documents and testimonies. "
                "The papers inside appear to be evidence related to a past court case."
            ),
        )

    def examine(self, game_state: 'GameState') -> str:
        if not game_state.get_story_flag(FLAG_READ_SQUIRES_DIARY):
            return (
                "You examine the sealed documents carefully. They appear to be official legal "
                "papers and testimonies from some kind of court case or military tribunal, but "
                "without more context about what you're looking for, you can't make sense of "
                "their significance. The names and details mentioned don't mean anything to "
                "you at the moment."
            )

        # Set flag that the secret documents have been examined after reading the diary
        game_state.set_story_flag(FLAG_EXAMINED_SECRET_DOCUMENTS, True)

        return (
            "The documents contain sworn testimonies and legal evidence proving that Sir "
            "Cedric was falsely accused of cowardice during a past battle. The papers show "
            "he was actually protecting civilians and following direct orders from his "
            "commanding officer. This evidence would completely clear his name and restore "
            "his honor."
        )
