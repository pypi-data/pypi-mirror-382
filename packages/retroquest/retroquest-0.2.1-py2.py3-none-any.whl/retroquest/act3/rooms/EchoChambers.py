"""EchoChambers room for the resonant chant sequence in Act 3."""
from ...engine.Room import Room
from ...engine.GameState import GameState
from ..items.RunicWalls import RunicWalls
from ..items.OldOathScrolls import OldOathScrolls


class EchoChambers(Room):
    """Echoing caverns with runic walls and chant rubbings."""

    def __init__(self) -> None:
        """Initialize Echo Chambers with runic walls and exits."""
        super().__init__(
            name="Echo Chambers",
            description=(
                "Smooth caverns carved from living stone stretch into shadow, where "
                "every footfall reverberates through the darkness like whispered "
                "incantations. Faint, otherworldly voices seem to mimic your speech, "
                "echoing from unseen alcoves as if ancient spirits dwell within the "
                "walls themselves. Mysterious runic walls line the chamber, their "
                "symbols glowing with a dim, ethereal light that pulses in rhythm "
                "with your heartbeat. The air thrums with an almost palpable energy, "
                "and you sense that this place has witnessed rituals of great power."
            ),
            items=[RunicWalls()],
            exits={
                "west": "CollapsedGalleries"
            },
        )
        self._scrolls_discovered = False

    def search(self, _game_state: GameState, _target: str = None) -> str:
        """Search the Echo Chambers to discover hidden Old Oath Scrolls."""
        if not self._scrolls_discovered:
            self._scrolls_discovered = True
            old_oath_scrolls = OldOathScrolls()
            self.add_item(old_oath_scrolls)
            return (
                "Your careful search of the shadowed alcoves reveals a bundle of "
                "ancient scrolls tucked away in a stone niche, their parchment "
                "yellowed with age and covered in faded script. These appear to be "
                "old oath scrolls, containing wisdom about sacred promises and "
                "the true nature of selfless vows."
            )
        else:
            return (
                "You have already discovered the old oath scrolls hidden in this "
                "chamber. The alcoves hold no further secrets."
            )
