"""Town Crier (Act II)

Role:
    Ambient exposition NPC delivering broad hooks (Sir Cedric seeking aid, notice board mention)
    that funnel early Act II players toward central activity hubs.

Function:
    - Single static informative dialogue establishing civic vibrancy and quest availability.
    - No state, flags, or branching; intentionally reliable repeating information source.

Design Notes:
    - Could later rotate announcements based on major act flags (e.g., honor restored) without
      altering baseline signature.
    - Simplicity improves performance—no imports beyond engine basics.
"""

from ...engine.Character import Character
from ...engine.GameState import GameState

class TownCrier(Character):
    """Ambient NPC who broadcasts civic news and points players to key hubs."""
    def __init__(self) -> None:
        super().__init__(
            name="town crier",
            description=(
                "A loud, enthusiastic man dressed in official Greendale colors who "
                "announces news and events throughout the city. He carries a brass "
                "bell and scroll with current announcements."
            ),
        )

    def talk_to(self, _game_state: GameState) -> str:
        name = self.get_name()
        return (
            f"[character_name]{name}[/character_name]: Hear ye, hear ye! Welcome to Greendale, "
            "traveler! The great [character_name]Sir Cedric[/character_name] seeks brave souls "
            "to aid in important matters. If you're looking for adventure and the chance "
            "to serve the realm, head to the castle! Also, don't forget to check the "
            "notice board for other opportunities!"
        )
