"""A corroded coin glimpsed on the ruins' floors; carriable but unused."""
from ...engine.Item import Item


class WeatheredCoin(Item):
    """A salt-pitted coin from an older sea economy; collectible but not used."""

    def __init__(self) -> None:
        """Initialize a Weathered Coin item."""
        super().__init__(
            name="Weathered Coin",
            description=(
                "A small, greened coin whose face has long since been worn away. "
                "It might be worth something to a collector, but not here."
            ),
            short_name="coin",
            can_be_carried=True,
        )
