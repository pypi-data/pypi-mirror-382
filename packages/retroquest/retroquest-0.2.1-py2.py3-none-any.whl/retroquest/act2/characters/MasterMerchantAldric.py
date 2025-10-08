"""Master Merchant Aldric character (Act II)."""

from ...engine.Character import Character
from ...engine.GameState import GameState
from ...engine.Item import Item
from ..items.ForestSurvivalKit import ForestSurvivalKit
from ..items.EnhancedLantern import EnhancedLantern
from ..items.QualityRope import QualityRope

class MasterMerchantAldric(Character):
    """Merchant dealing premium adventure gear and expedition supplies."""
    def __init__(self) -> None:
        super().__init__(
            name="master merchant aldric",
            description=(
                "A prosperous merchant with keen eyes for quality goods. He specializes in "
                "premium adventure gear and has connections throughout the trading networks."
            ),
        )
        self.wares = {
            "forest survival kit": {"item": ForestSurvivalKit(), "price": 50},
            "enhanced lantern": {"item": EnhancedLantern(), "price": 40},
            "quality rope": {"item": QualityRope(), "price": 20}
        }
        self.dialogue_options = [
            "Welcome to Aldric's Premium Adventure Gear! Only the finest equipment for "
            "discerning adventurers.",
            "Planning an expedition? You've come to the right place for quality supplies.",
            "I've heard tales of strange happenings in the forest. Good thing I stock the "
            "best protective gear!",
        ]
        self.dialogue_index = 0
        self.closed_dialogue = (
            "The [character_name]Master Merchant Aldric[/character_name] looks at you "
            "appraisingly. "
            "[dialogue]'I deal only with established customers and those with proper "
            "credentials. "
            "Do you have any introduction or referral that would qualify you for "
            "my premium services?'[/dialogue]"
        )
        self.gave_flyer = False

    def talk_to(self, _game_state: GameState) -> str:
        # If merchant hasn't been given the flyer, shop is not fully open yet
        if not self.gave_flyer:
            return self.closed_dialogue

        # Build wares information similar to Act 1 Shopkeeper
        wares_info = "My premium selection includes:\n"
        if self.wares:
            for name, details in self.wares.items():
                wares_info += (
                    f"- [item_name]{name.title()}[/item_name]: {details['price']} "
                    "[item_name]gold coins[/item_name]\n"
                )
        else:
            wares_info = "I'm currently restocking my premium inventory.\n"

        # Cycle through dialogue options like Act 1 Shopkeeper
        dialogue = self.dialogue_options[self.dialogue_index]
        self.dialogue_index = (self.dialogue_index + 1) % len(self.dialogue_options)

        return (
            f'The [character_name]Master Merchant Aldric[/character_name] says: '
            f'[dialogue]"{dialogue} {wares_info.strip()}"[/dialogue]'
        )

    def give_item(self, game_state: GameState, item_object: Item) -> str:
        """Handle giving items to Master Merchant Aldric"""
        from ..items.MerchantsFlyer import MerchantsFlyer

        if isinstance(item_object, MerchantsFlyer):
            # Remove the flyer from inventory
            if item_object in game_state.inventory:
                game_state.inventory.remove(item_object)
            self.gave_flyer = True
            game_state.current_room.add_wares()
            item_name = item_object.get_name()
            return (
                f"[success]You present the [item]{item_name}[/item] to "
                "[character_name]Master Merchant Aldric[/character_name]. His eyes "
                "light up as he examines it. 'Ah, excellent! This flyer grants you "
                "access to our premium selection and preferred customer pricing. "
                "What quality goods can I help you acquire today?'[/success]"
            )

        # Non-flyer items are politely declined
        item_name = item_object.get_name()
        return (
            f'The [character_name]Master Merchant Aldric[/character_name] examines the '
            f"{item_name}. "
            "[dialogue]'I appreciate the offer, but I deal in adventure gear, not "
            "donations. Perhaps you could purchase something instead?'[/dialogue]"
        )

    def buy_item(self, item_name_to_buy: str, game_state: GameState) -> str:
        """Handle buying items from Master Merchant Aldric"""
        # Check if shop is accessible
        if not self.gave_flyer:
            return self.closed_dialogue

        item_name_to_buy = item_name_to_buy.lower()
        name = self.get_name()
        event_msg = (
            "[event]You try to buy the [item_name]" + item_name_to_buy
            + "[/item_name] from the [character_name]" + name
            + "[/character_name].[/event]"
        )

        # Check if item is available
        if item_name_to_buy not in self.wares:
            return (
                event_msg
                + "\n"
                + (
                    f'[dialogue]"Sorry, I don\'t have any \' '
                    f'[item_name]{item_name_to_buy}[/item_name]\' for sale. '
                    'Check my current inventory for available items.'
                    '[/dialogue]'
                )
            )

        ware_details = self.wares[item_name_to_buy]
        price = ware_details["price"]

        # Count total coins in inventory using the batching system
        total_coins = game_state.get_item_count("coins")

        # Check if player has enough coins
        if total_coins < price:
            return (
                event_msg
                + "\n"
                + (
                    f'[failure]You don\'t have enough [item_name]coins[/item_name] '
                    f'for the [item_name]{item_name_to_buy}[/item_name]. It costs {price} '
                    f'[item_name]gold coins[/item_name] but you only have {total_coins}.'
                    '[/failure]'
                )
            )

        # Check if already have the item in inventory (not counting display items in room)
        if any(
            item.get_name().lower() == item_name_to_buy
            and item.can_be_carried
            for item in game_state.inventory
        ):
            return (
                event_msg
                + "\n"
                + (
                    f'[dialogue]"You already have a [item_name]{item_name_to_buy}[/item_name]. '
                    'One should be sufficient for your needs.'
                    '[/dialogue]'
                )
            )

        # Purchase the item - spend coins using the batching system
        coins_removed = game_state.remove_item_from_inventory("coins", price)
        if coins_removed != price:
            return (
                event_msg
                + "\n"
                + ('[failure]Transaction failed. Unable to process payment.[/failure]')
            )

        # Remove the display item from the room (if present)
        room_item_to_remove = None
        for item in game_state.current_room.items:
            if item.get_name().lower() == item_name_to_buy:
                room_item_to_remove = item
                break

        if room_item_to_remove:
            game_state.current_room.items.remove(room_item_to_remove)

        # Create new carriable instance of the item to add to inventory
        new_item = None
        if item_name_to_buy == "forest survival kit":
            new_item = ForestSurvivalKit()
        elif item_name_to_buy == "enhanced lantern":
            new_item = EnhancedLantern()
        elif item_name_to_buy == "quality rope":
            new_item = QualityRope()

        if new_item:
            new_item.can_be_carried = True  # Ensure the purchased item is carriable
            game_state.add_item_to_inventory(new_item)
            remaining_coins = game_state.get_item_count("coins")
            return (
                event_msg
                + "\n"
                + f'[success]You purchase the [item_name]{item_name_to_buy}[/item_name] from '
                + f'[character_name]Master Merchant Aldric[/character_name] for {price} '
                + f'[item_name]gold coins[/item_name]. You have {remaining_coins} '
                + '[item_name]coins[/item_name] remaining.[/success]'
            )
        else:
            # Should not happen if item is in wares, but safety check
            return (
                event_msg
                + "\n"
                + '[failure]An unexpected error occurred trying to sell the '
                + f'[item_name]{item_name_to_buy}[/item_name].[/failure]'
            )
