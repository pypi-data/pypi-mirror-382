"""PrayerBook Item

Narrative Role:
Religious/cultural artifact grounding village spirituality while hinting at latent mystical
currents (shifting runes). Bridges mundane faith and arcane systems.

Key Mechanics / Interactions:
- `read` produces atmospheric text with subtle arcane foreshadowing.
- Non-portable vs. portable distinction: currently carriable (could be restricted later
if needed).

Story Flags (Sets / Reads):
(none) – No tracking of whether player has read it yet.

Progression Effects:
- Enhances lore density; primes player for later ritual/spell incantation structures.

Design Notes:
- Could set a flag on first read to unlock evolved description or NPC dialogue variants.

"""

from ...engine.GameState import GameState
from ...engine.Item import Item

class PrayerBook(Item):
    """
    Religious/cultural artifact grounding village spirituality and hinting at mystical currents.
    """

    def __init__(self) -> None:
        """Initialize the Prayer Book item with name, description, and short name."""
        super().__init__(
            name="prayer book",
            description="A small, leather-bound book filled with prayers and hymns. "
            + "The pages are worn from years of use.",
            short_name="book"
        )

    def read(self, _game_state: 'GameState') -> str:
        """Read the prayer book and return its mystical message."""
        event_msg = f"[event]You read the [item_name]{self.get_name()}[/item_name].\n"
        return event_msg + (
            "The pages shimmer with shifting runes and cryptic sigils. As you try to focus, "
            "the words seem to rearrange themselves: 'By the moon's forgotten echo, let the "
            "silent bells resound...'\nBut the rest dissolves into a swirl of arcane nonsense. "
            "You feel a faint tingle in your fingertips."
        )
