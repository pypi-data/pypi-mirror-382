"""Sea-Sealed Letter item for Tidal Causeway (Act III)."""

from ...engine.GameState import GameState
from ...engine.Item import Item
from ..Act3StoryFlags import FLAG_ACT3_SEA_SEALED_LETTER_READ

class SeaSealedLetter(Item):
    """A scrap of vellum preserved by salt-crystal varnish."""

    def __init__(self) -> None:
        """Initialize the sea-sealed letter with its description."""
        super().__init__(
            name="Sea-Sealed Letter",
            short_name="letter",
            description=(
                "[event]You unfold the salt-preserved vellum carefully. The ancient "
                "ink, protected by crystalline varnish, reveals words in a familiar "
                "hand:[/event]\n\n"
                "[dialogue]'My beloved Mira, if you read this, then our fears have come "
                "to pass and Malakar has discovered our betrayal. We were his "
                "apprentices once—Lyra and I both served in his shadow, learning "
                "his dark arts. But when we saw what he planned for our unborn child, "
                "we could no longer remain silent.'[/dialogue]\n\n"
                "[dialogue]'The three relics hold the key to a ward that can hide our "
                "son from his sight. We will forge this protection with our lives if "
                "we must. Tell Elior, when he is ready, that his parents chose love "
                "over loyalty to darkness. The ward will hold until he is strong "
                "enough to face what we could not.'[/dialogue]\n\n"
                "[event]The letter is signed with two names: Lyra and Theron—your "
                "parents. Your hands tremble as you realize this testament of their "
                "defiance has waited in the depths all these years.[/event]"
            ),
            can_be_carried=True,
        )

    def examine(self, game_state: GameState) -> str:
        """Examine the letter and set the read flag."""
        game_state.set_story_flag(FLAG_ACT3_SEA_SEALED_LETTER_READ, True)
        return super().examine(game_state)

    def picked_up(self, _game_state: GameState) -> str:
        """Handle letter pickup and set story flag."""
        return (
            "[item_effect]You carefully fold the preserved fragment — a testament "
            "kept by the sea.[/item_effect]"
        )
