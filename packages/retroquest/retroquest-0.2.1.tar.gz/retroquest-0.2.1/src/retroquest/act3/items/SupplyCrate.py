"""Locked supply crate in Tool Cache for Miners' Rescue quest."""
from ...engine import GameState, Item
from .ReinforcedBraces import ReinforcedBraces
from .SupportStraps import SupportStraps
from .WedgeBlocks import WedgeBlocks
from .MinersKey import MinersKey

class SupplyCrate(Item):
    """A locked crate containing braces, straps, and wedge blocks."""
    def __init__(self) -> None:
        super().__init__(
            name="Supply Crate",
            description=(
                "A heavy wooden crate reinforced with iron bands. It is locked with a large iron "
                "padlock. The label reads: 'Rescue Supplies — For Emergency Use Only.'"
            ),
            short_name="crate",
            can_be_carried=False,
        )
        self.locked = True
        self.opened = False
        self.contents = [ReinforcedBraces(), SupportStraps(), WedgeBlocks()]

    def examine(self, _game_state: GameState) -> str:
        if self.locked:
            return (
                "[event]You examine the crate. The padlock is sturdy and rusted, but the keyhole "
                "looks intact. The crate is labeled for rescue supplies.[/event]"
            )
        elif not self.opened:
            return (
                "[event]The crate is unlocked but still closed. You could try to open it.[/event]"
            )
        else:
            return (
                "[event]The crate stands open, its contents mostly removed.[/event]"
            )

    def open(self, game_state: GameState) -> str:
        if self.locked:
            return (
                "[failure]The crate is locked. You'll need a key to open it.[/failure]"
            )
        if self.opened:
            return (
                "[event]The crate is already open. Only packing straw remains inside.[/event]"
            )
        # Add contents to the room
        for item in self.contents:
            game_state.current_room.add_item(item)
        self.opened = True
        return (
            "[event]You open the crate. Inside are heavy iron braces, strong hemp straps, and "
            "tapered wooden wedge blocks—just what you need to rescue the trapped miners![/event]"
        )

    def use_with(self, game_state: GameState, other_item: Item) -> str:
        if self.locked and isinstance(other_item, MinersKey):
            self.locked = False
            # Remove the key from inventory by name
            game_state.remove_item_from_inventory(other_item.get_name(), 1)
            return (
                "[event]You fit the miner's key into the padlock. With a click, the lock opens. "
                "The crate is now unlocked. The key is left twisted and useless, and you "
                "discard it.[/event]"
            )
        return super().use_with(game_state, other_item)
