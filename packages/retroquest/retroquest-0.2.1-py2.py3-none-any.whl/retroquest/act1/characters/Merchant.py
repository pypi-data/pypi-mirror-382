"""Merchant NPC who trades items and offers travel advice to the player."""

from ...engine.Character import Character
from ...engine.Item import Item
from ...engine.GameState import GameState


class Merchant(Character):
    """Traveling merchant NPC who trades valuables for useful gear."""
    def __init__(self) -> None:
        super().__init__(
            name="merchant",
            description=(
                "A traveling merchant with a cart full of wares and stories from "
                "distant lands. Always ready to trade or offer travel advice."
            )
        )
        self.boots_given = False  # Track if boots have been given

    def talk_to(self, _game_state: GameState, _player=None) -> str:
        """Return dialogue when the player speaks to the merchant."""
        # Use boots_given flag instead of checking inventory
        event_msg = (
            "[event]You speak with the [character_name]"
            + self.get_name()
            + "[/character_name].[/event]"
        )
        if not self.boots_given:
            return (
                event_msg
                + "\n"
                + (
                    "[dialogue]The [character_name]"
                    + self.get_name()
                    + "[/character_name] offers a friendly nod. 'Looking for something "
                    "specific, or just browsing? If you have any fine jewelry, especially "
                    "a [item_name]shiny ring[/item_name], I'm ready to exchange it for a "
                    "pair of sturdy [item_name]wandering boots[/item_name].'[/dialogue]"
                )
            )
        else:
            return (
                event_msg
                + "\n"
                + (
                    "[dialogue]The [character_name]"
                    + self.get_name()
                    + "[/character_name] grins. 'Those [item_name]boots[/item_name] should "
                    "serve you well on the road ahead! Let me know if you find anything "
                    "else of value.'[/dialogue]"
                )
            )

    def give_item(self, game_state: GameState, item_object: Item) -> str:
        """Handle items offered to the merchant and perform trades or gifts."""
        from ..items.ShinyRing import ShinyRing
        from ..items.WanderingBoots import WanderingBoots
        if isinstance(item_object, ShinyRing):
            game_state.remove_item_from_inventory(item_object.get_name())
            boots = WanderingBoots()
            game_state.add_item_to_inventory(boots)
            self.boots_given = True  # Set flag when boots are given
            event_msg = (
                "[event]You give the [item_name]"
                + item_object.get_name()
                + "[/item_name] to the [character_name]"
                + self.get_name()
                + "[/character_name].[/event]"
            )
            return (
                event_msg
                + "\n"
                + (
                    "[dialogue]The [character_name]"
                    + self.get_name()
                    + "[/character_name]'s eyes widen as you hand over the [item_name]"
                    + item_object.get_name()
                    + "[/item_name]. 'A fine piece! As promised, here are the [item_name]"
                    + boots.get_name()
                    + "[/item_name]. They'll serve you well on the road to Greendale.'[/dialogue]"
                )
                + "\n\n"
                + (
                    "[event]You receive a pair of [item_name]"
                    + boots.get_name()
                    + "[/item_name]![/event]"
                )
            )
        event_msg = (
            "[event]You offer the [item_name]"
            + item_object.get_name()
            + "[/item_name] to the [character_name]"
            + self.get_name()
            + "[/character_name].[/event]"
        )
        return (
            event_msg
            + "\n"
            + (
                "[dialogue]The [character_name]"
                + self.get_name()
                + "[/character_name] examines the [item_name]"
                + item_object.get_name()
                + "[/item_name] but shakes his head. 'Not interested in that, friend.'[/dialogue]"
            )
        )
