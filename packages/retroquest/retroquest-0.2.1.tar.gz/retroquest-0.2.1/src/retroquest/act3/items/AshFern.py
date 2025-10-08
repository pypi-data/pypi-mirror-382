"""Ash-Fern item: a fragile, ashen plant used in heat wards."""

from ...engine.Item import Item
from ...engine.GameState import GameState


class AshFern(Item):
    """Ash‑fern is a brittle, ashy frond used in simple warding mixtures."""

    def __init__(self) -> None:
        super().__init__(
            name="ash-fern",
            description=(
                "A brittle frond blackened by the mountain's breath. When mixed "
                "with cooled slag it can form a rudimentary heat‑ward paste."
            ),
            short_name="ash-fern",
            can_be_carried=True,
        )

    def use_with(self, game_state: GameState, other_item: Item) -> str:  # type: ignore[override]
        """Delegate combining with cooled slag to craft a heat ward mix."""
        # Import locally to avoid circular imports at module import time
        from ..items.HeatWardMix import HeatWardMix  # type: ignore
        from ..items.CooledSlag import CooledSlag

        # If combined with cooled slag, produce a HeatWardMix in inventory
        if isinstance(other_item, CooledSlag):
            # Remove components from inventory if present
            if self in game_state.inventory:
                game_state.inventory.remove(self)
            if other_item in game_state.inventory:
                game_state.inventory.remove(other_item)

            mix = HeatWardMix()
            game_state.inventory.append(mix)
            return (
                "[event]You combine the ash-fern with cooled slag, grinding them "
                "into a coarse paste. You now have a heat-ward mix.[/event]"
            )

        return (
            f"[failure]You can't use the [item_name]{self.get_name()}[/item_name] "
            f"with the [item_name]{other_item.get_name()}[/item_name].[/failure]"
        )
