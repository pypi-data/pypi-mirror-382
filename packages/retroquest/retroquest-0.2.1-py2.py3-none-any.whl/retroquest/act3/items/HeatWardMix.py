"""Heat Ward Mix item (ash-fern + cooled slag) used to prepare vents."""

from ...engine.Item import Item
from ...engine.GameState import GameState


class HeatWardMix(Item):
    """A simple mixture used to protect from the intense fumarole heat."""

    def __init__(self) -> None:
        super().__init__(
            name="heat-ward mix",
            description=(
                "A coarse paste of ash-fern and cooled slag prepared to seal and "
                "stabilize vent stones against the mountain's heat. Use it at the "
                "fumaroles after calibration."
            ),
            short_name="heat-ward mix",
            can_be_carried=True,
        )

    def use_with(self, game_state: GameState, other_item: Item) -> str:  # type: ignore[override]
        """Allow applying the mix directly to the fumarole room helper via an item.

        If used with the FumarolePassages room object (when the room is exposed as an
        item-like target) delegate to room's application helper. Otherwise, instruct.
        """
        # If used with a room-like object that has apply_heat_ward, call it
        if hasattr(other_item, 'apply_heat_ward'):
            return other_item.apply_heat_ward(game_state, self)

        return (
            f"[failure]You can't use the [item_name]{self.get_name()}[/item_name] "
            f"with the [item_name]{other_item.get_name()}[/item_name].[/failure]"
        )

    def use(self, game_state: GameState) -> str:  # type: ignore[override]
        """Use the mix in the current room if applicable (Fumarole Passages)."""
        room = game_state.current_room
        if room is None or room.name != "Fumarole Passages":
            return (
                f"[failure]You can't use the [item_name]{self.get_name()}[/item_name] "
                "usefully here.[/failure]"
            )

        if hasattr(room, 'apply_heat_ward'):
            return room.apply_heat_ward(game_state, self)

        return (
            f"[failure]The [item_name]{self.get_name()}[/item_name] has no obvious "
            "place to use here.[/failure]"
        )
