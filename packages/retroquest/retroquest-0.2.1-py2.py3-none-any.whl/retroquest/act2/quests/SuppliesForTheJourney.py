"""SuppliesForTheJourneyQuest: Gather essential gear for the forest expedition."""

from ...engine.Quest import Quest
from ...engine.GameState import GameState
from ..Act2StoryFlags import FLAG_DEMONSTRATED_COMBAT_SKILLS, FLAG_SUPPLIES_QUEST_COMPLETED

class SuppliesForTheJourneyQuest(Quest):
    """Quest to gather essential gear for the forest expedition."""
    def __init__(self) -> None:
        super().__init__(
            name="Supplies for the Journey",
            description=(
                "Sir Cedric mentioned the need for proper equipment for forest "
                "expeditions. Gather essential supplies from the Market District."
            ),
            completion=(
                "You have gathered all the essential supplies for forest exploration. "
                "The journey supplies quest is complete!"
            )
        )

    def check_trigger(self, game_state: GameState) -> bool:
        return game_state.get_story_flag(FLAG_DEMONSTRATED_COMBAT_SKILLS)

    def check_completion(self, game_state: GameState) -> bool:
        from ..items.ForestSurvivalKit import ForestSurvivalKit
        from ..items.EnhancedLantern import EnhancedLantern
        from ..items.QualityRope import QualityRope
        if not self.is_completed_flag:
            has_survival_kit = any(
                isinstance(item, ForestSurvivalKit) for item in game_state.inventory
            )
            has_lantern = any(
                isinstance(item, EnhancedLantern) for item in game_state.inventory
            )
            has_rope = any(
                isinstance(item, QualityRope) for item in game_state.inventory
            )
            if has_survival_kit and has_lantern and has_rope:
                self.is_completed_flag = True
                game_state.set_story_flag(FLAG_SUPPLIES_QUEST_COMPLETED, True)
                return True
        return False
