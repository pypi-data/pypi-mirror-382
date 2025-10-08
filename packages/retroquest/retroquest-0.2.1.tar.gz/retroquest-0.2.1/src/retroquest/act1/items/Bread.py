
"""Edible lure item used to coax chickens into dropping a hidden key."""
from ...engine.GameState import GameState
from .Chicken import Chicken
from ...engine.Item import Item
from .Key import Key


class Bread(Item):
    """
    Edible lure item used to coax chickens into dropping a hidden key.
    """

    def __init__(self) -> None:
        """Initialize the Bread item with name, description, and carry status."""
        super().__init__(
            name="bread",
            description=(
                "A small loaf of fresh, crusty bread. It smells delicious and could restore a "
                "bit of energy."
            ),
            can_be_carried=True
        )

    def use_with(self, game_state: GameState, other_item: Item) -> str:
        """Use bread with chickens to reveal a key, otherwise fail."""
        if isinstance(other_item, Chicken):
            # Remove bread from inventory
            game_state.remove_item_from_inventory(self.name)
            # Add key to the room
            game_state.current_room.add_item(Key())
            return (
                "[event]You offer the [item_name]bread[/item_name] to the "
                "[character_name]chickens[/character_name].[/event]\n"
                "They peck at it excitedly, and in the commotion, something shiny falls "
                "from a rafter. It's a [item_name]small key[/item_name]!"
            )
        else:
            return (
                f"[failure]You can't use the [item_name]bread[/item_name] with the "
                f"[item_name]{other_item.get_name()}[/item_name].[/failure]"
            )
