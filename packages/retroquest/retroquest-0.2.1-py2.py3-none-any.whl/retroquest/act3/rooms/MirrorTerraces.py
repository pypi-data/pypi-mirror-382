"""Module defining the MirrorTerraces room in Act 3."""
from ...engine import Room
from ..items import MirrorMount
from ..items.CharredInscription import CharredInscription
from ..Act3StoryFlags import (
    FLAG_ACT3_MIRRORS_OF_EMBER_LIGHT_STARTED,
    FLAG_ACT3_MIRRORS_OF_EMBER_LIGHT_COMPLETED,
)
from ...engine.GameState import GameState

class MirrorTerraces(Room):
    """The Mirror Terraces: stepped platforms with sockets for polished mirrors."""
    def __init__(self) -> None:
        """Initialize Mirror Terraces with description and exits."""
        super().__init__(
            name="Mirror Terraces",
            description=(
                "Stepped platforms rise in concentric benches, each ring studded with "
                "sockets for polished mirrors and brass mounts. Channels are neatly "
                "etched into the stone to carry and focus light up the slope; stray "
                "rays catch on alignment wedges and glint like cold flame. The air "
                "humms faintly with residual heat, and dusted ash settles on "
                "worktables where scholars and attendants file, polish, and fit "
                "mirror segments. A Terrace Warden watches the assembly points, "
                "checking the angles and murmuring measurements — the place smells "
                "of warm metal, singed cloth, and the mineral tang of cooling slag."
            ),
            # A prepared mount is present at the terraces for the player to use
            items=[MirrorMount(), CharredInscription()],
            characters=[],
            exits={
                "south": "EmberGallery",
                "east": "FumarolePassages",
                "west": "ObsidianOutcrops"
            },
        )

    def on_enter(self, game_state) -> None:
        """Room hook called when the player arrives; mark mirrors quest started."""
        # Set the story flag so the MirrorsOfEmberlight quest can trigger
        game_state.set_story_flag(FLAG_ACT3_MIRRORS_OF_EMBER_LIGHT_STARTED, True)

    def get_exits(self, game_state: GameState) -> dict[str, str]:
        """Return exits; hide east exit until mirrors quest is completed."""
        # Start with the base static exits and remove the east path unless
        # the Mirrors of Emberlight quest has been completed.
        exits = dict(self.exits)
        if not game_state.get_story_flag(
            FLAG_ACT3_MIRRORS_OF_EMBER_LIGHT_COMPLETED
        ):
            exits.pop("east", None)
        return exits
