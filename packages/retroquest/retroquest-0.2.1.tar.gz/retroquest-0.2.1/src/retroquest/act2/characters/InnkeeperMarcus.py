"""Innkeeper Marcus NPC: lodging, wares, and post-cure rewards (Act II)."""

from ...engine.Character import Character
from ...engine.GameState import GameState
from ..items.RoomKey import RoomKey
from ..items.DruidicCharm import DruidicCharm
from ..Act2StoryFlags import FLAG_KNOWS_ELENA_CURSE, FLAG_INNKEEPERS_DAUGHTER_COMPLETED

class InnkeeperMarcus(Character):
    """Innkeeper NPC who sells wares and rewards the player after Elena's cure."""
    def __init__(self) -> None:
        super().__init__(
            name="innkeeper marcus",
            description=(
                "A kind-hearted man who runs The Silver Stag Inn. He has worry lines on "
                "his face and glances frequently toward his daughter with obvious "
                "concern."
            ),
        )
        self.wares = {
            "room key": {"item": RoomKey(), "price": 10}
        }
        self.dialogue_options = [
            "Welcome to The Silver Stag Inn! We offer comfortable rooms and warm meals "
            "for weary travelers.",
            "These have been difficult times, but we still maintain the finest "
            "accommodations in Greendale.",
            "A good night's rest in a private room can work wonders for mind and body.",
        ]
        self.dialogue_index = 0
        self.has_given_charm = False

    def talk_to(self, game_state: GameState) -> str:
        if game_state.get_story_flag(FLAG_INNKEEPERS_DAUGHTER_COMPLETED):
            if not self.has_given_charm:
                # First time speaking after Elena is cured - give the Druidic Charm
                self.has_given_charm = True
                druidic_charm = DruidicCharm()
                game_state.add_item_to_inventory(druidic_charm)

                charm_name = druidic_charm.get_name()
                name = self.get_name()
                head = (
                    f"[character_name]{name}[/character_name]: *tears of joy in his eyes* "
                    "You have given me back my daughter! There are no words to express my "
                    "gratitude. "
                )
                body = (
                    f"This [item_name]{charm_name}[/item_name] has been in my family for "
                    "generations - it was blessed by the ancient druids who first settled "
                    "in these lands. Please, take it as a token of our eternal gratitude. "
                    "May it bring you protection and guidance on your heroic journey!\n\n"
                )
                tail = (
                    "[success]Marcus places the sacred charm in your hands with reverence. "
                    "You can feel the ancient magic thrumming within the carved wood.[/success]"
                )
                return head + body + tail
            else:
                return (
                    f"[character_name]{self.get_name()}[/character_name]: My daughter is "
                    "healthy and happy again, all thanks to you! The Silver Stag Inn will "
                    "always be your home. Whatever you need - rooms, meals, information - "
                    "it's yours freely."
                )

        # Build wares information
        wares_info = "I can offer you:\n"
        if self.wares:
            for name, details in self.wares.items():
                wares_info += (
                    f"- [item_name]{name.title()}[/item_name]: {details['price']} "
                    "[item_name]gold coins[/item_name]\n"
                )
        else:
            wares_info = "I'm currently not offering any services.\n"

        # Cycle through dialogue options
        dialogue = self.dialogue_options[self.dialogue_index]
        self.dialogue_index = (self.dialogue_index + 1) % len(self.dialogue_options)
        name = self.get_name()

        if game_state.get_story_flag(FLAG_KNOWS_ELENA_CURSE):
            dialogue_block = (
                f'The [character_name]{name}[/character_name] says: [dialogue]"{dialogue} '
                + f'{wares_info.strip()}"[/dialogue]\n\n'
            )
            plea = (
                "You've spoken with [character_name]Elena[/character_name]? Then you "
                "understand my desperation. The curse grows stronger each day, and I "
                "fear we don't have much time left. If you truly can help her, I'll "
                "give you anything - rooms, information, whatever you need."
            )
            return dialogue_block + plea
        else:
            dialogue_block = (
                f'The [character_name]{name}[/character_name] says: [dialogue]"{dialogue} '
                + f'{wares_info.strip()}"[/dialogue]\n\n'
            )
            closing = (
                "Though I must say, these have been dark times for my family. My daughter... "
                "well, perhaps you should speak with her yourself if you're looking to help "
                "those in need."
            )
            return dialogue_block + closing

    def buy_item(self, item_name_to_buy: str, game_state: GameState) -> str:
        """Handle buying items from Innkeeper Marcus"""
        item_name_to_buy = item_name_to_buy.lower()
        seller = self.get_name()
        event_msg = (
            f"[event]You try to buy the [item_name]{item_name_to_buy}[/item_name] from the "
            f"[character_name]{seller}[/character_name].[/event]"
        )

        # Check if item is available
        if item_name_to_buy not in self.wares:
            item_disp = f'[item_name]{item_name_to_buy}[/item_name]'
            return (
                event_msg
                + "\n"
                + (
                    f'[dialogue]"Sorry, I don\'t have any \'{item_disp}\' '
                    'for sale. Check what I can offer you."[/dialogue]'
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
                    f'[failure]You don\'t have enough [item_name]coins[/item_name] for the '
                    f'[item_name]{item_name_to_buy}[/item_name]. It costs {price} '
                    f'[item_name]gold coins[/item_name] but you only have {total_coins}.[/failure]'
                )
            )

        # Check if already have the item in inventory (not counting display items in room)
        inventory = game_state.inventory
        if any(
            item.get_name().lower() == item_name_to_buy and item.can_be_carried
            for item in inventory
        ):
            return (
                event_msg
                + "\n"
                + (
                    f'[dialogue]"You already have a [item_name]{item_name_to_buy}[/item_name]. '
                    'One room should be sufficient for your stay."[/dialogue]'
                )
            )

        # Purchase the item - spend coins using the batching system
        coins_removed = game_state.remove_item_from_inventory("coins", price)
        if coins_removed != price:
            return (
                event_msg
                + "\n"
                + '[failure]Transaction failed. Unable to process payment.[/failure]'
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
        if item_name_to_buy == "room key":
            new_item = RoomKey()

        if new_item:
            new_item.can_be_carried = True  # Ensure the purchased item is carriable
            game_state.add_item_to_inventory(new_item)
            remaining_coins = game_state.get_item_count("coins")
            seller = self.get_name()
            purchase_msg = (
                f'[success]You purchase the [item_name]{item_name_to_buy}[/item_name] from '
                f'[character_name]{seller}[/character_name] for {price} '
                f'[item_name]gold coins[/item_name]. He hands you a brass key and '
                "explains how to access the private rooms upstairs. "
                f'You have {remaining_coins} [item_name]coins[/item_name] remaining.[/success]'
            )
            return event_msg + "\n" + purchase_msg
        else:
            # Should not happen if item is in wares, but safety check
            return (
                event_msg
                + "\n"
                + '[failure]An unexpected error occurred trying to rent the room.[/failure]'
            )
