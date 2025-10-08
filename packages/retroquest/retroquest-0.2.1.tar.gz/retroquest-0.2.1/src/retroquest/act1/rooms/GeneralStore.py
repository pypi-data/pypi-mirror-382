"""General Store room: static early merchant hub with multi-category items."""

from ...engine.Room import Room
from ..items.Rope import Rope
from ..items.Apple import Apple
from ..items.Matches import Matches
from ..items.Armor import Armor
from ..items.Sword import Sword
from ..characters.Shopkeeper import Shopkeeper

class GeneralStore(Room):
    """Foundational vendor location showcasing breadth of item categories.

    Narrative Role:
        Introduces economic hub concept and early provisioning context.

    Key Mechanics:
        Static seeded inventory; no transaction system or dynamic pricing yet.

    Story Flags:
        None currently.

    Contents:
        - Items: ``Rope``, ``Apple``, ``Matches``, ``Sword``, ``Armor``.
        - NPC: ``Shopkeeper``.

    Design Notes:
        Future economy: migrate to merchant inventory abstraction with dynamic stock.
    """
    def __init__(self) -> None:
        """Initialize the General Store with its static inventory and NPC."""
        super().__init__(
            name="General Store",
            description=(
                "A cluttered shop overflowing with goods of every kind. Shelves groan under "
                "the weight of rope, apples, matches, and trinkets. The shopkeeper bustles "
                "about, dusting jars and chatting with customers. The air is thick with the "
                "mingled scents of fruit, wax, and old wood. Every corner seems to hold a "
                "new surprise, and the promise of a good bargain."
            ),
            items=[Rope(), Apple(), Matches(), Sword(), Armor()],
            characters=[Shopkeeper()],
            # Map alignment
            exits={"west": "VillageSquare", "south": "BlacksmithsForge"}
        )
