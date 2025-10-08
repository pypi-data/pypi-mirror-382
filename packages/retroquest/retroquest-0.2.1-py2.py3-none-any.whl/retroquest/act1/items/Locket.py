
"""Small, intricately carved silver locket with narrative significance."""
from ...engine.Item import Item
from ...engine.GameState import GameState
from ..spells.BlessSpell import BlessSpell

class Locket(Item):
    """
    Small, intricately carved silver locket with narrative significance.
    """

    def __init__(self) -> None:
        """Initialize the Locket item with name, description, and carry status."""
        super().__init__(
            name="locket",
            description=(
                "A small, intricately carved silver locket, clearly very old. It feels cool "
                "to the touch. Perhaps some elder in the village might know more about it."
            ),
            short_name="locket",
            can_be_carried=True
        )

    def picked_up(self, game_state: GameState) -> str:
        """Teach Bless spell if Priest is present and spell not known."""
        if not game_state.has_spell(BlessSpell().name):
            bless_spell = BlessSpell()
            game_state.learn_spell(bless_spell)
            return (
                "[event]You pick up the locket.[/event]\nAs you do this, the "
                "[character_name]priest[/character_name] gasps. The "
                "[character_name]priest[/character_name] nods gravely. "
                "[dialogue]'That locket... it is a relic of the village founders. It speaks "
                "of your connection to this place and its history. May this blessing protect "
                "you on your path.'[/dialogue]\nHe teaches you the [spell_name]bless[/spell_name] "
                "spell!\n[event]You have learned [spell_name]bless[/spell_name].[/event]"
            )
        return ""
