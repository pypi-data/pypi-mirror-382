(
    "Squires (Act II)\n\n"
    "Role:\n"
    "    Informational cluster NPC that supplies rumor-level context for Sir Cedric's "
    "alleged disgrace while subtly nudging the player toward investigating "
    "contradictory evidence.\n\n"
    "Interaction Logic:\n"
    "    - Only engages fully after Cedric's honor quest accepted "
    "(FLAG_CEDRIKS_HONOR_ACCEPTED).\n"
    "    - First qualifying interaction sets FLAG_SQUIRES_TALKED_TO (progress metric "
    "for quest chains / integration tests).\n\n"
    "Story Flags:\n"
    "    - Reads: FLAG_CEDRIKS_HONOR_ACCEPTED\n"
    "    - Sets: FLAG_SQUIRES_TALKED_TO\n\n"
    "Narrative Impact:\n"
    "    - Provides diegetic motivation to locate the diary and pursue exoneration "
    "path.\n"
    "    - Reinforces honor + mentorship themes central to Act II.\n\n"
    "Design Notes:\n"
    "    - Kept stateless after first flag set to avoid repetitive flag toggling.\n"
    "    - Dialogue intentionally dense with leads; ensures players can't miss Cedric "
    "arc foundations.\n"
)

from ...engine.Character import Character
from ...engine.GameState import GameState
from ..Act2StoryFlags import FLAG_SQUIRES_TALKED_TO, FLAG_CEDRIKS_HONOR_ACCEPTED

class Squires(Character):
    """Group NPC representing trainee knights offering rumors and quest leads."""
    def __init__(self) -> None:
        super().__init__(
            name="squires",
            description=(
                "Young men and women training to become knights under the guidance of the "
                "Training Master and Sir Cedric. They practice sword work and horsemanship with "
                "determination, though they occasionally pause to whisper among themselves about "
                "castle affairs and their mentors' reputations."
            ),
        )

    def talk_to(self, game_state: GameState) -> str:
        # Check if Cedric's Lost Honor quest has been accepted
        if not game_state.get_story_flag(FLAG_CEDRIKS_HONOR_ACCEPTED):
            # Squires are too busy to talk if quest hasn't been accepted
            return (
                "[character_name]Squires[/character_name]: *The squires are deeply "
                "focused on their training exercises, practicing sword forms and "
                "footwork with intense concentration. They seem too busy and "
                "focused to engage in conversation right now.* 'Sorry, we can't "
                "talk - the Training Master expects us to perfect these techniques "
                "before the day is over.'"
            )
        # Set flag that squires have been talked to (only if quest is accepted)
        game_state.set_story_flag(FLAG_SQUIRES_TALKED_TO, True)
        return (
            "[character_name]Squires[/character_name]: *The young squires lower their voices and "
            "glance around nervously.* We're not supposed to talk about it, but we've "
            "heard the older knights whispering about Sir Cedric's disgrace. They say he "
            "abandoned his post during a crucial battle and that soldiers died because of "
            "his cowardice. *One squire looks particularly troubled.* But it doesn't make "
            "sense - Sir Cedric has always taught us about honor and duty. He would never "
            "abandon his men. *Another squire nods.* We found an old diary under the stone "
            "benches that tells a different story. Maybe you should take a look at it."
        )
