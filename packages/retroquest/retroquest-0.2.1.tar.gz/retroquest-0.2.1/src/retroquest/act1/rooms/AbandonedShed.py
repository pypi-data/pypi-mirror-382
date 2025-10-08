"""Abandoned Shed room: staged unlock and layered search progression."""

from ...engine.Room import Room
from ..items.BrokenShovel import BrokenShovel
from ..items.MysteriousBox import MysteriousBox
from ..items.FishingRod import FishingRod  # Import FishingRod
from ..items.Magnet import Magnet  # Import Magnet
from ..items.ShedDoor import ShedDoor
from ...engine.GameState import GameState

class AbandonedShed(Room):
    """Staged micro-dungeon style container with unlock and gated search phases.

    Narrative Role:
        Early contained progression space teaching player that environment states change
        across interactions (unlock -> search -> reward tiers).

    Key Mechanics:
        - ``unlock()``: Toggles locked state; injects ``MysteriousBox`` and ``BrokenShovel``.
        - ``search()``: First successful (post-unlock) search adds ``FishingRod`` and ``Magnet``.
        - Internal booleans ``locked`` / ``room_searched`` control state; no story flags yet.

    Story Flags:
        None presently. Could elevate lock/search completions to flags if cross-room
        reactions are later required.

    Contents:
        - Initial: ``ShedDoor`` (implicit barrier object).
        - On unlock: ``MysteriousBox``, ``BrokenShovel``.
        - First search: ``FishingRod``, ``Magnet``.
        - Characters: None.

    Design Notes:
        Demonstrates reusable staged revelation pattern. Future abstraction could be a
        ``LockableLootRoom`` base capturing common sequencing logic. Narrative strings
        intentionally inline (localization not yet scoped).
    """
    def __init__(self) -> None:
        """Initialize the Abandoned Shed room and its initial locked/search state."""
        super().__init__(
            name="Abandoned Shed",
            description=(
                "A rickety shed leans precariously at the edge of Willowbrook, its weathered "
                "boards creaking in the wind. Rusty tools and broken crates are scattered "
                "about, and a thick layer of dust covers everything. Shadows gather in the "
                "corners, and the air smells of old earth and forgotten secrets. Something "
                "about the place feels both forlorn and mysteriously inviting."
            ),
            items=[ShedDoor()], # Items are added dynamically
            characters=[],
            exits={"north": "VillageWell", "south": "OldMill"}
        )
        self.locked = True  # The shed starts locked
        self.room_searched = False

    def unlock(self) -> str:
        """Unlock the shed, add unlock items, and return a descriptive message."""
        if not self.locked:
            return "The shed is already unlocked."
        self.locked = False
        self.add_item(MysteriousBox())
        self.add_item(BrokenShovel())
        return (
            "The old wooden door creaks open with a groan, revealing the dusty interior "
            "of the Abandoned Shed. A [item_name]Mysterious Box[/item_name] sits on a rickety "
            "table, and a [item_name]Broken Shovel[/item_name] leans against a cobweb-covered "
            "wall."
        )

    def search(self, _game_state: GameState, _target: str = None) -> str:
        """Search the shed; if first post-unlock search, add loot and return message."""
        if self.locked:
            return (
                "You take a look around the shed. Nothing! The [item_name]Shed Door[/item_name] "
                "is locked so you can't search inside."
            )

        items_found_messages = []
        if not self.room_searched:
            self.add_item(FishingRod())
            self.room_searched = True
            items_found_messages.append("a discarded [item_name]Fishing Rod[/item_name]")
            self.add_item(Magnet())
            items_found_messages.append("a small [item_name]Magnet[/item_name]")

        if items_found_messages:
            return (
                "You rummage through the clutter of rusty tools and broken crates. Tucked away in "
                f"dusty corners, you find {', and '.join(items_found_messages)}!"
            )
        return (
            "You search around the shed again, but find nothing else of interest among the "
            "clutter."
        )
