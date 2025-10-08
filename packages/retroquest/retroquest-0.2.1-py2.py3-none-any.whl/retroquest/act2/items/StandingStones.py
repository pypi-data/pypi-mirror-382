"""Standing Stones (Act II environmental item)."""

from ...engine.Item import Item
from ..spells.NatureSenseSpell import NatureSenseSpell
from ...engine.GameState import GameState

class StandingStones(Item):
    """Ancient druidic monoliths that convey nature magic and may teach a spell."""
    def __init__(self) -> None:
        super().__init__(
            name="standing stones",
            short_name="stones",
            description=(
                "Ancient stone monoliths covered in moss and carved with protective runes "
                "that pulse with faint magic. These druidic markers have stood for "
                "centuries, representing protection, passage, and the balance between "
                "civilization and wilderness. The old magic within them protects travelers "
                "at this threshold."
            ),
            can_be_carried=False,
        )
        self.examined = False

    def examine(self, game_state: GameState) -> str:
        """Examine the standing stones to learn about their magic."""
        if not self.examined:
            self.examined = True
            # Learn nature_sense spell automatically
            if not game_state.has_spell(NatureSenseSpell().name):
                nature_sense = NatureSenseSpell()
                game_state.learn_spell(nature_sense)
                spell_msg = (
                    "\n\n[success]As you trace the druidic runes with your finger, "
                    "ancient knowledge flows into your mind. The symbols begin to make "
                    "sense—they're not just markers, but a teaching tool! You feel a "
                    "connection forming with the natural world around you, and suddenly "
                    "you understand how to cast the [spell_name]Nature's Sense[/spell_name] "
                    "spell![/success]\n\n"
                    "[event]You have learned the spell: "
                    "[spell_name]Nature's Sense[/spell_name]![/event]"
                )
            else:
                spell_msg = ""
            return (
                "[info]You approach the ancient standing stones and run your hands over their "
                "weathered surfaces. The runes carved into the stone are clearly druidic—symbols "
                "representing protection, passage, and the balance between civilization and "
                "wilderness. These stones have stood here for centuries, marking the boundary "
                "between worlds. You can feel the old magic thrumming within them, a gentle but "
                "powerful force that has protected travelers for generations.[/info]"
                + spell_msg
            )
        else:
            return (
                "The standing stones continue to pulse with ancient magic, their druidic runes a "
                "testament to the old ways."
            )
