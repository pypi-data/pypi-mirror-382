"""Weathered stone pillars containing moon-worn sigils for tideward work."""
from ...engine.GameState import GameState
from ...engine.Item import Item


class Steles(Item):
    """
    Ancient stone pillars at the shore's edge with ward sigils.

    Narrative Role:
    - Source of Moon Rune shards needed for tideward ritual work
    - Visual markers of the shore's magical foundation
    - Immovable landmarks that ground the scene in ancient power

    Key Mechanics:
    - Cannot be picked up (part of the shore itself)
    - Examine reveals pale fragments useful for sigil completion
    - Contains narrative hints about ward magic and tidebound rituals
    """
    def __init__(self) -> None:
        """Initialize Steles with description and properties."""
        super().__init__(
            name="Steles",
            description=(
                "Weathered stone pillars at the surf's edge. Faint moon sigils are "
                "traced beneath coral crust, their lines worn by tide and wind."
            ),
            short_name="steles",
            can_be_carried=False,
        )

    def prevent_pickup(self) -> str:
        """Override pickup prevention with context-specific message."""
        return (
            "[failure]You can't take the [item_name]Steles[/item_name]. They are part "
            "of the shore itself—heavy and set.[/failure]"
        )

    def examine(self, _game_state: GameState) -> str:
        """Override examine with detailed description of the steles and fragments."""
        return (
            "[event]The steles bear shallow moon-marks, pores packed with salt. "
            "Loose pale fragments glint in crevices—likely usable in sigil work.[/event]"
        )
