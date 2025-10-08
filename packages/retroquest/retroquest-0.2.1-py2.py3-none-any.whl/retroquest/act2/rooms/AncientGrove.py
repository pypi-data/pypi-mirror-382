"""Ancient Grove room: sacred forest waypoint gating deeper heart access by quest flag."""

from ...engine.Room import Room
from ...engine.GameState import GameState
from ..items.SilverTree import SilverTree
from ..Act2StoryFlags import FLAG_WHISPERS_IN_WIND_COMPLETED

class AncientGrove(Room):
    """Sacred transitional clearing that gates progression deeper into the forest.

    Narrative Role:
        Establishes spiritual escalation; serves as liminal space between the
        outer forest approach and the Heart. Signals that ritual knowledge
        (quest completion) is required for further descent.

    Key Mechanics:
        - ``get_exits()`` hides ``south`` exit until ``FLAG_WHISPERS_IN_WIND_COMPLETED``.
        - Minimal population heightens contrast with forthcoming mystical core.

    Story Flags:
        - Reads: ``FLAG_WHISPERS_IN_WIND_COMPLETED``.
        - Sets: None (pure gate; quest logic external).

    Contents:
        - Item: ``SilverTree`` (lore anchor / potential future catalyst).
        - Characters: None (space intentionally quiet).

    Design Notes:
        Candidate for a generic ``QuestFlagExitGate`` helper if pattern repeats.
    """

    def __init__(self) -> None:
        """Initialize grove with ambient lore object and conditional south exit."""
        super().__init__(
            name="Ancient Grove",
            description=(
                "A circular clearing dominated by trees so old and massive they seem to touch "
                "the sky. Their bark bears carved symbols that predate human memory, and the "
                "air shimmers with concentrated magic. "
                "At the center grows a tree unlike any other - its silver bark gleams "
                "and its leaves whisper secrets in an ancient tongue. This is clearly a place "
                "of power and the sacred gateway to the forest's deepest mysteries."
            ),
            items=[SilverTree()],
            characters=[],
            exits={"north": "ForestEntrance", "south": "HeartOfTheForest"}
        )

    def get_exits(self, game_state: GameState) -> dict[str, str]:
        """Return exits, revealing south only after quest completion.

        Parameters:
            game_state: Global state; queried for the whisper quest completion flag.

        Returns:
            Mapping of direction strings to destination room names. Always includes
            ``north``; includes ``south`` only once the required flag is set.
        """
        base_exits = {"north": "ForestEntrance"}
        if game_state and game_state.get_story_flag(FLAG_WHISPERS_IN_WIND_COMPLETED):
            base_exits["south"] = "HeartOfTheForest"
        return base_exits
