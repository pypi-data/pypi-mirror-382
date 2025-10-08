"""Binding resin for repairing brass mirror segments."""
from ...engine import Item, GameState

class BindingResin(Item):
    """A viscous resin useful for securing mirror segments in mounts."""

    def __init__(self) -> None:
        """Initialize a Binding Resin item."""
        super().__init__(
            name="Binding Resin",
            description=(
                "A sticky, heat-cured resin used by mirrorwrights to bind brass "
                "segments into place."
            ),
            short_name="resin",
            can_be_carried=True,
        )

    def use_with(self, game_state: GameState, other_item: Item) -> str:
        """Delegate using resin on a MirrorMount to the mount's use_with.

        This allows commands like 'use resin with mirror mount' to be handled
        by the mount which enforces ordering and inventory rules.
        """
        from ..items.MirrorMount import MirrorMount

        if isinstance(other_item, MirrorMount):
            return other_item.use_with(game_state, self)

        return super().use_with(game_state, other_item)
