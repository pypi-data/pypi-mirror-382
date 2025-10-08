"""The Forest Guardian's Riddles Quest Module.

Wisdom / knowledge trial emphasizing respect for natural lore and establishes
rapport with forest guardian entities.

Trigger Conditions:
- Offered upon acceptance of the guardians' intellectual challenge
    (``FLAG_FOREST_GUARDIANS_RIDDLES_OFFERED``).

Objectives:
- Scripted list stored in ``self.objectives`` for UI/status rendering.
- Early objectives implicitly satisfied by visiting key biomes; later ones by
    solving riddle interactions (external logic sets completion flag).

Completion Logic:
- Monitors ``FLAG_FOREST_GUARDIANS_RIDDLES_COMPLETED``; on first completion
    awards experience and prints formatted quest completion string.

Design Notes:
- Provides mid‑act experience bump and thematically pairs with Whispers quest to
    represent dual aspects of forest acceptance: empathy (spirits) and intellect
    (guardians' wisdom).
"""

from ...engine.Quest import Quest
from ...engine.GameState import GameState
from ..Act2StoryFlags import (
        FLAG_FOREST_GUARDIANS_RIDDLES_OFFERED,
        FLAG_FOREST_GUARDIANS_RIDDLES_COMPLETED
)

class TheForestGuardiansRiddles(Quest):
    """Quest to solve the riddles posed by the forest guardians."""
    def __init__(self) -> None:
        super().__init__(
            name="The Forest Guardian's Riddles",
            description=(
                "The forest sprites have challenged you to prove your wisdom by solving the "
                "riddles of the forest guardians. You must journey to the Ancient Grove and "
                "beyond to the Whispering Glade, where ancient spirits will test "
                "your understanding of forest ways and natural wisdom."
            ),
            completion=(
                "You have successfully solved the riddles of the forest guardians, "
                "proving your wisdom and respect for the natural world. The "
                "forest spirits acknowledge your understanding."
            )
        )
        self.objectives = [
            "Speak with the Ancient Tree Spirit in the Ancient Grove",
            "Journey to the Whispering Glade and meet the water spirits",
            "Solve the riddles posed by the forest guardians",
            "Prove your wisdom and respect for the natural world"
        ]
        self.experience_reward = 200

    def check_trigger(self, game_state: GameState) -> bool:
        """Check if this quest should be activated."""
        return game_state.get_story_flag(FLAG_FOREST_GUARDIANS_RIDDLES_OFFERED)

    def check_completion(self, game_state: GameState) -> bool:
        """Check if the quest can be completed based on story flags."""
        return (
            game_state.get_story_flag(FLAG_FOREST_GUARDIANS_RIDDLES_COMPLETED)
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

    def get_status(self) -> str:
        """Return the current status of the quest."""
        if self.is_completed_flag:
            return f"[quest_status_complete]{self.name} - COMPLETED[/quest_status_complete]"
        else:
            status = f"[quest_status_active]{self.name} - IN PROGRESS[/quest_status_active]\n"
            for i, objective in enumerate(self.objectives):
                if i < 2:  # First two objectives are typically completed by visiting the locations
                    status += f"  ✓ {objective}\n"
                else:
                    status += f"  • {objective}\n"
            return status
