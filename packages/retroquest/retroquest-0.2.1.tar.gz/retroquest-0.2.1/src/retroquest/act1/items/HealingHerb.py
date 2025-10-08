"""Healing herb item used by the Act I healer NPC to control access to healing."""

from ...engine.Item import Item

class HealingHerb(Item):
    """Static, non-removable medicinal resource controlled by Mira (Act I healer).

    Purpose:
        Reinforces village stewardship: visible but not lootable. Communicates that healing
        will be accessed through NPC interaction rather than early inventory hoarding.

    Mechanics:
        - ``prevent_pickup`` always blocks acquisition with contextual dialogue.
        - No direct ``use``; future systems may enable brewing or preparation via healer.

    Design Notes:
        Could later support crafting verbs (e.g., ``brew``) gated by learned skill, location
        (Mira's hut), or quest milestones.
    """

    def __init__(self) -> None:
        super().__init__(
            name="healing herb",
            description=(
                "A bundle of fragrant green herbs, known for their restorative properties. "
                "Useful for healing wounds or brewing potions."
            ),
            short_name="herb",
        )

    def prevent_pickup(self) -> str:
        """Block pickup and deliver Mira's stewardship dialogue."""
        return (
            "[character_name]Mira[/character_name] gently but firmly stops you. "
            "[dialogue]'Those herbs are part of my stores, "
            "[character_name]Elior[/character_name]. They are not for taking, but for "
            "healing those who truly need them. If you require healing, simply ask.'"
            "[/dialogue]"
        )
