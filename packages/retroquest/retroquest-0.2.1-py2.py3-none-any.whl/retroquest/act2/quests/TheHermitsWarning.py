"""The Hermit's Warning Quest Module.

Provides early atmospheric foreshadowing and a soft tutorialized gating step
before deep exploration of the Enchanted Forest.

Trigger Conditions:
- Activated when the player accepts counsel from the forest hermit (sets
    ``FLAG_HERMITS_WARNING_ACCEPTED``) after initial wilderness approach.

Purpose:
- Delivers lore about shifting paths / spirits.
- Grants/acknowledges a protective charm item externally.
- Encourages acquiring proper survival supplies first.

Completion Logic:
- Marks complete when preparatory condition is satisfied (external sequence sets
    ``FLAG_HERMITS_WARNING_COMPLETED``). Quest itself is passive monitor.

Narrative Impact:
- Signals escalation from civilized outskirts to magical wilderness.
"""

from ...engine.Quest import Quest
from ...engine.GameState import GameState
from ..Act2StoryFlags import FLAG_HERMITS_WARNING_COMPLETED, FLAG_HERMITS_WARNING_ACCEPTED

class TheHermitsWarningQuest(Quest):
    """Quest to heed the hermit's warning and prepare for the Enchanted Forest."""
    def __init__(self) -> None:
        super().__init__(
            name="The Hermit's Warning",
            description=(
                "A mysterious forest hermit has warned you about the dangers of the "
                "Enchanted Forest. They spoke of ancient guardians, dark spirits, "
                "and ever-shifting paths that trap the unwary. The hermit has given "
                "you a protective charm to help safeguard your journey through the "
                "magical wilderness, but you need to prepare yourself before venturing "
                "further into the Enchanted Forest."
            ),
            completion=(
                "You have heeded the hermit's warning and are now prepared to face "
                "the challenges of the Enchanted Forest."
            )
        )

    def check_trigger(self, game_state: GameState) -> bool:
        """Check if the quest should be activated when the hermit's warning is accepted."""
        return game_state.get_story_flag(FLAG_HERMITS_WARNING_ACCEPTED)

    def check_completion(self, game_state: GameState) -> bool:
        """Check if the quest should be completed when the survival kit is used."""
        return game_state.get_story_flag(FLAG_HERMITS_WARNING_COMPLETED)
