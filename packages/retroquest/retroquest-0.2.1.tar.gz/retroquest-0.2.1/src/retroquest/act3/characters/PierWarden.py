"""PierWarden character for the Collapsed Pier in Act 3."""
from ...engine.Character import Character
from ...engine.GameState import GameState
from ..Act3StoryFlags import (
    FLAG_ACT3_TIDEWARD_SIGILS_COMPLETED,
    FLAG_ACT3_LANTERNS_OF_THE_DEEPS_LIT,
)


class PierWarden(Character):
    """A watchful warden of the pier who comments on local happenings.

    The Pier Warden does not provide items or change quests; their dialogue
    varies depending on whether the Tideward Sigils and Lanterns quests are
    completed/activated.
    """

    def __init__(self) -> None:
        """Initialize the Pier Warden with a short description."""
        super().__init__(
            name="Pier Warden",
            description=(
                "A salt-crusted figure who tends the ruined jetty and watches "
                "for those who come and go."
            ),
        )

    def talk_to(self, game_state: GameState) -> str:
        """Return context-sensitive dialogue about the pier and nearby ruins."""
        sigils = game_state.get_story_flag(FLAG_ACT3_TIDEWARD_SIGILS_COMPLETED)
        lanterns = game_state.get_story_flag(FLAG_ACT3_LANTERNS_OF_THE_DEEPS_LIT)

        if not sigils:
            return (
                "[dialogue]'I'd mind the high stones if I were you. The markers "
                "along the shore keep strange fragments—take heed and look for "
                "moon-signs before the tide turns.'[/dialogue]"
            )

        if sigils and not lanterns:
            return (
                "[dialogue]'You've done right by the pillars. There's a fused locker "
                "down in the vaults; I tried a key once but it stuck. Magic will "
                "loosen it, or so the old songs say.'[/dialogue]"
            )

        return (
            "[dialogue]'With the sigils attuned and the lanterns lit, the way grows "
            "steadier. Those who brave the sanctum find the tide less quick to "
            "swallow their steps.'[/dialogue]"
        )
