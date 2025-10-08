"""Armor Item

Narrative Role:
Early defensive gear establishing the concept of protective equipment without yet
integrating numerical mitigation mechanics.

Key Mechanics / Interactions:
- Basic `equip` and `examine` flows; no durability or stat calculations.
- Mirrors acquisition gating pattern with shopkeeper via `prevent_pickup`.

Story Flags (Sets / Reads):
(none) – Purely descriptive at this stage.

Progression Effects:
- Reinforces preparation loop (procure weapon + armor) ahead of deeper mechanical systems.

Design Notes:
- Parallel structure to `Sword` maintains consistency in UX.
- Future: introduce armor tiers or conditional dialogue when equipped in specific encounters.

"""

from ...engine.Item import Item
from ...engine.GameState import GameState


class Armor(Item):
    """
    Early defensive gear establishing the concept of protective equipment.
    """

    def __init__(self) -> None:
        """Initialize the Armor item with name, description, and short name."""
        super().__init__(
            name="armor",
            description=(
                "A sturdy leather armor vest that provides protection from harm. "
                "Well-crafted and reliable."
            ),
            short_name="armor"
        )

    def prevent_pickup(self) -> str:
        """Shopkeeper prevents taking the armor unless it's been purchased."""
        if not self.can_be_carried_flag:
            return (
                f"[character_name]Shopkeeper[/character_name] quickly steps over. "
                f"[dialogue]'Hold on there, friend! That [item_name]{self.get_name()}[/item_name] "
                f"is merchandise, not a free sample. If you want it, you'll need to buy "
                f"it proper-like.'[/dialogue]"
            )
        return ""  # Allow pickup if can_be_carried is True

    def use(self, _game_state: GameState) -> str:
        """Examine the armor for its protective qualities."""
        return (
            "[event]You examine the [item_name]armor[/item_name]. "
            "It looks like it would provide good protection if worn.[/event]"
        )

    def equip(self, _game_state: GameState) -> str:
        """Equip the armor to feel more protected."""
        return (
            "[event]You put on the [item_name]armor[/item_name]. "
            "You feel more protected and ready for danger.[/event]"
        )

    def examine(self, _game_state: GameState) -> str:
        """Examine the armor and read its description."""
        return (
            "[event]You examine the [item_name]armor[/item_name]. "
            f"{self.description}[/event]"
        )
