"""Boundary stone fragment item: inert lore shard hinting at future warding/ley-line systems."""

from ...engine.Item import Item


class BoundaryStoneFragment(Item):  # pylint: disable=too-few-public-methods
    """Weathered geomantic shard foreshadowing ward restoration mechanics.

    Purpose:
        Flavor collectible establishing the existence of boundary / ley infrastructure
        maintaining balance between settlement and wild regions.

    Mechanics:
        Currently inert; no ``use`` override. May combine with other fragments to form
        a reconstructed warding stone or unlock a stabilization ritual.

    Design Notes:
        Kept deliberately minimal until a broader ley-line or artifact assembly system
        is introduced. Naming supports future numbered suffix variants.
    """

    def __init__(self) -> None:
        """Initialize immutable fragment metadata (no dynamic state needed)."""
        super().__init__(
            name="boundary stone fragment",
            description=(
                "A weathered shard of carved granite etched with faint, interlocking sigils. "
                "The lines form geometric patterns suggestive of containment or balance, "
                "though erosion has obscured parts of the design. A residual tingle of "
                "dormant warding magic lingers in the stone."
            ),
            short_name="stone fragment",
            can_be_carried=True,
        )
