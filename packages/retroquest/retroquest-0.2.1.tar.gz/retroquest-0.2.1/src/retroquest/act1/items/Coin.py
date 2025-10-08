"""Coin item: simple Act I flavor token introducing future currency/economy concepts."""

from ...engine.GameState import GameState
from ...engine.Item import Item

class Coin(Item):
    """Basic currency token with minor flavor interaction (flip action).

    Purpose:
        Introduces the concept of trade goods / currency before formal economy systems are
        active. Provides a small ambient interaction via ``use``.

    Mechanics:
        - ``use``: returns a flavor message describing a coin flip result.

    Design Notes:
        Could later integrate with merchants or a barter subsystem; randomness could be
        injected for gamble hooks.
    """

    def __init__(self) -> None:
        super().__init__(
            name="coin",
            description=(
                "A small, circular piece of metal, likely used as currency. It has a simple "
                "stamp on one side."
            ),
            short_name="coin",
            can_be_carried=True,
        )

    def use(self, _game_state: GameState) -> str:
        """Flip the coin for a flavor message."""
        return (
            "[event]You flip the [item_name]coin[/item_name] in the air.[/event]\n"
            "It lands heads up. Seems like a regular [item_name]coin[/item_name], "
            "perhaps for trading."
        )
