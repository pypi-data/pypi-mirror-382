"""Silver leaves item: luminous forest collectible hinting at ritual reagent systems."""

from ...engine.Item import Item


class SilverLeaves(Item):  # pylint: disable=too-few-public-methods
    """Photic foliage fragment underscoring ancient forest luminosity themes.

    Purpose:
        Establishes subtle magical bioluminescent ecology; future alchemy / ritual
        reagent candidate making forest scavenging feel purposeful.

    Mechanics:
        Purely descriptive; inherits base ``examine``. Could later glow contextually
        near ley disturbances or during night cycles (if added).

    Design Notes:
        Kept minimal now to preserve upgrade space (infusions, powder extraction,
        barter token). Name aligned with potential parallel sets (e.g., Moonflowers).
    """

    def __init__(self) -> None:
        super().__init__(
            name="silver leaves",
            description=(
                "Delicate leaves that shimmer with a soft argent sheen even in shadow. "
                "Their surfaces refract light into faint auroral threads, and a cool, "
                "clean scent clings to them. Holding them you sense tranquil, ancient "
                "vitality."
            ),
            can_be_carried=True,
        )
