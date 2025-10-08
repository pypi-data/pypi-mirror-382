"""Magnetic fishing rod item used for attracting metallic objects and upgrades."""

from typing import TYPE_CHECKING
from ...engine.Item import Item
from .Stick import Stick

if TYPE_CHECKING:
    from ...engine.GameState import GameState

class MagneticFishingRod(Item):
    """
    Fishing rod with a magnet, used for attracting metallic objects and crafting upgrades.
    """

    def __init__(self) -> None:
        """Initialize the Magnetic Fishing Rod item with name and description."""
        super().__init__(
            name="magnetic fishing rod",
            description=(
                "A fishing rod with a magnet attached to the end. Good for attracting "
                "metallic objects."
            )
        )

    def use_with(self, game_state: 'GameState', other_item: Item) -> str:
        """Combine with Stick to create ExtendedMagneticFishingRod, or fail with Well."""
        from .ExtendedMagneticFishingRod import ExtendedMagneticFishingRod
        if isinstance(other_item, Stick):
            if self in game_state.inventory:
                game_state.inventory.remove(self)
            if other_item in game_state.inventory:
                game_state.inventory.remove(other_item)
            extended_rod = ExtendedMagneticFishingRod()
            game_state.inventory.append(extended_rod)
            return (
                f"[event]You attach the [item_name]{other_item.get_name()}[/item_name] "
                f"to the [item_name]{self.get_name()}[/item_name], creating an "
                f"[item_name]{extended_rod.get_name()}[/item_name].[/event]"
            )
        from .Well import Well
        if isinstance(other_item, Well):
            return (
                f"[failure]You try fishing in the [item_name]{other_item.get_name()}[/item_name], "
                f"but the [item_name]{self.get_name()}[/item_name] is too short to"
                f" reach the water.[/failure]"
            )
        return super().use_with(game_state, other_item)
