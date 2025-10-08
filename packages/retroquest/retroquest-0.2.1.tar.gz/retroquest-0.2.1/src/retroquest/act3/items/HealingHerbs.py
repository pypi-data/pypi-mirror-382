"""Healing Herbs item for Act III."""

from ...engine.GameState import GameState
from ...engine.Item import Item


class HealingHerbs(Item):
    """Mira's herbal preparations for ritual stabilization (Act III).

    Narrative Role:
        Establishes Mira's expertise and provides thematic preparation elements for
        complex rituals.

    Key Mechanics:
        Non-carriable; interaction restricted to preserve ritual integrity and reserve
        for guided use.
    """
    def __init__(self) -> None:
        """Initialize Healing Herbs with description and restrictions."""
        super().__init__(
            name="healing herbs",
            short_name="herbs",
            description=(
                "Bundles of resin-sweet stems and silverleaf—Mira's blends for "
                "steadying wounds and sharpening ritual focus during complex workings."
            ),
            can_be_carried=False,
        )

    def prevent_pickup(self) -> str:
        """Block pickup with narrative explanation through Mira."""
        return (
            "[character_name]Mira[/character_name] lifts a sachet, then shakes her "
            "head. [dialogue]'Leave these for the circles and crossings. When the "
            "rite calls for them, I will place them in your hands.'[/dialogue]"
        )

    def use(self, _game_state: GameState) -> str:  # noqa: ARG002
        """Provide flavor text when examining the herb preparations."""
        return (
            "You sort the sachets by scent and potency. Mira's mix will steady "
            "breath and sharpen focus—useful in rites and long treks between "
            "thresholds."
        )
