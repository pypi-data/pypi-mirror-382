"""WalkingStick: a simple travel aid item providing support on rugged mountain paths."""

from ...engine.GameState import GameState
from ...engine.Item import Item

class WalkingStick(Item):
    """A sturdy walking stick that aids travel and provides minor protection."""
    def __init__(self) -> None:
        super().__init__(
            name="walking stick",
            short_name="stick",
            description=(
                "A sturdy wooden walking stick worn smooth by many travelers. "
                "It provides reliable support on mountain paths and could serve "
                "as a makeshift weapon if needed."
            ),
            can_be_carried=True,
        )

    def use(self, _game_state: GameState) -> str:
        return (
            "You lean on the walking stick, feeling more steady on the rocky path. "
            "It's a small comfort and a reliable companion for any journey."
        )
