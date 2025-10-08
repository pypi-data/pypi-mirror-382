"""The Ancient Library Quest Module.

Discovers and explores the hidden subterranean archive beneath Greendale.

Trigger Conditions:
- Activated when the player uncovers the secret passage and accepts entry, setting
    ``FLAG_ANCIENT_LIBRARY_ACCEPTED``.

Core Objectives (implicit):
1. Gain access to the spectral librarian / arcane stacks.
2. Acquire the Crystal Focus item (enhances later magical interactions/mechanics).
3. Learn the ``dispel`` spell from recovered tomes / spectral tutoring.

Completion Logic:
- Quest completes when both the ``dispel`` spell is known AND the player possesses
    the ``Crystal Focus`` item. These two conditions gate Act II main quest narrative
    advancement (knowledge & lineage revelation).

Lore / Narrative Impact:
- Reveals prophetic material concerning the Chosen One lineage and establishes
    the player's heritage link. Provides early mid‑act power escalation while keeping
    forest progression balanced.
"""

from ...engine.Quest import Quest
from ...engine.GameState import GameState
from ..Act2StoryFlags import (
        FLAG_ANCIENT_LIBRARY_ACCEPTED
)

class TheAncientLibraryQuest(Quest):
    """Quest to discover and explore the hidden ancient library beneath Greendale."""
    def __init__(self) -> None:
        super().__init__(
            name="The Ancient Library",
            description=(
                "You've discovered a hidden passage beneath Greendale containing an "
                "ancient library of magical texts and lore. You should explore its "
                "depths and uncover the secrets within."
            ),
            completion=(
                "You have successfully gained access to the ancient library's "
                "knowledge! You've learned the dispel spell, discovered important "
                "information about your family heritage, and received a Crystal "
                "Focus to enhance your magical abilities. The library's secrets "
                "have revealed crucial insights about the Chosen One prophecy "
                "and your destiny."
            )
        )

    def check_trigger(self, game_state: GameState) -> bool:
        # Quest triggers when player discovers the secret passage
        return game_state.get_story_flag(FLAG_ANCIENT_LIBRARY_ACCEPTED)

    def check_completion(self, game_state: GameState) -> bool:
        # Quest completes when player has:
        # 1. Learned the dispel spell
        # 2. Gained the Crystal Focus
        return (game_state.has_spell("dispel") and
                game_state.has_item("Crystal Focus"))
