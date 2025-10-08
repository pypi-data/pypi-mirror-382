"""Mountain Hermit (Act II)

Role:
        Transitional mentor stationed between Willowbrook and Greendale who gifts the Training
        Sword and foreshadows escalating regional threats, thematically bridging Acts I & II.

Interaction Mechanics:
        - On first talk_to(): sets internal warned flag and (if not already) grants TrainingSword
            via helper method for narrative pacing.
        - Subsequent talks reinforce motivational guidance and confirm sword possession.

State Tracking (instance attributes):
        - sword_given: ensures the Training Sword cannot be duplicated.
        - warned_about_times: controls delivery of initial prophetic warning block.

Items Granted:
        - TrainingSword (non-combat symbolic credential used to gain trust / prove skill in
            Greendale training contexts and potential gating with martial NPCs).

Design Notes:
        - Uses helper method give_training_sword_with_dialogue to consolidate reward flow.
        - Maintains narrative gravitas while remaining mechanically simple—does not set
            story flags to keep early Act II onboarding clean.
        - If later balancing requires gating Cedric's test, a story flag could be added when
            sword is granted; keep hermit self-contained otherwise.
"""

from ...engine.Character import Character
from ...engine.GameState import GameState
from ..items.TrainingSword import TrainingSword

class MountainHermit(Character):
    """Hermit NPC who mentors the player and grants the Training Sword."""
    def __init__(self) -> None:
        super().__init__(
            name="mountain hermit",
            description=(
                "An old man wrapped in weathered robes, with wise eyes that seem to have "
                "seen many seasons pass. He sits by a small fire, watching the path "
                "between Willowbrook and Greendale with keen interest."
            )
        )
        self.sword_given = False
        self.warned_about_times = False

    def talk_to(self, game_state: GameState) -> str:
        name = self.get_name()
        event_msg = (
            "[event]You approach the [character_name]"
            f"{name}[/character_name].[/event]"
        )

        if not self.warned_about_times:
            self.warned_about_times = True
            name = self.get_name()
            warning_msg = (
                "[dialogue]The [character_name]"
                f"{name}[/character_name] looks up from his fire with ancient eyes. "
                "'Ah, a traveler heading to Greendale. I sense great changes coming to "
                "these lands. Dark forces stir, and heroes will be needed in the days "
                "ahead. You have the look of one who might rise to such challenges.'[/dialogue]"
            )

            if not self.sword_given:
                # Automatically give the training sword when first spoken to
                return self.give_training_sword_with_dialogue(game_state, event_msg, warning_msg)
            else:
                return event_msg + "\n" + warning_msg
        else:
            if self.sword_given:
                training_sword = TrainingSword()
                name = self.get_name()
                sword_name = training_sword.get_name()
                return (
                    event_msg
                    + "\n"
                    + (
                        "[dialogue]The [character_name]"
                        f"{name}[/character_name] nods sagely. 'The [item_name]"
                        f"{sword_name}[/item_name] I gave you will serve you well in Greendale. "
                        "Show them your skill, and doors will open. May your journey be "
                        "blessed with wisdom and courage.'[/dialogue]"
                    )
                )
            else:
                return self.give_training_sword_with_dialogue(game_state, event_msg, "")

    def give_training_sword_with_dialogue(
        self,
        game_state: GameState,
        event_msg: str,
        warning_msg: str,
    ) -> str:
        """Helper method to give training sword with appropriate dialogue"""
        if self.sword_given:
            name = self.get_name()
            return (
                "[dialogue]The [character_name]"
                f"{name}[/character_name] smiles. 'I already gave you the sword, young one. "
                "Use it wisely.'[/dialogue]"
            )

        self.sword_given = True
        training_sword = TrainingSword()
        game_state.add_item_to_inventory(training_sword)

        sword_name = training_sword.get_name()
        sword_dialogue = (
            "[dialogue]He reaches into his pack and pulls out a [item_name]"
            f"{sword_name}[/item_name]. 'Take this. If you truly are destined for "
            "greatness, you'll need to prove your skills to those who matter. "
            "This blade has served me well in teaching others.'[/dialogue]\n\n"
            f"[event]You receive a [item_name]{sword_name}[/item_name]![/event]"
        )

        if warning_msg:
            return event_msg + "\n" + warning_msg + "\n\n" + sword_dialogue
        else:
            return event_msg + "\n" + sword_dialogue

    def give_training_sword(self, game_state: GameState) -> str:
        """
        Gives the player a training sword if it has not already been given.
        """
        if self.sword_given:
            name = self.get_name()
            return (
                "[dialogue]The [character_name]"
                f"{name}[/character_name] smiles. 'I already gave you the sword, young one. "
                "Use it wisely.'[/dialogue]"
            )

        self.sword_given = True
        training_sword = TrainingSword()
        game_state.add_item_to_inventory(training_sword)

        event_msg = (
            "[event]The [character_name]"
            f"{self.get_name()}[/character_name] hands you the [item_name]"
            f"{training_sword.get_name()}[/item_name]." "[/event]"
        )
        name = self.get_name()
        sword_name = training_sword.get_name()
        dialogue_block = (
            "[dialogue]'This blade has trained many would-be heroes. It may not be "
            "sharp enough for battle, but it will show your skill to those who need "
            "convincing. Use it well in Greendale.'[/dialogue]\n\n"
        )
        receive_event = f"[event]You receive a [item_name]{sword_name}[/item_name]![/event]"
        return event_msg + "\n" + dialogue_block + receive_event
