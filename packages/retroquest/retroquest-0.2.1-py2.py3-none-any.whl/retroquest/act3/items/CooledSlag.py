"""Cooled Slag item: inert, glassy slag used for warding mixes."""

from ...engine.Item import Item



class CooledSlag(Item):
    """Cooled slag is granular, glassy waste usable in simple wards."""

    def __init__(self) -> None:
        super().__init__(
            name="cooled slag",
            description=(
                "Rough, glassy fragments of slag cooled against the tunnel walls. "
                "When ground with ash-fern it forms a basic heat‑ward paste."
            ),
            short_name="cooled slag",
            can_be_carried=True,
        )

    def use_with(self, game_state, other_item):
        """Delegate to AshFern's use_with if other_item is AshFern."""
        from .AshFern import AshFern
        if isinstance(other_item, AshFern):
            return other_item.use_with(game_state, self)
        return (
            f"[failure]You can't use the [item_name]{self.get_name()}[/item_name] "
            f"with the [item_name]{other_item.get_name()}[/item_name].[/failure]"
        )
