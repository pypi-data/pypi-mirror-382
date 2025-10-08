"""ShedDoor item representing a locked shed entrance unlocked by a key."""

from ...engine.GameState import GameState
from ...engine.Item import Item


class ShedDoor(Item):
    """Locked shed door that can be unlocked with a `Key` item."""

    def __init__(self) -> None:
        super().__init__(
            name="shed door",
            description=(
                "It's a sturdy wooden [item_name]door[/item_name], locked tight. "
                "There's a keyhole visible."
            ),
            short_name="door",
        )
        self.locked = True

    def use_with(self, game_state: GameState, other_item: Item) -> str:
        """Use a `Key` on the door to unlock it (consumes the key) or return failures."""
        from .Key import Key
        if isinstance(other_item, Key):
            if self.locked:
                key_name = other_item.get_name()
                door_name = self.get_name()
                game_state.remove_item_from_inventory(key_name)
                self.locked = False
                self.description = (
                    "The [item_name]" + door_name + "[/item_name] is unlocked and "
                    "slightly ajar."
                )
                game_state.current_room.unlock()
                return (
                    "[event]The [item_name]"
                    + key_name
                    + "[/item_name] turns in the lock! The [item_name]"
                    + door_name
                    + "[/item_name] creaks open.[/event]\n"
                    "You can see a few interesting things inside."
                )
            return (
                "[failure]The [item_name]"
                + self.get_name()
                + "[/item_name] is already unlocked.[/failure]"
            )
        if other_item:
            return (
                "[failure]You can't use the [item_name]"
                + other_item.get_name()
                + "[/item_name] on the [item_name]shed door[/item_name].[/failure]"
            )
