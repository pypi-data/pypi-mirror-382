"""The Healer's Apprentice Quest Module.

Advances the player's healing magic progression through mentorship with Master
Healer Lyria.

Trigger Conditions:
- Activated when apprenticeship is accepted (``FLAG_HEALERS_APPRENTICE_ACCEPTED``)
    after presenting prerequisite healing materials (e.g., herbs) in dialogue.

Learning Objective:
- Guides the acquisition of the advanced ``greater_heal`` spell via narrative
    training beats (actual flag set externally, this quest just monitors).

Completion Logic:
- Finishes when training sequence sets ``FLAG_HEALERS_APPRENTICE_COMPLETED``.

Narrative Impact:
- Expands player's supportive role identity; synergizes with future purification
    and protective spell mechanics in later acts.
"""

from ...engine.Quest import Quest
from ...engine.GameState import GameState
from ..Act2StoryFlags import (
        FLAG_HEALERS_APPRENTICE_ACCEPTED,
        FLAG_HEALERS_APPRENTICE_COMPLETED
)

class TheHealersApprenticeQuest(Quest):
    """Quest to become Master Healer Lyria's apprentice and learn greater_heal."""
    def __init__(self) -> None:
        super().__init__(
            name="The Healer's Apprentice",
            description=(
                "Master Healer Lyria has recognized your magical potential and offered "
                "to teach you advanced healing techniques. Learn from her wisdom and "
                "master the greater_heal spell."
            ),
            completion=(
                "You have successfully completed your apprenticeship with Master "
                "Healer Lyria! You've learned the greater_heal spell through her "
                "advanced training. Your understanding of healing magic has grown "
                "significantly."
            )
        )

    def check_trigger(self, game_state: GameState) -> bool:
        # Quest triggers when player talks to Lyria with Healing Herbs
        return game_state.get_story_flag(FLAG_HEALERS_APPRENTICE_ACCEPTED)

    def check_completion(self, game_state: GameState) -> bool:
        # Quest completes when player has learned greater_heal spell and received training
        return game_state.get_story_flag(FLAG_HEALERS_APPRENTICE_COMPLETED)
