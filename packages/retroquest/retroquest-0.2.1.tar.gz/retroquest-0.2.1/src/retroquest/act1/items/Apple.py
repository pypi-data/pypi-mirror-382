"""Apple Item

Narrative Role:
Basic consumable-style food item establishing village economy flavor and shop ownership gating
pattern. Serves as a harmless early example of merchant-protected goods.

Key Mechanics / Interactions:
- Pickup may be blocked by shopkeeper until purchased (``prevent_pickup`` checks
    `can_be_carried_flag`).
- Currently no consumption mechanic; persists in inventory as flavor/ potential barter object.

Story Flags (Sets / Reads):
(none) – Ownership/permission enforced locally via pickup prevention.

Progression Effects:
- Reinforces that mundane items can still require proper acquisition steps.

Design Notes:
- Future extension: add a `consume` method to restore minor health or morale when a health
    system is introduced.

"""

from ...engine.Item import Item


class Apple(Item):
    """
    Basic consumable-style food item establishing village economy flavor and shop ownership gating.
    """

    def __init__(self) -> None:
        """Initialize the Apple item with name and description."""
        super().__init__(
            name="apple",
            description=(
                "A crisp, red apple. It looks fresh and delicious, perfect for a quick snack."
            )
        )

    def prevent_pickup(self) -> str:
        """Shopkeeper prevents taking the apple unless it's been given/purchased."""
        if not self.can_be_carried_flag:
            return (
                f"[character_name]Shopkeeper[/character_name] quickly steps over. "
                f"[dialogue]'Hold on there, friend! That [item_name]{self.get_name()}[/item_name] "
                f"is merchandise, not a free sample. If you want it, you'll need to buy it "
                f"proper-like.'[/dialogue]"
            )
        return ""  # Allow pickup if can_be_carried is True
