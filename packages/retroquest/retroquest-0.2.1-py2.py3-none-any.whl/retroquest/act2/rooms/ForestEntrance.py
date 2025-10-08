"""Forest Entrance room: dual-item gated threshold to enchanted interior."""

from ...engine.Room import Room
from ...engine.GameState import GameState
from ..Act2StoryFlags import (
    FLAG_ENHANCED_LANTERN_USED_FOREST_ENTRANCE,
    FLAG_PROTECTIVE_CHARM_USED_FOREST_ENTRANCE
)
from ..items.EnchantedAcorn import EnchantedAcorn
from ..characters.ForestSprites import ForestSprites

class ForestEntrance(Room):
    """Threshold zone requiring two preparatory item usages.

    Narrative Role:
        Establishes tension and preparation theme; ensures players activate both
        protective and illumination aids before penetrating deeper biomes.

    Key Mechanics:
        - ``get_exits()`` shows ``south`` and ``east`` only when both lantern and
          charm flags are set.

    Story Flags:
        - Reads: ``FLAG_ENHANCED_LANTERN_USED_FOREST_ENTRANCE``,
          ``FLAG_PROTECTIVE_CHARM_USED_FOREST_ENTRANCE``.
        - Sets: None (flags owned by item usage contexts).

    Contents:
        - Item: ``EnchantedAcorn``.
        - NPCs: ``ForestSprites`` (ambient observers).

    Design Notes:
        Candidate for a future ``MultiFlagExitGate`` abstraction if repetition
        appears across acts.
    """

    def __init__(self) -> None:
        """Initialize entrance with ambient item and multi-flag exit gating."""
        super().__init__(
            name="Forest Entrance",
            description=(
                "Massive trees create a natural cathedral as you enter the Enchanted Forest. "
                "Dappled sunlight filters through the dense canopy, and the path ahead "
                "disappears into green shadows. The air is alive with birds and rustling leaves, "
                "but beneath it lies an expectant silence, as if the forest itself is watching. "
                "Two paths diverge deeper: one toward an ancient grove—the sacred gateway to the "
                "forest's heart—and one toward a tranquil glade. Small motes of light dance "
                "between the trees: forest sprites watching your every move."
            ),
            items=[EnchantedAcorn()],
            characters=[ForestSprites()],
            exits={"west": "ForestTransition", "south": "AncientGrove", "east": "WhisperingGlade"}
        )

    def get_exits(self, game_state: GameState) -> dict:
        """Return exits, revealing south/east only after both preparation flags.

        Parameters:
            game_state: Global state queried for required preparation flags.

        Returns:
            Mapping of available exits; always includes ``west``; adds ``south``
            and ``east`` once both lantern and charm usage flags are set.
        """
        exits = {"west": "ForestTransition"}  # Always allow going back west
        # Only show south and east exits if both items have been used
        lantern_used = game_state.get_story_flag(FLAG_ENHANCED_LANTERN_USED_FOREST_ENTRANCE)
        charm_used = game_state.get_story_flag(FLAG_PROTECTIVE_CHARM_USED_FOREST_ENTRANCE)
        if lantern_used and charm_used:
            exits["south"] = "AncientGrove"
            exits["east"] = "WhisperingGlade"
        return exits
