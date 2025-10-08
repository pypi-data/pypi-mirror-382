"""The Knight's Test Quest Module.

Skill validation mini‑quest establishing martial credibility with Sir Cedric.

Trigger Conditions:
- Activated after initial audience with Sir Cedric (``FLAG_SPOKEN_TO_SIR_CEDRIC``).

Objective:
- Demonstrate combat proficiency using training equipment (flag set externally).

Completion Logic:
- Monitors ``FLAG_DEMONSTRATED_COMBAT_SKILLS`` and completes immediately once
    proof is provided, enabling downstream supply acquisition and trust narrative.
"""

from ...engine.Quest import Quest
from ...engine.GameState import GameState
from ..Act2StoryFlags import FLAG_DEMONSTRATED_COMBAT_SKILLS, FLAG_SPOKEN_TO_SIR_CEDRIC

class TheKnightsTestQuest(Quest):
    """Quest to prove combat skills to Sir Cedric."""
    def __init__(self) -> None:
        super().__init__(
            name="The Knight's Test",
            description=(
                "Sir Cedric wants to see proof of your combat abilities before "
                "trusting you with important responsibilities. Demonstrate your "
                "martial skills with a training sword."
            ),
            completion=(
                "You have successfully demonstrated your combat skills to Sir "
                "Cedric. He now trusts your abilities!"
            )
        )

    def check_trigger(self, game_state: GameState) -> bool:
        return game_state.get_story_flag(FLAG_SPOKEN_TO_SIR_CEDRIC)

    def check_completion(self, game_state: GameState) -> bool:
        if game_state.get_story_flag(FLAG_DEMONSTRATED_COMBAT_SKILLS):
            return True
        return False
