"""Keepsake Note item for triggering the Echoes quest (Act III)."""

from ...engine.Item import Item
from ...engine.GameState import GameState
from ..Act3StoryFlags import FLAG_ACT3_ECHOES_QUEST_STARTED


class KeepsakeNote(Item):
    """A note from Mira referencing Elior's parents and hinting at hidden truths."""

    def __init__(self) -> None:
        """Initialize the keepsake note with its description."""
        super().__init__(
            name="Keepsake Note",
            description=(
                "A small, worn piece of parchment in Mira's careful handwriting. "
                "The note seems to carry the weight of long-held secrets, and "
                "mentions fragments of truth scattered across the relic sites."
            ),
            can_be_carried=True,
            short_name="note"
        )

    def examine(self, game_state: GameState) -> str:
        """Read the note's contents."""
        if not game_state.get_story_flag(FLAG_ACT3_ECHOES_QUEST_STARTED):
            game_state.set_story_flag(FLAG_ACT3_ECHOES_QUEST_STARTED, True)

        return (
            "[event]You unfold the note carefully, reading Mira's words:[/event]\n\n"
            "[italic]'Elior, as you journey to the relic sites, keep your eyes "
            "open for traces of the past. Your parents left marks upon this "
            "world—fragments of their story that Malakar could not erase. In "
            "the depths where courage is tested, on the heights where wisdom "
            "burns, and in the shadows where sacrifice echoes, you may find "
            "the truth of how they hid you from his sight. The three testimonies "
            "will reveal what love can accomplish against the darkest power.'[/italic]\n\n"
            "[event]The note fills you with a sense of purpose beyond the "
            "immediate quest. Somewhere in each relic site, pieces of your "
            "heritage await discovery.[/event]"
        )
