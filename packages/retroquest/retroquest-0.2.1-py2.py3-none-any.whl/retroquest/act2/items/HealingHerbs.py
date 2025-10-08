"""Healing herbs item for Act 2 (alchemical / medical component)."""

from ...engine.GameState import GameState
from ...engine.Item import Item

class HealingHerbs(Item):
    """A bundle of medicinal herbs used for healing and crafting."""
    def __init__(self) -> None:
        super().__init__(
            name="healing herbs",
            short_name="herbs",
            description=(
                "A bundle of carefully selected medicinal herbs known for their "
                "healing properties. These herbs are essential for advanced healing "
                "magic and potion-making."
            ),
            can_be_carried=True,
        )

    def use(self, _game_state: GameState) -> str:
        return (
            "You examine the healing herbs. They are fresh and potent - perfect for use "
            "in advanced healing magic, training with Master Healer Lyria, or crafting "
            "powerful remedies."
        )
