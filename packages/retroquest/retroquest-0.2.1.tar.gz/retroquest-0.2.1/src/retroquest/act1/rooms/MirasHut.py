"""Mira's Hut room: early healing and mystical mentor resource node."""

from ...engine.Room import Room
from ..items.HealingHerb import HealingHerb
from ..items.AncientAmulet import AncientAmulet
from ..characters.Mira import Mira

class MirasHut(Room):
    """Healing and arcane primer location anchored by mentor NPC.

    Narrative Role:
        Introduces restorative + mystical duality through item pairing and character.

    Key Mechanics:
        Static; supplies consumable (``HealingHerb``) and artifact (``AncientAmulet``).

    Story Flags:
        None currently.

    Contents:
        - Items: ``HealingHerb``, ``AncientAmulet``.
        - NPC: ``Mira``.

    Design Notes:
        Serves as base for potential later blessing or spell tutoring systems.
    """
    def __init__(self) -> None:
        """Initialize Mira's Hut with its items and resident mentor NPC."""
        super().__init__(
            name="Mira's Hut",
            description=(
                "A fragrant hut filled with drying herbs and mysterious potions. Shelves "
                "overflow with bottles, roots, and colorful flowers. The air is thick with "
                "the scent of lavender and sage. Sunlight streams through stained glass, "
                "painting the walls in shifting hues. Mira herself moves gracefully among "
                "her concoctions, her eyes bright with knowledge and kindness."
            ),
            items=[HealingHerb(), AncientAmulet()],
            characters=[Mira()],
            exits={"south": "VillageSquare"}
        )
