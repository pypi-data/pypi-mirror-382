"""Prophetic Vision spell for Act II."""

from ...engine.Spell import Spell
from ..Act2StoryFlags import FLAG_GATHERING_STORM_COMPLETED
from ...engine.GameState import GameState

class PropheticVision(Spell):
    """Ultimate divination spell concluding Act II foresight quest progression.

    Provides a climactic vision when cast with Sir Cedric present. The first contextual
    cast completes the Gathering Storm quest and delivers an extended prophecy. Later
    casts return a shorter, reflective variant of the vision.
    """

    def __init__(self) -> None:
        super().__init__(
            name="prophetic_vision",
            description=(
                "A powerful divination spell that allows the caster to glimpse possible futures "
                "and see the threads of fate."
            ),
        )
    def cast_spell(self, game_state: GameState) -> str:
        """Cast the prophetic vision; variant depends on Cedric presence and story flags.

        When Sir Cedric is present and the gathering storm flag is unset, the first cast
        completes the Gathering Storm quest and delivers an extended prophecy.
        """
        # Check if Sir Cedric is present in the current room
        from ..characters.SirCedric import SirCedric

        cedric_present = any(
            isinstance(char, SirCedric) for char in game_state.current_room.characters
        )
        if not cedric_present:
            return (
                "[info]As you begin to cast the prophetic vision spell, you sense that the "
                "visions would be most meaningful if shared with someone who can act upon the "
                "knowledge. You should use this spell together with Sir Cedric, who has the "
                "authority and wisdom to prepare for the threats that the visions reveal.[/info]"
            )

        if not game_state.get_story_flag(FLAG_GATHERING_STORM_COMPLETED):
            # First casting - complete The Gathering Storm quest
            game_state.set_story_flag(FLAG_GATHERING_STORM_COMPLETED, True)
            return (
                "[magic]You close your eyes and reach out with your newly granted sight beyond "
                "sight. With Sir Cedric standing beside you, you share the visions as they flood "
                "your mind like fragments of a shattered mirror, each reflecting a possible "
                "future:\n\n"

                "You see shadows gathering in the north, darker than any natural darkness. "
                "Ancient evils stir in forgotten places, and you sense that Malakar's "
                "interest in Willowbrook was only the beginning of a much larger design. "
                "The scattered threads of fate show you glimpses of trials yet to come - "
                "allies who will stand with you, "
                "enemies who will test your resolve, and choices that will shape the very fabric "
                "of the world.\n\n"

                "The vision fades, but the knowledge remains. Sir Cedric's expression grows grave "
                "as he witnesses the prophetic revelations. You understand now that your journey "
                "has only just begun, and the gathering storm spoken of by Sir Cedric is far "
                "greater than anyone imagined. Together, armed with this foresight, you are "
                "better prepared for whatever challenges lie ahead.[/magic]"
            )

        return (
            "[magic]You cast the prophetic vision spell, and brief glimpses of possible futures "
            "dance before your eyes. The gift of foresight reminds you that every choice creates "
            "ripples through the tapestry of time, and wisdom lies in understanding the "
            "consequences of your actions.[/magic]"
        )
