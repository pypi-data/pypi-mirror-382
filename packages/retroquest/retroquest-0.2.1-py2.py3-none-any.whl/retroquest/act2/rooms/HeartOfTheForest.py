"""Heart of the Forest room: climactic ritual sanctum with offering altar."""

from ...engine.Room import Room
from ..items.OfferingAltar import OfferingAltar

class HeartOfTheForest(Room):
    """Climactic inner sanctum emphasizing ritual and revelation.

    Narrative Role:
        High‑magic focal space associated with Nyx and late-act lore delivery.
        Access already validated by upstream gating (AncientGrove path).

    Key Mechanics:
        - Static exits; contains ``OfferingAltar`` as ritual interaction hub.

    Story Flags:
        - Reads none directly; future altar interactions may set offering or
          blessing flags.

    Contents:
        - Item: ``OfferingAltar``.
        - Characters: None currently (sprite manifestation externalized).

    Design Notes:
        Kept static to focus player attention on event sequencing; could evolve
        into a ``RitualChamber`` specialization if multiple similar arenas are
        introduced.
    """

    def __init__(self) -> None:
        """Initialize heart chamber with altar and single northern exit."""
        super().__init__(
            name="Heart of the Forest",
            description=(
                "The deepest part of the Enchanted Forest, where reality feels fluid and "
                "magic flows like water. Impossible colors paint the landscape and the air "
                "sparkles with latent energy. A colossal tree dominates the center, its "
                "branches seeming to uphold the sky. Before it rests an ancient altar carved "
                "from starstone, runes pulsing with otherworldly light. This is Nyx's domain "
                "where profound secrets surface. The sacred grove path is the only passage into "
                "this mystical heart."
            ),
            items=[OfferingAltar()],
            characters=[],
            exits={"north": "AncientGrove"}
        )
