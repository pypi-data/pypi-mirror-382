"""Fishing rod item and its conditional upgrade to a magnetic variant."""
from typing import TYPE_CHECKING
from ...engine.Item import Item
from .Magnet import Magnet
from .MagneticFishingRod import MagneticFishingRod
if TYPE_CHECKING:
    from ...engine.GameState import GameState

class FishingRod(Item):
    """Fishing rod tool with upgrade path to a MagneticFishingRod."""

    def __init__(self) -> None:
        super().__init__(
            name="fishing rod",
            short_name="rod",
            description="A simple fishing rod. It looks a bit flimsy.",
            can_be_carried=True,
        )

    def use_with(self, game_state: 'GameState', other_item: Item) -> str:
        """Combine with Magnet if spell is learned, interact with River, or fail with Well."""
        if isinstance(other_item, Magnet):
            # Only allow combining if the spell 'purify' is learned
            if game_state.has_spell('purify'):
                # Remove self (FishingRod) and Magnet from inventory
                if self in game_state.inventory:
                    game_state.inventory.remove(self)
                if other_item in game_state.inventory:
                    game_state.inventory.remove(other_item)

                # Add MagneticFishingRod to inventory
                magnetic_rod = MagneticFishingRod()
                game_state.inventory.append(magnetic_rod)
                return (
                    f"[event]You attach the [item_name]{other_item.get_name()}[/item_name] to "
                    f"the [item_name]{self.get_name()}[/item_name], creating a "
                    f"[item_name]{magnetic_rod.get_name()}[/item_name].[/event]"
                )
            else:
                return (
                    "[failure]You could force the magnet onto the rod, but it would likely "
                    "prevent you from fishing — and you are really keen on doing some "
                    "fishing![/failure]"
                )

        from .River import River  # Local import
        if isinstance(other_item, River):  # River-specific interaction
            return other_item.use_with(game_state, self)

        from .Well import Well  # Local import for Well
        if isinstance(other_item, Well):
            return (
                "[failure]You try fishing in the [item_name]well[/item_name], but the "
                "[item_name]rod[/item_name] is too short to reach the water.[/failure]"
            )
        return super().use_with(game_state, other_item)
