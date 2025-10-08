"""Corroded iron key from the pier vaults."""
from ...engine.GameState import GameState
from ...engine.Item import Item


class RustedLockerKey(Item):
    """
    A salt-corroded key that cannot open its intended lock through normal means.

    Narrative Role:
    - Symbol of decay and the futility of conventional approaches
    - Red herring that hints at magical solutions rather than physical ones
    - Atmospheric detail that reinforces the pier's deteriorated state

    Key Mechanics:
    - Can be carried but cannot successfully unlock the locker
    - Provides failure feedback when used with locker
    - Pickup text reinforces its compromised condition
    """
    def __init__(self) -> None:
        """Initialize Rusted Locker Key with description and properties."""
        super().__init__(
            name="Rusted Locker Key",
            description=(
                "A corroded iron key recovered from the pier vaults. Its teeth are "
                "pitted with salt and age."
            ),
            short_name="key",
            can_be_carried=True,
        )

    def picked_up(self, _game_state: GameState) -> str:
        """Override pickup to emphasize the key's compromised condition."""
        return (
            "[info]Its teeth are ragged with corrosion; it might fit, but the lock "
            "has long since fused.[/info]"
        )

    def use_with(self, _game_state: GameState, other_item: Item) -> str:
        """Override item interaction to provide failure feedback with locker."""
        from .Locker import Locker
        if isinstance(other_item, Locker):
            # Delegate to the locker interaction handler, providing this rusted
            # key as the 'other_item' so the Locker can decide how to respond.
            return other_item.use_with(_game_state, self)
        return super().use_with(_game_state, other_item)
