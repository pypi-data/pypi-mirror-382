"""Forest Transition room: flag-gated boundary into enchanted interior."""

from ...engine.Room import Room
from ...engine.GameState import GameState
from ..Act2StoryFlags import FLAG_HERMITS_WARNING_COMPLETED
from ..characters.ForestHermit import ForestHermit
from ..items.StandingStones import StandingStones

class ForestTransition(Room):
    """Boundary zone requiring hermit's warning resolution.

    Narrative Role:
        Marks psychological shift from civilized path to mystical domain while
        reinforcing preparedness (survival kit / warning acceptance).

    Key Mechanics:
        - ``get_exits()`` hides ``east`` until ``FLAG_HERMITS_WARNING_COMPLETED``.

    Story Flags:
        - Reads: ``FLAG_HERMITS_WARNING_COMPLETED``.
        - Sets: None (flag authored elsewhere).

    Contents:
        - NPC: ``ForestHermit``.
        - Item: ``StandingStones`` (lore anchor).

    Design Notes:
        Simple flag gate; could use a future ``GateOnFlag`` mixin.
    """

    def __init__(self) -> None:
        """Initialize transition with hermit NPC and conditional east exit."""
        super().__init__(
            name="Forest Transition",
            description=(
                "The boundary between the civilized mountain paths and the wild Enchanted Forest. "
                "Ancient standing stones mark the threshold, carved with protective runes that "
                "pulse with faint magic. The air grows thicker and you sense ancient power "
                "awakening. Beyond lies a realm where normal rules may not apply. "
                "A robed figure sits peacefully among the stones."
            ),
            items=[StandingStones()],
            characters=[ForestHermit()],
            exits={"west": "MountainPath", "east": "ForestEntrance"}
        )

    def get_exits(self, game_state: GameState) -> dict:
        """Return exits; hide east until hermit's warning flag is set.

        Parameters:
            game_state: Global state used to read hermit's warning completion.

        Returns:
            Mapping of exits including ``west`` and conditionally ``east`` when
            preparedness has been acknowledged.
        """
        exits = super().get_exits(game_state).copy()
        # Remove east exit if survival kit hasn't been used
        if not game_state.get_story_flag(FLAG_HERMITS_WARNING_COMPLETED):
            exits.pop("east", None)
        return exits
