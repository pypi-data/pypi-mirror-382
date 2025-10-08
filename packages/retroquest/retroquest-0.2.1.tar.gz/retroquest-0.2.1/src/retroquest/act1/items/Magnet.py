"""Magnet Item

Narrative Role:
    Simple component item suggesting utility in retrieval puzzles and in crafting / combining
    with tools (fishing rod) to extend reach capability.

Key Mechanics / Interactions:
    - When used with ``FishingRod``, delegates to the rod to handle upgrade logic (centralizes
      combination rules in the primary tool).

Story Flags (Sets / Reads):
    (none)

Progression Effects:
    - Part of an upgrade chain enabling metallic object retrieval from depth (e.g., well ring
      via extended variants later).

Design Notes:
    - Minimal own logic; intentionally lean to reduce maintenance duplication across reciprocal
      ``use_with`` paths.
"""

from ...engine.Item import Item
from ...engine.GameState import GameState

class Magnet(Item):
    """
    Small, strong magnet used for retrieval puzzles and crafting upgrades.
    """

    def __init__(self) -> None:
        """Initialize the Magnet item with name, description, and carry status."""
        super().__init__(
            name="magnet",
            description=(
                "A small, surprisingly strong magnet. It might be useful for retrieving "
                "metallic objects from hard-to-reach places."
            ),
            can_be_carried=True,
        )

    def use_with(self, game_state: 'GameState', other_item: Item) -> str:
        """Delegate to FishingRod's use_with if applicable, otherwise fallback."""
        from .FishingRod import FishingRod
        if isinstance(other_item, FishingRod):
            return other_item.use_with(game_state, self)
        return super().use_with(game_state, other_item)
