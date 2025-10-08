"""A cracked brass mirror segment used in Mirror Terraces quests."""
from ...engine import Item, GameState

class BrassMirrorSegment(Item):
    """A curved brass segment for reassembling the mirror channel."""

    def __init__(self) -> None:
        """Initialize a Brass Mirror Segment item."""
        super().__init__(
            name="Brass Mirror Segment",
            description=(
                "A battered brass segment whose face still catches light. It looks "
                "fragile but usable when bound into the mirror mounts."
            ),
            short_name="mirror segment",
            can_be_carried=True,
        )

    def use_with(self, game_state: GameState, other_item: Item) -> str:
        """Allow using the brass segment with mounts by delegating to the mount.

        If `other_item` is a MirrorMount instance, delegate the action to its
        use_with so the mount handles inventory checks and state changes.
        """
        from ..items.MirrorMount import MirrorMount

        if isinstance(other_item, MirrorMount):
            # Delegate to the mount; pass this segment as the other_item
            return other_item.use_with(game_state, self)

        return super().use_with(game_state, other_item)
