"""The Innkeeper's Daughter Quest Module.

Focused curative sequence combining staged restorative magic applications.

Trigger Conditions:
- Begins when player learns of Elena's curse (``FLAG_KNOWS_ELENA_CURSE``).

Intended Cure Sequence (narrative order):
1. Apply advanced healing (``greater_heal``) to stabilize.
2. Use purified / crystal water to cleanse lingering spiritual residue.
3. Cast ``dispel`` to break the underlying dark enchantment.

Completion Logic:
- External interaction flow sets ``FLAG_INNKEEPERS_DAUGHTER_COMPLETED`` which this
    quest monitors via ``check_completion``.

Narrative Impact:
- Demonstrates compound spell synergy and validates mastery gained from other
    Act II progression quests (Healer's Apprentice + Ancient Library).
"""

from ...engine.Quest import Quest
from ...engine.GameState import GameState
from ..Act2StoryFlags import (
        FLAG_KNOWS_ELENA_CURSE,
        FLAG_INNKEEPERS_DAUGHTER_COMPLETED
)

class TheInnkeepersDaughterQuest(Quest):
    """Quest to save Elena, the innkeeper's daughter, from a dark curse."""
    def __init__(self) -> None:
        super().__init__(
            name="The Innkeeper's Daughter",
            description=(
                "Elena, the barmaid at The Silver Stag Inn, has been cursed by a "
                "dark wizard. Use your magical abilities to break the curse and save "
                "her life."
            ),
            completion=(
                "Through careful magical healing, you successfully broke Elena's "
                "curse. You first strengthened her with a greater heal spell, then "
                "purified her spirit with crystal-clear water, and finally used a "
                "dispel spell to shatter the dark magic completely. Elena is now "
                "free from the wizard's curse!"
            ),
        )

    def check_trigger(self, game_state: GameState) -> bool:
        return game_state.get_story_flag(FLAG_KNOWS_ELENA_CURSE)

    def check_completion(self, game_state: GameState) -> bool:
        return game_state.get_story_flag(FLAG_INNKEEPERS_DAUGHTER_COMPLETED)
