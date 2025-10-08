"""Faded photograph item used to reveal a hint and set a story flag."""

from ...engine.Item import Item
from ...engine.GameState import GameState
from ..Act1StoryFlags import FLAG_READ_PHOTO_MESSAGE

class FadedPhotograph(Item):
    """
    Personal relic tying Elior to family backstory and exploration hints.
    """

    def __init__(self) -> None:
        """Initialize the Faded Photograph item with name, description, and carry status."""
        super().__init__(
            name="faded photograph",
            short_name="photograph",
            description=(
                "An old, faded photograph. The image is barely visible, but you can make out "
                "two adults and a child. On the back, in your mother's handwriting, is a "
                "cryptic message: [dialogue]Seek the truth where the river bends.[/dialogue]"
            ),
            can_be_carried=True
        )

    def examine(self, game_state: GameState) -> str:
        """Set the story flag when the photograph is examined."""
        game_state.set_story_flag(FLAG_READ_PHOTO_MESSAGE, True)
        return super().examine(game_state)
