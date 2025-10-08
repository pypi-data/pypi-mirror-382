"""A sharp knife item that can be used to cut through vines and other obstacles."""
from ...engine.Item import Item

class SharpKnife(Item):
    """A sharp knife item that can be used to cut through vines and other obstacles."""
    def __init__(self) -> None:
        super().__init__(
            name="sharp knife",
            description="A well-sharpened knife. It looks like it could cut through "
            + "almost anything.",
            short_name="knife",
            can_be_carried=True
        )

    def use_with(self, game_state, other_item: Item) -> str:
        from .Vines import Vines  # Local import for isinstance check
        if isinstance(other_item, Vines):
            return other_item.use_with(game_state, self)
        return super().use_with(game_state, other_item)
