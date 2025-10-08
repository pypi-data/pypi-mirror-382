"""SmoothStone Item

Narrative Role:
Ambient river find that can act as a tactile focus or low-stakes collectible,
grounding the world with natural artifacts.

Key Mechanics / Interactions:
- Portable (`can_be_carried=True`).
- No special actions yet – potential future use as a sling stone, rune substrate, or trade trinket.

Story Flags (Sets / Reads):
(none)

Progression Effects:
- Offers harmless inventory filler encouraging experimentation without risk.

Design Notes:
- Could be one of several variant stones encouraging set collection.

"""

from ...engine.Item import Item

class SmoothStone(Item):
    """
    Ambient river find that can act as a tactile focus or low-stakes collectible,
    grounding the world with natural artifacts.
    """

    def __init__(self) -> None:
        """Initialize the Smooth Stone item with name, description, and carry status."""
        super().__init__(
            name="smooth stone",
            description=(
                "A small, flat stone polished smooth by the river's current. It fits perfectly "
                "in your palm."
            ),
            short_name="stone",
            can_be_carried=True
        )
