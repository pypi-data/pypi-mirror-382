"""Ravine: Steep ravine environmental hazard used in a rescue sequence."""

from typing import TYPE_CHECKING
from ...engine.Item import Item

if TYPE_CHECKING:
    from ...engine.Character import Character
    from ...engine.GameState import GameState

class Ravine(Item):
    """A steep ravine discovered through forest speech.
    This geographic feature cannot be carried.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ravine",
            description=(
                "A steep, rocky ravine that cuts deep into the forest floor. The walls "
                "are too treacherous to climb safely without proper equipment."
            ),
            can_be_carried=False,  # This item cannot be picked up
        )

    def examine(self, _game_state: 'GameState') -> str:
        return (
            "Looking down into the ravine, you can see the remnants of a merchant caravan "
            "trapped at the bottom. The wooden wagon wheels are visible among the rocks, "
            "and you can hear faint voices calling for help. The walls are steep and "
            "dangerous - you'll need rope or other climbing equipment to safely reach the "
            "bottom and see what is there."
        )

    def use_with(self, game_state: 'GameState', other_item) -> str:
        """Handle using the ravine with other items. Delegates to Quality Rope if applicable."""
        from .QualityRope import QualityRope  # Import here to avoid circular imports
        if isinstance(other_item, QualityRope):
            # Delegate to the Quality Rope's use_with method, passing ravine as the target
            return other_item.use_with(game_state, self)
        else:
            return f"You can't use the ravine with {other_item.get_name()}."
