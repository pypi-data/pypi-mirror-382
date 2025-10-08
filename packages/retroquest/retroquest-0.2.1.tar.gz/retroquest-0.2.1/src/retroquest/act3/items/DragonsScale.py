"""DragonsScale item for the Dragon's Hall in Act 3."""
from ...engine.Item import Item
from ...engine.GameState import GameState
from ..Act3StoryFlags import FLAG_ACT3_DRAGONS_SCALE_ACQUIRED


class DragonsScale(Item):
    """The Dragon's Scale relic representing Selflessness."""

    def __init__(self) -> None:
        """Initialize DragonsScale as a precious relic."""
        super().__init__(
            name="Dragon's Scale",
            description=(
                "A scale from the ancient dragon, dark as midnight yet shot "
                "through with veins of deep gold. It pulses with a slow, steady "
                "warmth and weighs heavy with the promise of protection and "
                "sacrifice."
            ),
            can_be_carried=True,
            short_name="scale"
        )

    def picked_up(self, game_state: GameState) -> str:
        """Handle taking the Dragon's Scale relic with prerequisite checks."""
        # Requirements met, allow pickup
        game_state.set_story_flag(FLAG_ACT3_DRAGONS_SCALE_ACQUIRED, True)
        return (
            "[event]The dragon's scale settles into your hands with surprising "
            "weight. You feel the burden of responsibility and the strength that "
            "comes from selfless action. The relic pulses warmly against your "
            "palm.[/event]"
        )
