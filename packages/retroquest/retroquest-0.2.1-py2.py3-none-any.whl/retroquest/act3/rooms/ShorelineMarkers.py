"""Shoreline Markers room for Act 3."""

from ...engine.GameState import GameState
from ...engine.Room import Room
from ..items import MoonRuneShards, Steles, PolishedShell
from ..Act3StoryFlags import FLAG_ACT3_TIDEWARD_SIGILS_STARTED


class ShorelineMarkers(Room):
    """Shore location with weathered steles containing moon rune shards."""


    def __init__(self) -> None:
        """Initialize Shoreline Markers with steles and exits."""
        super().__init__(
            name="Shoreline Markers",
            description=(
                "The shore here is quiet and cold. Weathered steles rise from the sand, "
                "their worn faces full of shallow marks. Salt and time have smudged "
                "many lines, but faint moon sigils still show when the tide drops. "
                "Loose pale flakes sit in the grooves; they shimmer like old stars. "
                "When the moon is high, the stones seem to hum with a slow, patient "
                "voice—an old magic tied to the sea."
            ),
            items=[Steles(), PolishedShell()],
            characters=[],
            exits={"south": "TidalCauseway", "east": "OuterWards"},
        )
        # Track whether runes have been revealed here at least once.
        self.runes_revealed = False

    def search(self, game_state: GameState, _target: str = None) -> str:
        """Search the steles to find Moon Rune shards for ward construction."""
        # If runes have already been revealed at this location, return an
        # idempotent message even if the shards are not currently present.
        if self.runes_revealed:
            return (
                "[event]You comb the surf-slick stones again. pale shards gleam in "
                "the cracks, but you've already gathered what you need.[/event]"
            )
        # Reveal runes
        self.items.append(MoonRuneShards())
        # Remember that the runes were revealed here so future searches do not
        # recreate them even if they are later removed.
        self.runes_revealed = True
        # Mark that the Tideward Sigils side quest has been started by reaching
        # the shoreline markers. This flag is used to trigger the quest in the
        # quest system.
        if not game_state.get_story_flag(FLAG_ACT3_TIDEWARD_SIGILS_STARTED):
            game_state.set_story_flag(FLAG_ACT3_TIDEWARD_SIGILS_STARTED, True)
        return (
            "[event]You brush aside kelp and barnacle crusts. A cluster of pale moon "
            "shards comes free—etched with curved lines that seem to hum when the "
            "moon leans toward the sea. They feel keyed to the tide, as if the "
            "lunar pull listens to these marks.[/event]"
        )
