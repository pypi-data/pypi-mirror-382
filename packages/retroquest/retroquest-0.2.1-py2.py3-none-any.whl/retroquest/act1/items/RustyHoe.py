
"""Gardening hoe with a rusted blade and splintered handle, useful for tilling soil."""
from ...engine.GameState import GameState
from ...engine.Item import Item

class RustyHoe(Item):
    """
    Gardening hoe with a rusted blade and splintered handle, useful for tilling soil.
    """

    def __init__(self) -> None:
        """Initialize the Rusty Hoe item with name, description, and carry status."""
        super().__init__(
            name="rusty hoe",
            description="A gardening hoe with a rusted blade and a splintered handle. "
            + "It might still be useful for tilling soil.",
            short_name="hoe",
            can_be_carried=True
        )

    def use(self, game_state: 'GameState') -> str:
        """Till the soil in Vegetable Field to find a coin, otherwise fail."""
        from .Coin import Coin
        if game_state.current_room.name == "Vegetable Field":
            player_has_coin = any(isinstance(item, Coin) for item in game_state.inventory)
            if not player_has_coin:
                game_state.add_item_to_inventory(Coin())
                return (
                    "[event]You till the soil with the [item_name]rusty hoe[/item_name].\n[/event]"
                    "The ground is tough, and you unearth a small, tarnished "
                    "[item_name]coin[/item_name]! "
                    "You quickly pocket it."
                )
            else:
                return (
                    "[failure]You till the soil again with the [item_name]hoe[/item_name], but it "
                    "seems you've already found what was hidden here.[/failure]"
                )
        else:
            return (
                "[failure]You swing the [item_name]rusty hoe[/item_name], but it doesn't seem to "
                "have much effect here. It's a sturdy (but rusty) tool, though.[/failure]"
            )
