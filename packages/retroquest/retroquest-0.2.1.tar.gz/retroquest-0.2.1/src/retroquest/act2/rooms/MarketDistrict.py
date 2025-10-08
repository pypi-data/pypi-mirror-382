"""Market District room for Act II."""

from ...engine.Room import Room
from ..characters.MasterMerchantAldric import MasterMerchantAldric
from ..characters.CaravanMasterThorne import CaravanMasterThorne
from ..items.ForestSurvivalKit import ForestSurvivalKit
from ..items.EnhancedLantern import EnhancedLantern
from ..items.QualityRope import QualityRope

class MarketDistrict(Room):
    """Commerce hub supplying preparation gear (Act II)."""
    def __init__(self) -> None:
        super().__init__(
            name="Market District",
            description=(
                "Narrow streets crammed with shops and trading posts weave a maze of commerce. "
                "Spices, leather, and fresh bread scent the air. Merchant wagons clog passageways "
                "while deals are argued in several languages. Serious business gets done here."
            ),
            items=[],
            characters=[MasterMerchantAldric(), CaravanMasterThorne()],
            exits={"west": "MainSquare", "north": "SilverStagInn", "south": "MerchantsWarehouse"}
        )

    def add_wares(self) -> None:
        """Populate the market's display wares as non-carriable placeholders.

        These items represent stock on display. A future purchase transaction would toggle each
        item's `can_be_carried` to True, allowing the player to take it.
        """
        survival_kit = ForestSurvivalKit()
        survival_kit.can_be_carried = False
        enhanced_lantern = EnhancedLantern()
        enhanced_lantern.can_be_carried = False
        quality_rope = QualityRope()
        quality_rope.can_be_carried = False
        self.items = [survival_kit, enhanced_lantern, quality_rope]
