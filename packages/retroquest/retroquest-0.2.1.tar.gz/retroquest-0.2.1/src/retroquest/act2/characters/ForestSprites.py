"""Forest Sprites NPC definition.

Role:
    Playful threshold guardians for deeper forest zones. They initiate the
    "Forest Guardian's Riddles" quest that tests player wisdom / respect.

Key Behavior:
    - First interaction sets ``FLAG_FOREST_GUARDIANS_RIDDLES_OFFERED``.
    - Subsequent dialogues provide gentle directional hints (Ancient Grove,
      Whispering Glade) without duplicating quest logic.

Design Notes:
    Maintains minimal state via ``riddles_quest_given`` to avoid re-triggering.
"""

from ...engine.Character import Character
from ...engine.GameState import GameState
from ..Act2StoryFlags import FLAG_FOREST_GUARDIANS_RIDDLES_OFFERED

class ForestSprites(Character):
    """Playful threshold guardians who offer the Forest Guardian's Riddles quest."""

    def __init__(self) -> None:
        super().__init__(
            name="forest sprites",
            description=(
                "Tiny, luminescent beings that dance through the air like living sparks "
                "of light. These mischievous but benevolent forest spirits appear as "
                "glowing wisps with delicate, translucent wings. They speak in chiming "
                "voices that sound like wind chimes in a gentle breeze, and their "
                "presence fills the air with a sense of ancient magic and playful "
                "wisdom."
            ),
        )
        self.riddles_quest_given = False

    def talk_to(self, game_state: GameState) -> str:
        name = self.get_name()
        event_msg = (
            "[event]You approach the [character_name]"
            + name
            + "[/character_name].[/event]"
        )
        if not self.riddles_quest_given:
            # Give the Forest Guardian's Riddles quest
            self.riddles_quest_given = True
            game_state.set_story_flag(FLAG_FOREST_GUARDIANS_RIDDLES_OFFERED, True)
            return (
                event_msg
                + "\n"
                + (
                    f"[dialogue]The [character_name]{name}[/character_name] flutter around you "
                    "in a sparkling dance, their chiming voices creating a melodic chorus. "
                    "'Welcome, traveler, to the threshold of the deep forest! We are the "
                )

                + (
                    "guardians of the ancient paths, keepers of riddles and secrets old.'"
                    "[/dialogue]\n\n"
                )

                + (
                    "[dialogue]'If you would venture deeper into our sacred realm, you must "
                    "prove your wisdom and understanding of forest ways. Seek the Ancient "
                    "Grove where the silver-barked tree holds court, and beyond that, the "
                    "Whispering Glade where the water spirits dwell. Answer their riddles, "
                    "and you shall earn the right to walk freely among the deepest mysteries "
                    "of our forest.'[/dialogue]\n\n"
                )

                + (
                    "[dialogue]'But beware - the forest tests not just knowledge, but heart "
                    "and spirit as well. Show respect to all living things, and the "
                    "ancient powers will guide your steps. Show arrogance or harm, and "
                    "the very trees will lead you astray until you learn better ways.'"
                    "[/dialogue]"
                )
            )
        else:
            # Subsequent conversations provide guidance
            return (
                event_msg
                + "\n"
                + (
                    f"[dialogue]The [character_name]{name}[/character_name] continue their "
                    "eternal dance, chiming softly. 'The ancient ones await your wisdom, "
                )

                + (
                    "traveler. Remember - the forest rewards those who listen with their "
                    "hearts as well as their minds. The silver tree and the water spirits "
                    "hold the keys to deeper understanding.'[/dialogue]"
                )
            )

    def examine(self, _game_state: GameState) -> str:
        name = self.get_name()
        return (
            f"[event]You study the [character_name]{name}[/character_name] more closely. "
            f"{self.description} They seem to be composed of pure forest magic, ancient "
            f"guardians who have watched over these woods since the earliest days. "
            f"Their dance follows patterns that mirror the movement of leaves in the "
            f"wind and the flow of streams through the forest.[/event]"
        )
