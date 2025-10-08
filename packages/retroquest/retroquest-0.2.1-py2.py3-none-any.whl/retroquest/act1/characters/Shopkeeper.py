"""Shopkeeper NPC for Act I - general store owner and vendor logic."""

from ...engine.Character import Character
from ...engine.Item import Item
from ..items.Rope import Rope
from ..items.Apple import Apple
from ..items.Matches import Matches
from ..items.Coin import Coin
from ..items.Armor import Armor
from ..items.Sword import Sword
from ..Act1StoryFlags import FLAG_CONNECT_WITH_NATURE
from ...engine.GameState import GameState

class Shopkeeper(Character):
    """
    Represents the shopkeeper NPC in Willowbrook's General Store.
    """
    def __init__(self) -> None:
        super().__init__(
            name="shopkeeper",
            description=(
                "The owner of the General Store, always bustling about and eager to "
                "strike a bargain or share a rumor."
            )
        )
        self.wares = {
            "rope": {"item": Rope(), "price": 1},
            "matches": {"item": Matches(), "price": 4},
            "sword": {"item": Sword(), "price": 5},
            "armor": {"item": Armor(), "price": 10}
        }
        self.dialogue_options = [
            (
                "Welcome to my humble store! Finest goods in Willowbrook, "
                "I assure you."
            ),
            "Looking for something specific, or just browsing?",
            (
                "Heard some strange tales from travelers lately. This village "
                "isn't as sleepy as it seems."
            ),
        ]
        self.dialogue_index = 0
        self.closed_dialogue = (
            "The [character_name]Shopkeeper[/character_name] shakes his head. "
            "[dialogue]'Sorry, not open for business just yet. Come back later, lad—"
            "there's something you need to discover first.'[/dialogue]"
        )

    def talk_to(self, game_state: GameState) -> str:
        # If Elior hasn't been tasked to connect with nature, shop is not open yet
        if not game_state.get_story_flag(FLAG_CONNECT_WITH_NATURE):
            return self.closed_dialogue

        # Check if priest needs matches and shopkeeper hasn't given them yet
        if game_state.get_story_flag("priest_talked_to") and "matches" in self.wares:
            # Assuming matches_item_in_room is always found if this block is reached
            # Give matches to player for the priest
            game_state.current_room.remove_item("Matches")

            new_matches = Matches()  # Create a new instance for the inventory
            game_state.add_item_to_inventory(new_matches)

            # Remove matches from wares so they can't be bought/given again
            del self.wares["matches"]

            return (
                "The [character_name]Shopkeeper[/character_name] leans in. "
                '[dialogue]"Ah, you spoke to the [character_name]priest[/character_name]? '
                'He does get through his [item_name]matches[/item_name]. '
                'Here, take these for him, on the house. Tell him I said hello!"[/dialogue]'
                "\n\n[event]You receive a box of [item_name]matches[/item_name].[/event]"
            )

        # Standard dialogue if matches aren't being given for the priest
        wares_info = "I have a few things for sale:\n"
        if self.wares:
            for name, details in self.wares.items():
                wares_info += (
                    f"- [item_name]{name.capitalize()}[/item_name]: {details['price']} "
                    "[item_name]coin(s)[/item_name]\n"
                )
        else:
            wares_info = "I'm currently out of stock of items for sale.\n"

        wares_info += (
            "And remember, you always get an extra [item_name]apple[/item_name] "
            "with every purchase!\n"
        )

        dialogue = self.dialogue_options[self.dialogue_index]
        self.dialogue_index = (self.dialogue_index + 1) % len(self.dialogue_options)

        return (
            "The [character_name]Shopkeeper[/character_name] says: "
            f'[dialogue]"{dialogue} {wares_info.strip()}[/dialogue]"'
        )

    def give_item(self, _game_state: GameState, _item_object: Item) -> str:
        """Handle an item being given to the shopkeeper; unused parameters are
        underscored per project rules."""
        return (
            "The [character_name]Shopkeeper[/character_name] chuckles. "
            '[dialogue]"Not looking for donations, friend, but I appreciate the '
            'thought!"[/dialogue]'
        )

    def buy_item(self, item_name_to_buy: str, game_state: GameState) -> str:
        if not game_state.get_story_flag(FLAG_CONNECT_WITH_NATURE):
            return self.closed_dialogue
        item_name_to_buy = item_name_to_buy.lower()
        event_msg = (
            f"[event]You try to buy the [item_name]{item_name_to_buy}[/item_name] from the "
            f"[character_name]{self.get_name()}[/character_name].[/event]"
        )
        if item_name_to_buy not in self.wares:
            return (
                event_msg
                + "\n"
                + (
                    "[dialogue]Sorry, I don't have any '[item_name]"
                    + f"{item_name_to_buy}[/item_name]' for sale.[/dialogue]"
                )
            )

        ware_details = self.wares[item_name_to_buy]
        price = ware_details["price"]

        # Check if player has enough coins
        coin_count = 0
        for item in game_state.inventory:
            if isinstance(item, Coin):
                coin_count += 1

        if coin_count < price:
            return (
                event_msg
                + "\n"
                + (
                    f"[failure]You don't have enough [item_name]coins[/item_name] for "
                    f"the [item_name]{item_name_to_buy}[/item_name]. It costs {price} "
                )
                + "[item_name]coin(s)[/item_name].[/failure]"
            )

        # Remove coins from inventory
        removed_coins = 0
        for item in list(game_state.inventory):  # Iterate over a copy for safe removal
            if isinstance(item, Coin) and removed_coins < price:
                game_state.inventory.remove(item)
                removed_coins += 1

        # Add item to inventory
        # Need to create a new instance of the item to add to inventory
        new_item = Apple()  # Assuming the shopkeeper gives an apple with every purchase
        new_item.can_be_carried = True
        game_state.add_item_to_inventory(new_item)
        if item_name_to_buy == "rope":
            new_item = Rope()
        elif item_name_to_buy == "matches":
            new_item = Matches()
        elif item_name_to_buy == "sword":
            new_item = Sword()
        elif item_name_to_buy == "armor":
            new_item = Armor()
        else:
            # Should not happen if item_name_to_buy is in self.wares
            return "An unexpected error occurred trying to sell the item."
        new_item.can_be_carried = True
        game_state.add_item_to_inventory(new_item)

        # Remove item from General Store's items list if it's a unique item or limited stock
        # For now, assume infinite stock in the store, but the player buys one instance.
        # If the store's stock should deplete, that logic would go here,
        # potentially removing item_object from game_state.current_room.items

        return (
            "\n[event]You bought a [item_name]"
            f"{new_item.get_name()}[/item_name] for {price} "
            "[item_name]coin(s)[/item_name] and got an extra "
            "[item_name]apple[/item_name] as a bonus![/event]"
        )
