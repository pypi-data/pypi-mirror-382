"""Forest Hermit NPC definition.

Role:
    Transitional wilderness mentor who provides protective charm and activates
    the "Hermit's Warning" quest sequence (``FLAG_HERMITS_WARNING_ACCEPTED``) to
    gate deeper forest traversal with preparatory lore.

Key Mechanics:
    - First interaction grants ``ProtectiveCharm`` item and sets acceptance flag.
    - Subsequent talks reinforce guidance (non-repetitive reward logic).

Design Notes:
    Uses internal booleans to prevent duplicate charm distribution. Leaves quest
    completion mechanics to external forest transition logic per modular design.
"""

from ...engine.Character import Character
from ...engine.GameState import GameState
from ..items.ProtectiveCharm import ProtectiveCharm
from ..Act2StoryFlags import FLAG_HERMITS_WARNING_ACCEPTED

class ForestHermit(Character):
    """Wilderness mentor who grants a protective charm and warns of deeper trials."""

    def __init__(self) -> None:
        super().__init__(
            name="forest hermit",
            description=(
                "A mysterious figure wrapped in forest-green robes, with skin weathered "
                "by years in the wilderness. Their eyes hold the wisdom of the forest, "
                "and they carry protective charms and talismans from the deep woods."
            ),
        )
        self.has_warned = False
        self.charm_given = False

    def talk_to(self, game_state: GameState) -> str:
        name = self.get_name()
        event_msg = (
            "[event]You approach the [character_name]"
            + name
            + "[/character_name].[/event]"
        )

        if not self.has_warned:
            self.has_warned = True
            self.charm_given = True

            # Give protective charm and complete "The Hermit's Warning" quest
            protective_charm = ProtectiveCharm()
            game_state.add_item_to_inventory(protective_charm)
            # Quest will be activated by the Forest Transition room when appropriate
            # Set quest completion flag
            game_state.set_story_flag(FLAG_HERMITS_WARNING_ACCEPTED, True)
            return (
                event_msg
                + "\n"
                + (
                    f"[dialogue]The [character_name]{self.get_name()}[/character_name] "
                    "studies you with ancient eyes. 'I have been waiting for you, "
                )

                + (
                    "young one. The forest spirits whispered of your coming. You "
                    "seek to enter the Enchanted Forest, but few mortals who "
                    "venture unprepared ever return.'[/dialogue]\n\n"
                )

                + (
                    "[dialogue]'The forest is alive with magic both beautiful and "
                    "terrible. Ancient guardians protect its secrets, and the very "
                    "trees themselves judge the worth of those who walk among them. "
                    "Dark spirits prey upon the unwary, and the paths shift like "
                    "shadows at twilight.'[/dialogue]\n\n"
                )

                + (
                    "[dialogue]'But you... you have the light of destiny about you. "
                    "Take this charm—it will protect you from the forest's darker "
                    "influences and mark you as one under my protection. Remember: "
                    "show respect to all forest beings, never take more than you give, "
                    "and listen to the wind's warnings.'[/dialogue]\n\n"
                )

                + ("[event]You receive a [item_name]protective charm[/item_name]![/event]")
            )
        else:
            return (
                event_msg
                + "\n"
                + (
                    f"[dialogue]The [character_name]{self.get_name()}[/character_name] "
                    "nods knowingly. 'The forest awaits, but remember my warnings. "
                )
                + (
                    "Trust in nature's wisdom, and the ancient ways will guide your "
                    "steps. May the spirits of leaf and stone watch over you.'[/dialogue]"
                )
            )
