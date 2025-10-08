"""AncientChronicle: stationary tome that can teach the Dispel spell."""

from ...engine.GameState import GameState
from ...engine.Item import Item
from ..Act2StoryFlags import FLAG_SPECTRAL_LIBRARIAN_FRIENDLY

class AncientChronicle(Item):
    """Stationary tome that can teach the Dispel spell when the librarian permits."""
    def __init__(self) -> None:
        super().__init__(
            name="ancient chronicle",
            short_name="chronicle",
            description=(
                "A massive tome containing historical records of the region. The pages hold "
                "detailed accounts of ancient bloodlines, family genealogies, and the "
                "significance of settlements such as Willowbrook."
            ),
            can_be_carried=False,
        )

    def use(self, game_state: GameState) -> str:
        if game_state.get_story_flag(FLAG_SPECTRAL_LIBRARIAN_FRIENDLY):
            # Learn dispel spell from ancient texts
            from ..spells.DispelSpell import DispelSpell
            game_state.learn_spell(DispelSpell())

            return (
                "[info]You study the ancient texts, reviewing the knowledge of the "
                "[spell_name]dispel[/spell_name] spell and the revelations about your "
                "heritage. The words of the Chosen One prophecy echo in your mind as you "
                "contemplate your destiny.[/info]"
            )
        else:
            return (
                "[info]The [character_name]Spectral Librarian[/character_name] materializes "
                "before you, blocking your access to the ancient texts. 'These sacred "
                "chronicles are not for the unworthy,' the spirit intones. 'Prove yourself "
                "first, then perhaps I will permit you to study these treasures.'[/info]"
            )
