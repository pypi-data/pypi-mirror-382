"""ShinyPebble: a small collectible pebble used for flavor and minor interactions."""

from ...engine.Item import Item


class ShinyPebble(Item):
    """Minor collectible pebble that glints; currently flavor-only."""

    def __init__(self) -> None:
        super().__init__(
            name="shiny pebble",
            description=(
                "A small, smooth pebble that glints in the sunlight. It feels oddly "
                "warm to the touch."
            ),
            short_name="pebble",
            can_be_carried=True
        )
