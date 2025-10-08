"""Horseshoe Item

Narrative Role:
Evokes pastoral setting and folk belief in luck. Serves as a sturdy metal artifact for potential
repair, warding, or trade quests.

Key Mechanics / Interactions:
- Currently inert flavor; portable.

Story Flags (Sets / Reads):
(none)

Progression Effects:
- Seeds expectation of future crafting/repair system or superstition-based interactions.

Design Notes:
- Could later mount above a doorway to set a protective flag or be combined with smithing tools.

"""

from ...engine.Item import Item

class Horseshoe(Item):
    """Portable flavor/crafting seed item representing a bent iron horseshoe.

    Purpose:
        Ambient world-building object that hints at future systems (luck, repair, trade,
        warding). Carries no current mechanical effect beyond being collectible.

    Design Notes:
        Could later:
            - Be mounted in a room to set a protective / luck flag.
            - Serve as a metal component in a smithing or repair recipe.
            - Act as a barter token for a superstition-inclined NPC.
    """

    def __init__(self) -> None:
        super().__init__(
            name="horseshoe",
            description=(
                "A heavy iron horseshoe, slightly bent. It might bring luck or be useful for "
                "repairs."
            ),
            can_be_carried=True,
        )
