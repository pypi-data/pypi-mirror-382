"""Castle Approach room: ceremonial avenue gating access to the castle courtyard."""

from ...engine.Room import Room
from ...engine.GameState import GameState
from ..characters.Herald import Herald
from ..characters.CastleGuardCaptain import CastleGuardCaptain

class CastleApproach(Room):
    """Processional path enforcing protocol before courtyard access.

    Narrative Role:
        Establishes hierarchy and formality between the civic spaces and the
        noble inner grounds. Functions as a soft gate prior to martial and
        political hubs (Courtyard, Great Hall).

    Key Mechanics:
        - ``get_exits()`` removes ``west`` until ``enable_castle_courtyard()`` is
          invoked (after presenting entry pass to the Herald).
        - Exit pruning performed on a copy to avoid mutating base definition.

    Story Flags:
        - None directly; uses a local boolean for lightweight state.

    Contents:
        - NPCs: ``Herald`` (protocol), ``CastleGuardCaptain`` (authority).
        - Items: None (focus kept on social gating).

    Design Notes:
        Local boolean could migrate to a story flag if other rooms later need
        awareness of courtyard access state.
    """

    def __init__(self) -> None:
        """Initialize approach with protocol NPCs and gated courtyard exit."""
        super().__init__(
            name="Castle Approach",
            description=(
                "A wide avenue lined with statues of Greendale's heroes leads to an impressive "
                "castle of white stone. Tall spires reach toward the sky, and colorful banners "
                "snap in the wind. "
                "Guards in ceremonial armor patrol the approach, their presence both welcoming "
                "and imposing. This is clearly where power resides in Greendale."
            ),
            items=[],
            characters=[Herald(), CastleGuardCaptain()],
            exits={"south": "MainSquare", "west": "CastleCourtyard"}
        )
        self.castle_courtyard_enabled = False

    def get_exits(self, game_state: GameState) -> dict:
        """Return exits; withhold west exit until protocol fulfilled.

        Parameters:
            game_state: Unused; accepted for interface parity.

        Returns:
            Mapping of available exits; ``west`` omitted until courtyard enabled.
        """
        exits = super().get_exits(game_state).copy()
        # Remove west exit to CastleCourtyard until entry pass has been shown to herald
        if not self.castle_courtyard_enabled and "west" in exits:
            del exits["west"]
        return exits

    def enable_castle_courtyard(self) -> None:
        """Enable west exit to the castle courtyard after entry pass validation."""
        self.castle_courtyard_enabled = True
