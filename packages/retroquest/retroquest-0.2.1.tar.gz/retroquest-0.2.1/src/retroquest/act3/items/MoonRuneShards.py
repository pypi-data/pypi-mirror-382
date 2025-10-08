"""Moon Rune shards used to engrave tideward sigils."""

from ...engine.GameState import GameState
from ...engine.Item import Item


class MoonRuneShards(Item):
    """
    Etched moon-forged shards used for ward-line restoration.

    Narrative Role:
    - Material component for completing tideward ward sigils
    - Harvested fragments that connect shore magic to ritual work
    - Tactile element that reinforces the coastal magical tradition
    """
    def __init__(self) -> None:
        """Initialize Moon Rune shards with description and properties."""
        super().__init__(
            name="Moon Rune Shards",
            description=(
                "Thin, chalky shards veined with pale luster. Each shard holds a "
                "faint lunar marking, as if carved in moonlight and salt."
            ),
            short_name="moon rune shards",
            can_be_carried=True,
        )

    def picked_up(self, _game_state: GameState) -> str:
        """Override pickup to provide tactile flavor text."""
        return "[dim]The shards whisper with tide-salt; they leave a faint dust on" \
               " your fingers.[/dim]"

    def use_with(self, game_state: GameState, other_item: 'Item') -> str:
        """Delegate pillar combinations to the room hook when used with pillars."""
        from .WardingPillars import WardingPillars
        if isinstance(other_item, WardingPillars):
            return other_item.use_with(game_state, self)
        return super().use_with(game_state, other_item)
