
"""Small, rusty key for unlocking objects in the environment."""
from ...engine.GameState import GameState
from ...engine.Item import Item

class Key(Item):
    """
    Small, rusty key for unlocking objects in the environment.
    """

    def __init__(self) -> None:
        """Initialize the Key item with name, description, and carry status."""
        super().__init__(
            name="key",
            description="A small, rusty key. It looks like it might unlock something.",
            can_be_carried=True
        )

    def use_with(self, game_state: 'GameState', other_item: Item) -> str:
        """Use the key with a ShedDoor, otherwise fallback to base behavior."""
        from .ShedDoor import ShedDoor
        if isinstance(other_item, ShedDoor):
            return other_item.use_with(game_state, self)
        return super().use_with(game_state, other_item)
