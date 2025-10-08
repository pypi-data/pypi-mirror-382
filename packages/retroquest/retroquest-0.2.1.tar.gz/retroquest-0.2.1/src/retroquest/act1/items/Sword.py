"""Sword item for combat and heroism flavor."""

from ...engine.Item import Item
from ...engine.GameState import GameState

class Sword(Item):
    """
    Sword item representing a combat/heroism symbol with equip and examine actions.
    """
    def __init__(self) -> None:
        """Initialize the Sword item with name, description, and short name."""
        super().__init__(
            name="sword",
            description=(
                "A well-balanced iron sword with a sharp edge. The blade gleams with a faint "
                "sheen, and the leather-wrapped handle feels comfortable in your grip."
            ),
            short_name="sword"
        )

    def prevent_pickup(self) -> str:
        """Shopkeeper prevents taking the sword unless it's been purchased."""
        if not self.can_be_carried_flag:
            return (
                f"[character_name]Shopkeeper[/character_name] quickly steps over. "
                f"[dialogue]'Hold on there, friend! That [item_name]{self.get_name()}[/item_name] "
                f"is merchandise, not a free sample. If you want it, you'll need to buy it "
                f"proper-like.'[/dialogue]"
            )
        return ""  # Allow pickup if can_be_carried is True

    def use(self, _game_state: GameState) -> str:
        """Examine the sword for its combat readiness."""
        return (
            "[event]You examine the [item_name]sword[/item_name]. "
            "It feels perfectly balanced and ready for combat.[/event]"
        )

    def equip(self, _game_state: GameState) -> str:
        """Equip the sword to feel more confident and prepared."""
        return (
            "[event]You grip the [item_name]sword[/item_name] firmly. "
            "You feel more confident and prepared for any threats.[/event]"
        )

    def examine(self, _game_state: GameState) -> str:
        """Examine the sword and read its description."""
        return (
            "[event]You examine the [item_name]sword[/item_name]. "
            f"{self.description}[/event]"
        )
