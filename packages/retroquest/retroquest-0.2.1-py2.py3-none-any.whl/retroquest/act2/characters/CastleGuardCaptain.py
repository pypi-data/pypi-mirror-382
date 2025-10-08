"""Castle Guard Captain: brief orientation NPC at the castle (Act II)."""

from ...engine.Character import Character
from ...engine.GameState import GameState

class CastleGuardCaptain(Character):
    """Orientation NPC who advises visitors on castle protocol and introductions."""
    def __init__(self) -> None:
        super().__init__(
            name="castle guard captain",
            description=(
                "A stern-looking officer in polished armor who oversees security for "
                "the castle grounds. He provides guidance on proper protocol for "
                "meeting with nobility."
            ),
        )

    def talk_to(self, _game_state: GameState) -> str:
        name = self.get_name()
        return (
            f"[character_name]{name}[/character_name]: Welcome to the castle grounds. "
            "[character_name]Sir Cedric[/character_name] can be found in the courtyard. "
            "When speaking with him, address him as 'Sir' and show proper respect. "
            "He's been seeking capable individuals for important work, so if you're "
            "here about that, be prepared to demonstrate your abilities."
        )
