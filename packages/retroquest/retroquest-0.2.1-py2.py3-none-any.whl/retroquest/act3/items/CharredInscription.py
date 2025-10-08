"""Charred Inscription item for Mount Ember (Act III)."""

from ...engine.Item import Item
from ...engine.GameState import GameState
from ..Act3StoryFlags import FLAG_ACT3_CHARRED_INSCRIPTION_READ


class CharredInscription(Item):
    """A charred inscription etched into cooled lava, part of the Hidden Bond story."""

    def __init__(self) -> None:
        """Initialize the charred inscription with its description."""
        super().__init__(
            name="Charred Inscription",
            description=(
                "Words burned deep into cooled lava, the letters blackened by "
                "intense heat. The inscription speaks of a ward forged in desperation, "
                "written by hands that knew time was running short."
            ),
            can_be_carried=False,
            short_name="inscription"
        )

    def examine(self, game_state: GameState) -> str:
        """Examine the inscription to read its message."""
        if not game_state.get_story_flag(FLAG_ACT3_CHARRED_INSCRIPTION_READ):
            game_state.set_story_flag(FLAG_ACT3_CHARRED_INSCRIPTION_READ, True)

        return (
            "[event]You trace the charred letters with your finger, feeling the "
            "heat that once shaped them. The inscription reads:[/event]\n\n"
            "[italic]'In fire and flame we forge the final ward. Should our son "
            "face the darkness we once served, let him know that love burns "
            "brighter than any shadow. The binding is set in three parts: "
            "courage from the depths, wisdom from the heights, and sacrifice "
            "from the heart. When united, they shall be his shield.'[/italic]\n\n"
            "[event]The words seem to pulse with warmth, as if the love that "
            "wrote them still burns in the stone.[/event]"
        )
