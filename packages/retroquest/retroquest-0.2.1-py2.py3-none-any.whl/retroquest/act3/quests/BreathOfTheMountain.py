"""BreathOfTheMountain: Quest for calibrating vents and crafting a heat ward on Mount Ember."""
from ...engine import GameState, Quest
from ..Act3StoryFlags import (
    FLAG_ACT3_BREATH_OF_THE_MOUNTAIN_STARTED,
    FLAG_ACT3_BREATH_OF_THE_MOUNTAIN_COMPLETED,
)

class BreathOfTheMountain(Quest):
    """Quest: Calibrate vent stones and craft a heat ward to cross the Fumarole Passages."""
    def __init__(self) -> None:
        super().__init__(
            name="Breath of the Mountain",
            description=(
                "The Fumarole Passages exhale waves of heat and steam, blocking the way forward. "
                "Find a way to cross the shifting vents and reach the heights to the south."
            ),
            completion=(
                "With patience and ingenuity, Elior crafts a heat ward from ash-fern and cooled "
                "slag, then calibrates the mountain's ancient vents to breathe in a steady, safe "
                "rhythm. "
                "The searing passages yield, opening the way to the Phoenix's crater and the next "
                "trial of wisdom."
            ),
        )

    def check_trigger(self, game_state: GameState) -> None:
        """Mark quest as started."""
        return game_state.get_story_flag(FLAG_ACT3_BREATH_OF_THE_MOUNTAIN_STARTED)

    def check_completion(self, game_state: GameState) -> bool:
        """Quest is complete when the heat ward is applied and vents are calibrated."""
        return game_state.get_story_flag(FLAG_ACT3_BREATH_OF_THE_MOUNTAIN_COMPLETED)
