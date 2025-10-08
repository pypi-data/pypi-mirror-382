"""Blacksmith: village blacksmith NPC and dialog logic."""

from ...engine.Item import Item
from ...engine.Character import Character
from ..Act1StoryFlags import FLAG_BLACKSMITH_MET, FLAG_DEER_CAN_BE_OBSERVED
from ..items.Coin import Coin
from ..items.DullKnife import DullKnife
from ..items.SharpKnife import SharpKnife
from ..items.MillstoneFragment import MillstoneFragment
from ...engine.GameState import GameState

class Blacksmith(Character):
    """Blacksmith NPC who forges tools, sharpens blades, and shares village lore."""

    def __init__(self) -> None:
        super().__init__(
            name="blacksmith",
            description=(
                "A burly, skilled craftsman who forges tools and weapons for the "
                "village. He is always ready to offer advice or sharpen a blade."
            ),
        )

    def talk_to(self, game_state: GameState) -> str:
        """Return dialogue when the player talks to the blacksmith.

        Sets and reads story flags to vary responses.
        """
        event_msg = (
            f"[event]You speak with the [character_name]{self.get_name()}"
            "[/character_name].[/event]"
        )

        if game_state.get_story_flag(FLAG_BLACKSMITH_MET):
            return (
                event_msg
                + "\n"
                + (
                    "[dialogue]'Welcome back, young [character_name]Elior[/character_name]. "
                    "Need something else?'[/dialogue]"
                )
            )

        game_state.set_story_flag(FLAG_BLACKSMITH_MET, True)
        return (
            event_msg
            + "\n"
            + (
                "[dialogue]'Well met, young one. I am Borin, the village "
                f"[character_name]{self.get_name()}[/character_name]. If you need tools "
                "made or mended, I'm your man. A sharp blade can be a good friend.'"
                "[/dialogue]"
            )
        )

    def give_item(self, game_state: GameState, item_object: Item) -> str:
        """Handle items offered to the blacksmith and perform exchanges.

        May modify inventory and set story flags.
        """
        if isinstance(item_object, Coin) or isinstance(item_object, DullKnife):
            # Check for "knife (dull)" in inventory
            dull_knife_instance = game_state.get_item('dull knife')
            coin_instance = game_state.get_item('coin')
            if dull_knife_instance and coin_instance:
                # Remove coin from inventory
                game_state.remove_item_from_inventory(item_object.get_name())
                # Remove the dull knife from inventory
                game_state.remove_item_from_inventory(dull_knife_instance.get_name())
                # Add a new sharp knife to inventory
                game_state.add_item_to_inventory(SharpKnife())

                event_msg = (
                    f"[event]You give the [item_name]{item_object.get_name()}[/item_name] "
                    f"and [item_name]{dull_knife_instance.get_name()}[/item_name] to the "
                    f"[character_name]{self.get_name()}[/character_name].[/event]"
                )

                return (
                    event_msg
                    + "\n"
                    + (
                        f"The [character_name]{self.get_name()}[/character_name] takes your "
                        f"[item_name]{item_object.get_name()}[/item_name] and your "
                        f"[item_name]{dull_knife_instance.get_name()}[/item_name]. He "
                        "expertly sharpens it on his whetstone and hands you back a "
                        "gleaming [item_name]sharp knife[/item_name]!"
                    )
                )
            else:
                event_msg = (
                    f"[event]You offer the [item_name]{item_object.get_name()}[/item_name] to "
                    f"the [character_name]{self.get_name()}[/character_name].[/event]"
                )
                return (
                    event_msg
                    + "\n"
                    + (
                        f"The [character_name]{self.get_name()}[/character_name] eyes the "
                        f"[item_name]{item_object.get_name()}[/item_name]. "
                        "[dialogue]'Thanks for the offer, but I can only sharpen a "
                        "[item_name]dull knife[/item_name] for ye if you have one—and you'll "
                        "need to pay me a coin for the service.'[/dialogue]"
                    )
                )
        elif isinstance(item_object, MillstoneFragment):
            game_state.remove_item_from_inventory(item_object.get_name())
            # Optionally, set a story flag if needed
            game_state.set_story_flag(FLAG_DEER_CAN_BE_OBSERVED, True)

            event_msg = (
                f"[event]You give the [item_name]{item_object.get_name()}[/item_name] to "
                f"the [character_name]{self.get_name()}[/character_name].[/event]"
            )

            return (
                event_msg
                + "\n"
                + (
                    f"The [character_name]{self.get_name()}[/character_name] takes the "
                    f"[item_name]{item_object.get_name()}[/item_name], turning it over in "
                    "his calloused hands. "
                    "[dialogue]'Aye, this is from the old mill, alright. Sturdy stone. "
                    "You know, old tales say the mill was built on a place of ancient "
                    "power. Some say a magical deer sometimes appears in the Hidden "
                    "Glade, but only when all is calm and rest-ful—no voices, no "
                    "footsteps, just the hush of the wind and the song of the stream. "
                    "If you seek the deer, remember: it will not show itself to those "
                    "who rush or bring trouble.'[/dialogue]"
                )
            )
        else:
            event_msg = (
                f"[event]You offer the [item_name]{item_object.get_name()}[/item_name] to "
                f"the [character_name]{self.get_name()}[/character_name].[/event]"
            )

            return (
                event_msg
                + "\n"
                + (
                    f"The [character_name]{self.get_name()}[/character_name] looks at the "
                    f"[item_name]{item_object.get_name()}[/item_name]. "
                    "[dialogue]'I don't have a use for this, lad.'[/dialogue]"
                )
            )
