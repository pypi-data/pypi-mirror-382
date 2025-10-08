"""Teleportation Focus item for Act III."""

from ...engine.GameState import GameState
from ...engine.Item import Item


class TeleportationFocus(Item):
    """Anchor focus for long-range circle magic (Act III).

    Narrative Role:
        Stabilizes Mira's ritual spaces, enabling safe transitions once multi-room
        prerequisites are met.

    Key Mechanics:
        Non-carriable; examined for flavor and prevented from pickup to preserve ritual
        integrity.
    """

    def __init__(self) -> None:
        """Initialize Teleportation Focus with description and properties."""
        super().__init__(
            name="teleportation focus",
            short_name="focus",
            description=(
                "A crystal prism that hums faintly near Mira's spellwork. Facets "
                "catch stray motes of light and fold them inward, anchoring safe "
                "circles across distant thresholds."
            ),
            can_be_carried=False,
        )

    def examine(self, _game_state: GameState) -> str:  # noqa: ARG002
        """Return a descriptive examination of the focus."""
        return (
            "[event]You study the prism. Reflections hover a breath out of sync—each "
            "a doorway waiting for Mira's word.[/event]"
        )

    def prevent_pickup(self) -> str:
        """Prevent pickup, reminding the player of its ritual function."""
        return (
            "[character_name]Mira[/character_name] steadies the prism. "
            "[dialogue]'Careful. The circle anchors through this focus. I must bear "
            "it while the weave stays open.'[/dialogue]"
        )
