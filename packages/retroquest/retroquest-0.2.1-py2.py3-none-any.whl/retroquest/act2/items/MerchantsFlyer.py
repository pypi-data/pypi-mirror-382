"""Merchant's flyer item for Market District introductions and coupons."""

from ...engine.GameState import GameState
from ...engine.Item import Item

class MerchantsFlyer(Item):
    """Promotional flyer advertising Market District merchants and coupons."""
    def __init__(self) -> None:
        super().__init__(
            name="merchant's flyer",
            short_name="flyer",
            description=(
                "A colorful handbill advertising the Market District's finest merchants "
                "and their premium goods. It features a special introduction coupon "
                "for new customers seeking quality adventure gear."
            ),
            can_be_carried=True,
        )

    def use(self, _game_state: GameState) -> str:
        return (
            "You examine the merchant's flyer. It advertises quality goods from Master "
            "Merchant Aldric and would serve as a good introduction when visiting "
            "the Market District."
        )
