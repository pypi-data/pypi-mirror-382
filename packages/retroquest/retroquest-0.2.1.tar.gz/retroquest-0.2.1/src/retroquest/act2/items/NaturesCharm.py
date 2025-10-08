"""Nature's charm item for Act 2 (sacred ritual component)."""

from ...engine.Item import Item
from ...engine.GameState import GameState

class NaturesCharm(Item):
    """One of the sacred charms required for the Offering Altar ritual."""
    def __init__(self) -> None:
        super().__init__(
            name="nature's charm",
            description=(
                "An ancient charm blessed by the knights of old, carved from living wood and "
                "inlaid with silver runes. It pulses with a gentle green light and seems to "
                "resonate with the natural world. This is clearly one of the sacred charms "
                "mentioned in the old texts - those needed to summon the forest sprite Nyx."
            )
        )

    def use_with(self, game_state: 'GameState', other_item) -> str:
        from ..items.OfferingAltar import OfferingAltar
        if isinstance(other_item, OfferingAltar):
            return other_item.use_with(game_state, self)
        return super().use_with(game_state, other_item)
