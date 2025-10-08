"""Healer's House room: restorative enclave for future healing progression."""

from ...engine.Room import Room
from ..characters.MasterHealerLyria import MasterHealerLyria

class HealersHouse(Room):
    """Restorative cottage supporting future advanced healing interactions.

    Narrative Role:
        Provides a quiet location associated with recovery and potential future
        spell or ritual learning through the resident healer.

    Key Mechanics:
        - Maintains ``emergency_healing_used`` boolean (reserved for later one‑
          time aid or scripted event).

    Story Flags:
        - None currently (state local; may promote to flag when shared logic is
          required across rooms).

    Contents:
        - NPC: ``MasterHealerLyria``.
        - Items: None (ambiance only for now).

    Design Notes:
        Kept deliberately minimal; healing actions should likely live on the
        character class rather than room to maintain single responsibility.
    """

    def __init__(self) -> None:
        """Initialize healer's house with ambient description and healer NPC."""
        super().__init__(
            name="Healer's House",
            description=(
                "A cozy cottage filled with the scents of medicinal herbs and healing potions. "
                "Dried plants hang from the rafters and shelves are packed with bottles of many "
                "shapes and colors. A warm fire crackles in the hearth while comfortable chairs "
                "invite recovery. This is clearly a place of healing and learning."
            ),
            items=[],
            characters=[MasterHealerLyria()],
            exits={"south": "ResidentialQuarter"}
        )
        self.emergency_healing_used = False
