"""Whispers in the Wind Quest Module.

Spiritual communion quest emphasizing harmony with elemental / woodland spirits.

Trigger Conditions:
- Offered after the Ancient Tree Spirit invites deeper communion (flag
    ``FLAG_WHISPERS_IN_WIND_OFFERED``).

Objectives (implicit):
- Locate and engage water nymph spirits in the Whispering Glade.
- Solve their riddles / perform respectful interaction sequence.
- Return sanctified gifts to the Ancient Tree Spirit.

Completion Logic:
- Completes when ``FLAG_WHISPERS_IN_WIND_COMPLETED`` is set externally; quest
    awards experience via overridden ``complete`` method and sets internal
    completion flag to prevent duplication.

Narrative Impact:
- Reinforces player's trust relationship with nature and unlocks / foreshadows
    broader forest faction alignment.
"""

from ...engine.Quest import Quest
from ...engine.GameState import GameState
from ..Act2StoryFlags import (
        FLAG_WHISPERS_IN_WIND_OFFERED,
        FLAG_WHISPERS_IN_WIND_COMPLETED
)

class WhispersInTheWind(Quest):
    """Quest to commune with water nymphs and earn the Ancient Tree Spirit's trust."""
    def __init__(self) -> None:
        super().__init__(
            name="Whispers in the Wind",
            description=(
                "The Ancient Tree Spirit has sensed mystical beings hidden within the "
                "forest's depths. Gentle whispers carry on the wind, speaking of "
                "ancient wisdom and forgotten lore. To prove yourself worthy of the "
                "forest's trust, you must seek out these hidden spirits in the "
                "Whispering Glade and demonstrate your understanding of nature's "
                "mysteries."
            ),
            completion=(
                "You have communed with the Water Nymphs in the Whispering Glade, "
                "solved their ancient riddles, and earned their sacred gifts. By "
                "returning these blessed items to the Ancient Tree Spirit, you have "
                "proven yourself a true friend to the woodland spirits and earned "
                "the forest's trust."
            )
        )

    def check_trigger(self, game_state: GameState) -> bool:
        """Check if this quest should be activated."""
        return game_state.get_story_flag(FLAG_WHISPERS_IN_WIND_OFFERED)

    def check_completion(self, game_state: GameState) -> bool:
        """Check if the quest can be completed based on story flags."""
        return (
            game_state.get_story_flag(FLAG_WHISPERS_IN_WIND_COMPLETED)
            and not self.is_completed_flag
        )

    def complete(self, game_state: GameState) -> str:
        """Complete the quest and give rewards."""
        if not self.is_completed_flag:
            self.is_completed_flag = True

            # Add experience
            if hasattr(game_state, 'add_experience'):
                game_state.add_experience(self.experience_reward)
                exp_msg = f" You gain {self.experience_reward} experience!"
            else:
                exp_msg = ""
            return f"[quest_complete]Quest Complete: {self.name}[/quest_complete]{exp_msg}"
        return self.completion
