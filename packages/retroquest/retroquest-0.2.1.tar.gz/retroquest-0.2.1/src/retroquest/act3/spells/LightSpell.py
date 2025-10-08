"""Light spell for Act 3."""

from ...engine.GameState import GameState
from ...engine.Spell import Spell


class LightSpell(Spell):
    """A steady kindling that coaxes prisms to life."""

    def __init__(self) -> None:
        """Initialize Light spell with description."""
        super().__init__(
            name="light",
            description="A steady kindling that coaxes prisms to life.",
        )

    def cast_spell(self, game_state: GameState) -> str:
        """Cast light spell, checking for room-specific lighting effects."""
        hook = getattr(game_state.current_room, 'cast_light_here', None)
        if hook:
            return hook(game_state)
        return ("[event]A warm spark flares in your palm and fades—nothing here seems to "
                "catch.[/event]")

    def cast_on_item(self, game_state: GameState, target_item) -> str:
        """Cast the spell on a specific item by delegating to the base class.

        Most items do not react specially, so the base implementation handles
        generic behavior. This override exists to permit room-level or
        item-level specialization when needed.
        """
        # If the target is a lantern bracket, casting light should trigger the
        # room-level lighting behavior (same as casting the spell normally).
        from ..items.LanternBracket import LanternBracket
        if isinstance(target_item, LanternBracket):
            return self.cast_spell(game_state)
        return super().cast_on_item(game_state, target_item)
