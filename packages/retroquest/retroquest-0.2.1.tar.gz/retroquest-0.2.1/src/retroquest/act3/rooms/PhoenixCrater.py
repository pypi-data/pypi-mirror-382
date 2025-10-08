"""Module defining the PhoenixCrater room in Act 3."""
from ...engine.Room import Room


class PhoenixCrater(Room):
    """The Phoenix Crater: a luminous bowl of vitrified rock."""
    def __init__(self) -> None:
        """Initialize Phoenix Crater with description and exits."""
        self._base_description = (
            "A luminous bowl of vitrified rock where warm drafts swirl and cinders dance in "
            "spirals. The air smells of ozone, resin, and warm iron; the whole bowl feels like "
            "a giant hearth that remembers how to forge stars."
        )
        self._phoenix_description = (
            " At the crater's heart an enormous phoenix reclines on a throne of cooled slag and "
            "ember—its plumage a molten fan of red-gold feathers that shimmer and steam. Each "
            "breath it gives sends a shower of glowing ash that drifts like sparks, and its "
            "coal-bright eyes watch with a patient, ancient intelligence. Its talons curl around "
            "glassed stones, and every movement rings with a metal-on-metal chime, as if the bird "
            "were at once creature and relic. Now and then a single feather arcs away in a slow, "
            "burning arc, embedding itself in the rim where it cools to a shard that still hums "
            "faintly."
        )
        super().__init__(
            name="Phoenix Crater",
            description=self._base_description,
            items=[],
            characters=[],
            exits={"north": "FumarolePassages"},
        )
    def rest(self, _game_state) -> str:
        """Reveal the Phoenix when the player rests."""
        from ..characters.Phoenix import Phoenix
        if not any(c.get_name().lower() == "phoenix" for c in self.characters):
            self.add_character(Phoenix())
            self.description = self._base_description + self._phoenix_description
            return (
                "You rest for a moment, and as your eyes close, the air grows warmer. When you "
                "open them, a vast phoenix of living ember stands before you, its gaze meeting "
                "yours with ancient, knowing patience."
            )
        return "You rest for a moment, gathering your strength."
