"""Fisherman NPC who teaches fishing basics and can accept fish."""

from ...engine.Character import Character
from ...engine.Item import Item
from ..items.Fish import Fish
from ..spells.PurifySpell import PurifySpell
from ...engine.GameState import GameState


class Fisherman(Character):
    """Fisherman NPC who teaches fishing basics and can accept fish."""

    def __init__(self) -> None:
        super().__init__(
            name="fisherman",
            description=(
                "A weathered old man who spends his days by the riverbank, "
                "fishing and humming quiet tunes. He knows much about the river "
                "and its secrets."
            ),
        )
        self.knows_fishing_basics = False
        self.received_fish = False
        self.dialogue_states = {
            "initial": (
                "[dialogue]The [character_name]fisherman[/character_name] nods at you. "
                "'The river's been a bit strange lately. Not many fish biting, and "
                "my arm... well, it's seen better days. Oh, I wish I could pull up "
                "a pike or two!'[/dialogue]"
            ),
            "taught_fishing": (
                "[dialogue]The [character_name]fisherman[/character_name] smiles. 'Good "
                "to see you trying your luck with the rod. Any luck yet?'[/dialogue]"
            ),
            "received_fish_thanks": (
                "[dialogue]The [character_name]fisherman[/character_name]'s eyes light "
                "up. 'Ah, a fine catch! Thank you kindly. It's been a while since "
                "I've had a fresh river fish.'[/dialogue]"
            ),
            "taught_spells": (
                "[dialogue]The [character_name]fisherman[/character_name] looks out "
                "over the water. 'The river has many moods. Treat it with respect, "
                "and it might share its secrets with you.'[/dialogue]"
            ),
        }
        self.current_dialogue_key = "initial"

    def talk_to(self, game_state: GameState) -> str:  # noqa: D401 - override explanation
        """Handle talking to the fisherman and teach fishing basics if eligible."""
        # Set the story flag that the player has talked to the fisherman
        game_state.set_story_flag("talked_to_fisherman", True)
        # Check if player has a fishing rod in game_state.inventory
        player_has_rod = game_state.has_item("fishing rod")

        if self.current_dialogue_key == "initial":
            if player_has_rod and not game_state.get_story_flag("learned_fishing_basics"):
                game_state.set_story_flag("learned_fishing_basics", True)
                self.knows_fishing_basics = True
                self.current_dialogue_key = "taught_fishing"
                return (
                    "[dialogue]The [character_name]fisherman[/character_name] notices "
                    "your [item_name]fishing rod[/item_name]. 'Ah, a fellow angler! "
                    "My arm's busted, can't fish myself. But I can tell you a thing "
                    "or two. Cast your line near the reeds, that's where they like "
                    "to hide. Patience is key, my friend, patience.'[/dialogue]\n"
                    "He teaches you the basics of fishing."
                )
            elif game_state.get_story_flag("learned_fishing_basics"):
                # If already taught, but current_dialogue_key is still initial, switch
                # to taught_fishing so the dialogue falls through below.
                self.current_dialogue_key = "taught_fishing"
            else:
                return self.dialogue_states["initial"]

        if self.current_dialogue_key == "taught_fishing" and self.received_fish:
            # This state transition happens in give_item
            pass

        event_msg = (
            "[event]You speak with the [character_name]"
            + self.get_name()
            + "[/character_name].[/event]"
        )
        return event_msg + "\n" + self.dialogue_states[self.current_dialogue_key]

    def give_item(self, game_state: GameState, item_object: Item) -> str:
        """Handle items offered to the fisherman and teach spells if appropriate."""
        if isinstance(item_object, Fish) and not self.received_fish:
            self.received_fish = True
            game_state.remove_item_from_inventory(item_object.name)
            # Teach spell
            game_state.learn_spell(PurifySpell())
            self.current_dialogue_key = "taught_spells"
            event_msg = (
                "[event]You give the [item_name]"
                + item_object.name
                + "[/item_name] to the [character_name]Fisherman[/character_name].[/event]"
            )
            return (
                event_msg
                + "\n"
                + self.dialogue_states["received_fish_thanks"]
                + " "
                + (
                    "[dialogue]'The river's water... it's not been right. Murky. "
                    "But I sense you have a connection to the old ways. Let me "
                    "teach you something to help. With this, you can cleanse "
                    "water,'[/dialogue] "
                )
                + "\n"
                + "You have learned [spell_name]purify[/spell_name]!"
            )

        elif isinstance(item_object, Fish) and self.received_fish:
            event_msg = (
                "[event]You offer the [item_name]"
                + item_object.name
                + "[/item_name] to the [character_name]Fisherman[/character_name].[/event]"
            )
            return (
                event_msg
                + "\n"
                + (
                    "[dialogue]The [character_name]fisherman[/character_name] smiles. "
                    "'Thank you, but I've already eaten. Save it for yourself!'"
                    "[/dialogue]"
                )
            )

        event_msg = (
            "[event]You offer the [item_name]"
            + item_object.name
            + "[/item_name] to the [character_name]Fisherman[/character_name].[/event]"
        )
        return (
            event_msg
            + "\n"
            + (
                "The [character_name]fisherman[/character_name] looks at the "
                "[item_name]"
                + item_object.name
                + "[/item_name] curiously but doesn't seem to need it."
            )
        )
