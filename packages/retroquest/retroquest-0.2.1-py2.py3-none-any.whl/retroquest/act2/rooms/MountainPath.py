"""Mountain Path room for Act II."""

from ...engine.Room import Room
from ...engine.GameState import GameState
from ..items.MountainFlower import MountainFlower
from ..items.WalkingStick import WalkingStick
from ..items.CampSite import CampSite
from ..characters.MountainHermit import MountainHermit
from ..Act2StoryFlags import FLAG_SUPPLIES_QUEST_COMPLETED

class MountainPath(Room):
    """Preparation corridor linking settlements (Act II).

    Narrative Role:
        Bridges Act I context and Greendale while signaling the shift toward deeper wilderness.

    Key Mechanics:
        `get_exits()` withholds the eastern forest transition until the supplies quest flag is set.

    Story Flags:
        Reads: `FLAG_SUPPLIES_QUEST_COMPLETED` to expose the forest route.
        Sets: None; completion handled externally.

    Contents:
        Items: Mountain Flower, Walking Stick, Camp Site (rest / flavor potential). NPC: Mountain
        Hermit who can provide guidance or quests.

    Design Notes:
        Early gating underscores readiness. Could later layer travel events (weather, encounters)
        344for
        pacing variety.
    """
    def __init__(self) -> None:
        super().__init__(
            name="Mountain Path",
            description=(
                "A winding trail climbs through rocky terrain between Willowbrook and Greendale. "
                "Sturdy trees cast intermittent shade and the path remains well tended despite "
                "its remoteness. Glimpses of both settlements appear at overlooks, offering "
                "reflective pauses. A small "
                "camp site used by travelers rests just off the main trail."
            ),
            items=[MountainFlower(), WalkingStick(), CampSite()],
            characters=[MountainHermit()],
            exits={"north": "GreendaleGates", "east": "ForestTransition"}
        )

    def get_exits(self, game_state: GameState) -> dict[str, str]:
        """Return exits, hiding forest route until supplies quest completion.

        The eastern exit (forest transition) is removed when the supplies quest prerequisite has not
        yet been satisfied.
        """
        exits_dict = super().get_exits(game_state).copy()
        if not game_state.get_story_flag(FLAG_SUPPLIES_QUEST_COMPLETED):
            exits_dict.pop("east", None)
        return exits_dict
