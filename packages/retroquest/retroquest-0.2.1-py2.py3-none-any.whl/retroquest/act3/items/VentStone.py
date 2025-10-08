"""Vent Stone item used in Fumarole Passages for calibration."""

from ...engine.Item import Item
from ...engine.GameState import GameState


class VentStone(Item):
    """A carved stone used to tune the timing of the fumarole vents."""

    def __init__(self) -> None:
        super().__init__(
            name="vent stone",
            description=(
                "A smooth, heat-tempered stone carved with grooves that fit into "
                "the fumarole fittings. Several are needed to calibrate the vents."
            ),
            short_name="vent stone",
            can_be_carried=True,
        )

    def use(self, game_state: GameState) -> str:  # type: ignore[override]
        """Use the vent stone to attempt a calibration when in the passages."""
        # Find current room name and act accordingly
        room = game_state.current_room
        if room is None or room.name != "Fumarole Passages":
            return (
                f"[failure]You can't use the [item_name]{self.get_name()}[/item_name] "
                "usefully here.[/failure]"
            )

        # Delegate to room helper if present
        return room.calibrate_with_stone(game_state, self)
