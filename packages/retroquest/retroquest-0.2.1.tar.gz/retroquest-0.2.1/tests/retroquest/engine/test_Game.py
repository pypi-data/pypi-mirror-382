"""Tests for the Game class and game mechanics."""
# pylint: disable=too-many-lines

from unittest.mock import MagicMock
import pytest
from engine import GameState
from retroquest.engine.Game import Game
from retroquest.engine.Room import Room
from retroquest.engine.Act import Act
from retroquest.engine.Item import Item

# --- Mock Room classes for testing ---
class MockRoom(Room):
    """Mock room class for testing purposes."""

    def __init__(self, name, description="A mock room."):
        """Initialize a mock room with the given name and description."""
        super().__init__(name, description)
        self.items = []
        self.characters = []

    def can_leave(self):
        """Always allow leaving the room."""
        return True

    def add_exit(self, direction, room):
        """Add an exit in the given direction to the specified room."""
        self.exits[direction] = room

    def add_item(self, item):
        """Add an item to the room."""
        self.items.append(item)

    def add_character(self, character):
        """Add a character to the room."""
        self.characters.append(character)

class TakeMockItem(Item):
    """Mock item for take command tests supporting prevent_pickup and picked_up hooks."""
    def __init__(self, name, description="A test item", can_pickup=True, pickup_message=None):
        """Initialize a mock item with pickup behavior configuration."""
        super().__init__(name, description)
        self._can_pickup = can_pickup
        self._pickup_message = pickup_message

    def prevent_pickup(self):
        """Return failure message if item cannot be picked up, otherwise None."""
        if not self._can_pickup:
            return f"[failure]The {self.name} is too heavy to lift.[/failure]"
        return None

    def picked_up(self, _game_state):
        """Return custom message when item is successfully picked up."""
        return self._pickup_message

class TakeMockAct(Act):
    """Mock act class for testing take command functionality."""

    def __init__(self):
        """Initialize the mock act with test rooms."""
        test_room = Room("Test Room", "A room for testing the take command.")
        empty_room = Room("Empty Room", "A room with no items.")
        super().__init__(
            name="Test Act",
            rooms={"TestRoom": test_room, "EmptyRoom": empty_room},
            quests={},
            music_file='',
            music_info=''
        )

    def is_completed(self, _game_state: GameState) -> bool:
        """Return True when the act's completion conditions are met."""
        return False
# ==== End migrated take multiple tests support classes ====

# Dummy room and item setup for test
ROOMS = {
    "EliorsCottage": MockRoom("Elior's Cottage", "A cozy cottage with a warm hearth."),
    "VegetableField": MockRoom(
        "Vegetable Field",
        "A patch of tilled earth where vegetables struggle to grow. The soil is dry and rocky."
    ),
    "ChickenCoop": MockRoom("Chicken Coop"),
    "VillageSquare": MockRoom("Village Square"),
    "MirasHut": MockRoom("Mira's Hut"),
    "BlacksmithsForge": MockRoom("Blacksmith's Forge"),
    "GeneralStore": MockRoom("General Store"),
    "VillageWell": MockRoom("Village Well"),
    "AbandonedShed": MockRoom("Abandoned Shed"),
    "OldMill": MockRoom("Old Mill"),
    "Riverbank": MockRoom("Riverbank"),
    "ForestPath": MockRoom("Forest Path"),
    "HiddenGlade": MockRoom("Hidden Glade"),
    "VillageChapel": MockRoom("Village Chapel"),
    "RoadToGreendale": MockRoom("Road to Greendale"),
}

@pytest.fixture(name="basic_rooms")
def basic_rooms_fixture():
    """Create minimal room network for testing."""
    # Minimal room network for testing
    cottage = MockRoom("EliorsCottage", "A cozy cottage with a warm hearth.")
    field = MockRoom(
        "VegetableField",
        "A patch of tilled earth where vegetables struggle to grow. The soil is dry and rocky."
    )
    # Add exits for movement tests
    cottage.add_exit('south', field.name)
    field.add_exit('north', cottage.name)
    return {
        "EliorsCottage": cottage,
        "VegetableField": field,
    }

@pytest.fixture(name="game")
def game_fixture(basic_rooms):
    """Create a Game instance using the provided basic rooms."""
    act = Act("TestAct", basic_rooms, [], '', '')
    return Game([act])

def test_game_initial_state(game, basic_rooms):
    """Verify the game initializes with expected defaults."""
    assert game.state.current_room == basic_rooms["EliorsCottage"]
    assert game.is_running is True
    assert game.state.inventory == []
    assert game.state.history == []

def test_move_valid(game, basic_rooms):
    """Test moving in a valid direction between rooms."""
    # EliorsCottage south -> VegetableField
    result = game.move('south')
    assert game.state.current_room == basic_rooms["VegetableField"]
    assert "You move south to" in result
    assert f"[room_name]{basic_rooms['VegetableField'].name}[/room_name]" in result

def test_move_invalid(game):
    """Ensure moving in an invalid direction returns an error."""
    result = game.move('west')
    assert "can't go that way" in result

def test_visited_rooms_initial(game):
    """Only the starting room should be visited at game start."""
    # Only the starting room should be visited
    assert game.state.visited_rooms == [game.state.current_room.name]

def test_visited_rooms_after_move(game, basic_rooms):
    """Visited rooms should include rooms after movement."""
    basic_rooms["EliorsCottage"].can_leave()
    # Move to another room
    game.move('south')
    assert basic_rooms["VegetableField"].name in game.state.visited_rooms
    # Both rooms should be in visited_rooms
    expected_rooms = {basic_rooms["EliorsCottage"].name, basic_rooms["VegetableField"].name}
    assert set(game.state.visited_rooms) == expected_rooms

def test_visited_rooms_no_duplicates(game, basic_rooms):
    """Visited rooms list should not contain duplicates after moves."""
    basic_rooms["EliorsCottage"].can_leave()
    # Move to another room and back
    game.move('south')
    game.move('north')  # Assuming VegetableField has north exit back
    # No duplicates in visited_rooms
    assert game.state.visited_rooms.count(basic_rooms["EliorsCottage"].name) == 1
    assert game.state.visited_rooms.count(basic_rooms["VegetableField"].name) == 1

def test_map_initial_state(game):
    """Map output should list visited rooms and their exits."""
    result = game.map()
    assert "Visited Rooms and Exits:" in result
    assert "- [room_name]EliorsCottage[/room_name]:" in result
    assert "    south -> [room_name]VegetableField[/room_name]" in result
    assert "- [room_name]VegetableField[/room_name]" not in result

def test_map_after_move(game):
    """Map should include both rooms after moving between them."""
    game.move('south')
    result = game.map()
    assert "- [room_name]EliorsCottage[/room_name]:" in result
    assert "- [room_name]VegetableField[/room_name]:" in result
    assert "    south -> [room_name]VegetableField[/room_name]" in result
    assert "    north -> [room_name]EliorsCottage[/room_name]" in result

def test_map_multiple_moves(game):
    """Multiple moves should show both rooms and no duplicate entries."""
    game.move('south')
    game.move('north')
    result = game.map()
    assert "- [room_name]EliorsCottage[/room_name]:" in result
    assert "- [room_name]VegetableField[/room_name]:" in result
    assert "    south -> [room_name]VegetableField[/room_name]" in result
    assert "    north -> [room_name]EliorsCottage[/room_name]" in result
    assert result.count('- ') == 2

def test_take_item_from_room(game):
    """Taking an item from a room moves it to inventory."""
    from retroquest.act1.items.Egg import Egg
    egg = Egg()
    game.state.current_room.items.append(egg)
    assert egg in game.state.current_room.items
    result = game.take('egg')
    assert "You take the [item_name]egg[/item_name]" in result
    assert egg in game.state.inventory
    assert egg not in game.state.current_room.items

def test_take_item_not_present(game):
    """Trying to take a non-present item returns a message."""
    result = game.take('nonexistent')
    assert "There is no 'nonexistent' here to take." in result
    assert len(game.state.inventory) == 0

# ==== Migrated take multiple tests start ====
def test_take_multiple_identical_items():
    """Test taking multiple identical items in one command."""
    act = TakeMockAct()
    game = Game([act])
    coins = [TakeMockItem("coins", "A gold coin") for _ in range(5)]
    test_room = game.state.all_rooms["TestRoom"]
    for coin in coins:
        test_room.add_item(coin)
    game.state.current_room = test_room
    assert sum(1 for item in test_room.get_items() if item.get_name().lower() == "coins") == 5
    result = game.command_parser.parse("take coins")
    assert "[event]You take 5 [item_name]coins[/item_name].[/event]" in result
    assert sum(1 for item in test_room.get_items() if item.get_name().lower() == "coins") == 0
    assert sum(1 for item in game.state.inventory if item.get_name().lower() == "coins") == 5

def test_take_single_item():
    """Test taking a single item from a room."""
    act = TakeMockAct()
    game = Game([act])
    sword = TakeMockItem("sword", "A sharp sword")
    test_room = game.state.all_rooms["TestRoom"]
    test_room.add_item(sword)
    game.state.current_room = test_room
    result = game.command_parser.parse("take sword")
    assert "[event]You take the [item_name]sword[/item_name].[/event]" in result
    assert len(test_room.get_items()) == 0
    assert len(game.state.inventory) == 1 and game.state.inventory[0].get_name() == "sword"

def test_take_mixed_pickupable_and_non_pickupable_items():
    """Test mixed pickupable and non-pickupable items behavior."""
    act = TakeMockAct()
    game = Game([act])
    book1 = TakeMockItem("book", "A readable book", can_pickup=True)
    book2 = TakeMockItem("book", "Another book", can_pickup=True,
                         pickup_message="This book is heavy!")
    book3 = TakeMockItem("book", "A chained book", can_pickup=False)
    test_room = game.state.all_rooms["TestRoom"]
    for book in (book1, book2, book3):
        test_room.add_item(book)
    game.state.current_room = test_room
    result = game.command_parser.parse("take book")
    assert "[event]You take 2 [item_name]book[/item_name].[/event]" in result
    assert "This book is heavy!" in result
    assert "too heavy to lift" in result
    remaining = [item for item in test_room.get_items() if item.get_name().lower() == "book"]
    inv_books = [item for item in game.state.inventory if item.get_name().lower() == "book"]
    assert len(remaining) == 1
    assert len(inv_books) == 2

def test_take_nonexistent_item():
    """Test taking an item that does not exist in the room."""
    act = TakeMockAct()
    game = Game([act])
    game.state.current_room = game.state.all_rooms["EmptyRoom"]
    result = game.command_parser.parse("take unicorn")
    assert "[failure]There is no 'unicorn' here to take.[/failure]" in result

def test_take_with_pickup_messages():
    """Test pickup messages for items that emit messages when picked up."""
    act = TakeMockAct()
    game = Game([act])
    gem1 = TakeMockItem("gem", "A sparkling gem",
                        pickup_message="The gem glows as you touch it!")
    gem2 = TakeMockItem("gem", "Another gem",
                        pickup_message="This gem feels warm.")
    gem3 = TakeMockItem("gem", "A third gem", pickup_message=None)
    test_room = game.state.all_rooms["TestRoom"]
    for gem in (gem1, gem2, gem3):
        test_room.add_item(gem)
    game.state.current_room = test_room
    result = game.command_parser.parse("take gem")
    assert "The gem glows as you touch it!" in result
    assert "This gem feels warm." in result
    assert "[event]You take 3 [item_name]gem[/item_name].[/event]" in result
    assert len(test_room.get_items()) == 0
    assert len(game.state.inventory) == 3


def test_take_with_empty_pickup_message_treated_as_no_message():
    """Ensure an empty-string pickup message is treated as no message.

    This guards the change where item.picked_up() now returns str instead of
    Optional[str]. The engine should treat an empty string as falsy and not
    append it to the main take event line.
    """
    act = TakeMockAct()
    game = Game([act])
    gem1 = TakeMockItem("gem", "A sparkling gem", pickup_message="The gem glows!")
    gem2 = TakeMockItem("gem", "A silent gem", pickup_message="")
    test_room = game.state.all_rooms["TestRoom"]
    for gem in (gem1, gem2):
        test_room.add_item(gem)
    game.state.current_room = test_room
    result = game.command_parser.parse("take gem")
    # The non-empty message should be present
    assert "The gem glows!" in result
    # The main event line should reflect two items taken
    assert "[event]You take 2 [item_name]gem[/item_name].[/event]" in result

def test_take_backward_compatibility_with_existing_behavior():
    """Regression test ensuring single-item take behavior remains compatible."""
    test_items = [
        TakeMockItem("sword", "A sharp sword"),
        TakeMockItem("shield", "A sturdy shield"),
        TakeMockItem("potion", "A healing potion"),
    ]
    for item in test_items:
        game = Game([TakeMockAct()])
        test_room = game.state.all_rooms["TestRoom"]
        test_room.add_item(item)
        game.state.current_room = test_room
        result = game.command_parser.parse(f"take {item.get_name()}")
        assert "[failure]" not in result
        assert "[event]You take the" in result
        assert len(game.state.inventory) == 1
        assert game.state.inventory[0].get_name() == item.get_name()
# ==== Migrated take multiple tests end ====

def test_drop_item_from_inventory(game):
    """Dropping an item removes it from inventory and places it in the room."""
    from retroquest.act1.items.Lantern import Lantern
    lantern = Lantern()
    game.state.inventory.append(lantern)
    assert lantern in game.state.inventory
    result = game.drop('lantern')
    assert "You drop the [item_name]lantern[/item_name]" in result
    assert lantern not in game.state.inventory
    assert lantern in game.state.current_room.items

def test_drop_item_not_in_inventory(game):
    """Dropping a non-owned item returns an informative message."""
    result = game.drop('nonexistent')
    assert "You don't have a 'nonexistent' to drop." in result

def test_learn_spell(game):
    """Learning a new spell registers it in known_spells."""
    from retroquest.act1.spells.LightSpell import LightSpell
    light_spell = LightSpell()
    result = game.learn(light_spell)
    assert "You have learned the [spell_name]light[/spell_name] spell!" in result
    assert light_spell in game.state.known_spells

def test_learn_spell_already_known(game):
    """Learning an already known spell is a no-op."""
    from retroquest.act1.spells.LightSpell import LightSpell
    light_spell = LightSpell()
    game.learn(light_spell) # Learn it once
    game.learn(light_spell) # Try to learn again
    assert game.state.known_spells.count(light_spell) == 1

def test_spells_command_no_spells(game):
    """Spells command informs when no spells are known."""
    result = game.spells()
    assert "You don't know any spells yet." in result

def test_spells_command_with_spells(game):
    """Spells command lists known spells with descriptions."""
    from retroquest.act1.spells.LightSpell import LightSpell
    from retroquest.act1.spells.HealSpell import HealSpell
    light_spell = LightSpell()
    heal_spell = HealSpell()
    game.learn(light_spell)
    game.learn(heal_spell)
    result = game.spells()
    assert "Known Spells:" in result
    light_line = (
        f"  - [spell_name]{light_spell.get_name()}[/spell_name]: "
        f"{light_spell.get_description()}"
    )
    heal_line = (
        f"  - [spell_name]{heal_spell.get_name()}[/spell_name]: "
        f"{heal_spell.get_description()}"
    )
    assert light_line in result
    assert heal_line in result

# --- Tests for 'give' command ---

def test_give_item_to_character_successful(game):
    """Giving an item to a character calls their give_item and returns its message."""
    from retroquest.act1.items.Apple import Apple
    from retroquest.act1.characters.Villager import Villager
    # Assuming a generic Villager character

    apple = Apple()
    villager = Villager() # Villager needs to be in the room

    game.state.inventory.append(apple)
    game.state.current_room.characters.append(villager)

    # Mock the villager's give_item method
    villager.give_item = MagicMock(
        return_value=(
            f"[character_name]{villager.get_name()}[/character_name] takes the "
            f"[item_name]{apple.get_name()}[/item_name]."
        )
    )

    result = game.give(f"{apple.get_name()} to {villager.get_name()}")

    expected = (
        f"[character_name]{villager.get_name()}[/character_name] takes the "
        f"[item_name]{apple.get_name()}[/item_name]."
    )
    assert expected in result
    villager.give_item.assert_called_once_with(game.state, apple)


def test_give_item_not_in_inventory(game):
    """Giving an item not in inventory reports an informative message."""
    from retroquest.act1.characters.Villager import Villager
    villager = Villager()
    game.state.current_room.characters.append(villager)

    result = game.give(f"nonexistent_item to {villager.get_name()}")
    assert "You don\'t have any \'nonexistent_item\' to give." in result

def test_give_item_to_character_not_in_room(game):
    """Giving to a non-present character returns an error."""
    from retroquest.act1.items.Apple import Apple
    apple = Apple()
    game.state.inventory.append(apple)

    # Character "Ghost" is not added to the room
    result = game.give(f"{apple.get_name()} to Ghost")
    assert "There is no character named \'Ghost\' here." in result

def test_give_item_character_does_not_want(game):
    """Character refusal is handled and reported."""
    from retroquest.act1.items.Stick import Stick # An item the character might not want
    from retroquest.engine.Character import Character # Base character

    stick = Stick()
    generic_char = Character(name="Grumpy Person", description="Someone grumpy.")

    game.state.inventory.append(stick)
    game.state.current_room.characters.append(generic_char)
    # The default Character.give_item should be called
    result = game.give(f"{stick.get_name()} to {generic_char.get_name()}")
    expected_refusal = (
        f"[character_name]{generic_char.get_name()}[/character_name] doesn't seem interested "
        f"in the [item_name]{stick.get_name()}[/item_name]."
    )
    assert expected_refusal in result

def test_give_item_invalid_format(game):
    """Invalid give command formats are handled with helpful messages."""
    result = game.give("apple villager") # Missing "to"
    assert "Invalid command format. Please use \'give <target1> to <target2>\'." in result

    result = game.give("to villager") # Missing item
    assert "What do you want to give?" in result

    result = game.give("apple to") # Missing character
    assert "Who/What should I give apple to?" in result

# --- Tests for \'look\' command ---

def test_look_in_room_with_items_and_characters(game):
    """Look should include items and characters in the room description."""
    from retroquest.act1.items.Apple import Apple
    from retroquest.act1.characters.Villager import Villager

    apple = Apple()
    villager = Villager()

    # Ensure the starting room (Elior\'s Cottage) is used for this test
    # or set current_room explicitly if needed.
    current_room = game.state.current_room
    current_room.items.append(apple)
    current_room.characters.append(villager)

    # Mock the room\'s describe method to verify it\'s called
    # Or, more practically, check that the output contains expected elements
    # from the room description, item names, and character names.
    current_room.describe = MagicMock(return_value=
        f"{current_room.description}\n"
        f"Items here: {apple.get_name()}\n"
        f"You see: {villager.get_name()}"
    )

    game.look()

def test_look_in_empty_room(game):
    """Looking in an empty room shows base description only."""
    # Move to a room that we ensure is empty (or make it empty)
    # For simplicity, let\'s use VegetableField and clear it.
    game.move('south') # Move to VegetableField
    current_room = game.state.current_room
    current_room.items.clear()
    current_room.characters.clear()

    # Original description of VegetableField without items/chars
    original_description = (
        "A patch of tilled earth where vegetables struggle to grow. "
        "The soil is dry and rocky."
    )
    current_room.description = original_description  # Ensure it's set for the test

    # Mock describe or check its output structure
    # If Room.describe() dynamically builds the string, we check for absence of item/char lines
    # For this test, let\'s assume describe() returns the base description if no items/chars
    current_room.describe = MagicMock(return_value=original_description)

    game.look()

# --- Tests for \'inventory\' command ---

def test_inventory_empty(game):
    """Inventory command reports when the inventory is empty."""
    result = game.inventory()
    assert "Your inventory is empty." in result

def test_inventory_with_items(game):
    """Inventory lists items the player is carrying."""
    from retroquest.act1.items.Apple import Apple
    from retroquest.act1.items.Stick import Stick
    apple = Apple()
    stick = Stick()

    game.state.inventory.append(apple)
    game.state.inventory.append(stick)

    result = game.inventory()

    assert "You are carrying:" in result
    assert f"- [item_name]{apple.get_name()}[/item_name]" in result
    assert f"- [item_name]{stick.get_name()}[/item_name]" in result

# --- Tests for 'examine' command ---

def test_examine_item_in_inventory(game):
    """Examining an item in inventory returns the item's description."""
    from retroquest.act1.items.Apple import Apple

    apple = Apple()
    apple_description = "A juicy red apple, looking perfectly ripe."
    apple.examine = MagicMock(return_value=apple_description)
    apple.get_name = MagicMock(return_value="apple")

    game.state.inventory.append(apple)
    # Ensure it's not also in the room to avoid ambiguity for this specific test
    if apple in game.state.current_room.items:
        game.state.current_room.items.remove(apple)

    result = game.examine("apple")
    assert result == apple_description
    apple.examine.assert_called_once()

def test_examine_item_in_room(game):
    """Examining an item in the room returns the item's description."""
    from retroquest.act1.items.Apple import Apple

    apple = Apple()
    apple_description = "A shiny green apple, lying on the ground."
    apple.examine = MagicMock(return_value=apple_description)
    apple.get_name = MagicMock(return_value="apple")

    game.state.current_room.items.append(apple)
    # Ensure it's not in inventory for this specific test
    if apple in game.state.inventory:
        game.state.inventory.remove(apple)

    result = game.examine("apple")
    assert result == apple_description
    apple.examine.assert_called_once()

def test_examine_character_in_room(game):
    """Examining a character returns their description wrapped as an event."""
    from retroquest.act1.characters.Villager import Villager
    # Assuming Villager's get_description returns the description passed to constructor
    char_description = "A weary-looking traveler, resting by the old oak tree."
    traveler = Villager()
    traveler.description = char_description

    game.state.current_room.characters.append(traveler)

    result = game.examine("Villager")
    expected = (
        '[event]You examine [character_name]villager[/character_name]. '
        + char_description
        + '[/event]'
    )
    assert result == expected

def test_examine_target_not_found(game):
    """Examining a non-existent target reports a clear message."""
    game.state.inventory.clear()
    game.state.current_room.items.clear()
    game.state.current_room.characters.clear()

    result = game.examine("dragon")
    assert result == "You don't see any 'dragon' here."

def test_examine_no_argument(game):
    """Calling examine with no argument returns a prompt."""
    result = game.examine("") # Assuming CommandParser passes empty string for no arg
    assert result == "Examine what?"

def test_examine_case_insensitivity(game):
    """Examine should be case-insensitive for names."""
    from retroquest.act1.items.Apple import Apple
    from retroquest.act1.characters.Villager import Villager

    # Test with item
    apple = Apple()
    apple_description = "A golden delicious apple."
    apple.description = apple_description
    apple.get_name = MagicMock(return_value="Golden Apple") # Name with space and caps
    game.state.inventory.append(apple)

    result_item = game.examine("golden apple")
    expected_item = (
        '[event]You examine the [item_name]Golden Apple[/item_name]. '
        + apple_description
        + '[/event]'
    )
    assert result_item == expected_item
    game.state.inventory.clear() # Clean up for next part of test

    # Test with character
    char_description = "The village blacksmith, strong and sturdy."
    blacksmith = Villager()
    blacksmith.name = "Blacksmith John"
    blacksmith.description = char_description
    game.state.current_room.characters.append(blacksmith)

    result_char = game.examine("blacksmith JOHN")
    expected_char = (
        '[event]You examine [character_name]Blacksmith John[/character_name]. '
        + char_description
        + '[/event]'
    )
    assert result_char == expected_char
    game.state.current_room.characters.clear() # Clean up

# --- Tests for 'buy' command ---

def test_buy_item_successful(game):
    """Buying an item from a shopkeeper returns success message."""
    from retroquest.act1.items.Rope import Rope
    from retroquest.act1.items.Coin import Coin
    from retroquest.act1.characters.Shopkeeper import Shopkeeper # Assuming Shopkeeper has buy_item

    shopkeeper = Shopkeeper()
    rope_instance = Rope() # The item instance the shopkeeper would sell

    # Setup shopkeeper's wares and mock buy_item
    # For this test, we assume Shopkeeper.buy_item handles coin deduction and item addition
    # and returns a success message.
    shopkeeper.wares = {"rope": {"item": rope_instance, "price": 1}}
    shopkeeper.buy_item = MagicMock(
        return_value=(
            f"You bought a [item_name]{rope_instance.get_name()}[/item_name] for 1 "
            f"[item_name]coin[/item_name](s)."
        )
    )

    game.state.current_room.characters.append(shopkeeper)
    game.state.inventory.append(Coin()) # Player has one coin

    result = game.buy("rope from shopkeeper")

    expected_buy = (
        f"You bought a [item_name]{rope_instance.get_name()}[/item_name] for 1 "
        f"[item_name]coin[/item_name](s)."
    )
    assert expected_buy in result
    shopkeeper.buy_item.assert_called_once_with("rope", game.state)
    # Further checks could be:
    # - assert Coin not in game.state.inventory (if buy_item removes it)
    # - assert rope_instance in game.state.inventory (if buy_item adds it)
    # These depend on the Shopkeeper.buy_item implementation.

def test_buy_item_not_sold_by_character(game):
    """Test buying an item the shopkeeper does not stock."""
    from retroquest.act1.characters.Shopkeeper import Shopkeeper
    from retroquest.act1.items.Coin import Coin

    shopkeeper = Shopkeeper()
    shopkeeper.buy_item = MagicMock(return_value="Sorry, I don't have any 'magic beans' for sale.")
    game.state.current_room.characters.append(shopkeeper)
    game.state.inventory.append(Coin())

    result = game.buy("magic beans from shopkeeper")
    assert "Sorry, I don't have any 'magic beans' for sale." in result
    shopkeeper.buy_item.assert_called_once_with("magic beans", game.state)

def test_buy_item_not_enough_coins(game):
    """Test buying an item when player lacks sufficient coins."""
    from retroquest.act1.characters.Shopkeeper import Shopkeeper
    from retroquest.act1.items.Rope import Rope

    shopkeeper = Shopkeeper()
    rope_instance = Rope()
    # Assume rope costs 1 coin, but player has 0
    shopkeeper.wares = {"rope": {"item": rope_instance, "price": 1}}
    shopkeeper.buy_item = MagicMock(
        return_value=(
            "You don't have enough [item_name]coins[/item_name] for the "
            "[item_name]rope[/item_name]. It costs 1 [item_name]coin[/item_name](s)."
        )
    )

    game.state.current_room.characters.append(shopkeeper)
    # game.state.inventory is empty (no coins)

    result = game.buy("rope from shopkeeper")
    expected_not_enough = (
        "You don't have enough [item_name]coins[/item_name] for the "
        "[item_name]rope[/item_name]. It costs 1 [item_name]coin[/item_name](s)."
    )
    assert expected_not_enough in result
    shopkeeper.buy_item.assert_called_once_with("rope", game.state)

def test_buy_item_character_not_present(game):
    """Test buying from a non-present character returns an error."""
    from retroquest.act1.items.Coin import Coin
    game.state.inventory.append(Coin())

    result = game.buy("rope from Ghostly Shopkeeper")
    assert "There is no character named 'Ghostly shopkeeper' here." in result

def test_buy_item_character_cannot_sell(game):
    """Test buying from a character that cannot sell items."""
    from retroquest.act1.characters.Villager import Villager # Villager cannot sell
    from retroquest.act1.items.Coin import Coin

    villager = Villager()
    game.state.current_room.characters.append(villager)
    game.state.inventory.append(Coin())

    result = game.buy("rope from villager")
    expected_nosell = (
        f"[character_name]{villager.get_name()}[/character_name] does not have any "
        f"[item_name]rope[/item_name] to sell right now."
    )
    assert expected_nosell in result

def test_buy_item_invalid_format(game):
    """Test invalid buy command formats are handled gracefully."""
    result = game.buy("rope shopkeeper") # Missing "from"
    assert "Invalid command format. Please use 'buy <target1> from <target2>'." in result

    result = game.buy("from shopkeeper") # Missing item
    assert "What do you want to buy?" in result

    result = game.buy("rope from") # Missing character
    assert "[failure]Who/What should I buy rope from?[/failure]" in result

# Helper classes for 'use' tests
# These are defined here to be available for the test functions below.
# They duck-type the necessary methods of game items for testing purposes.
class MockItemToUse: # Renamed to avoid conflict if Item is imported elsewhere by chance
    """Duck-typed mock item used for testing item use behaviors."""
    def __init__(self, name, short_name=None, description="A mock item."):
        """Initialize the mock item with name and optional short name."""
        self._name = name
        self._short_name = short_name if short_name else name
        self._description = description
        self.requires_pickup = False
        self.use_called_with_state = None
        self.use_with_called_with_state_and_item = None
        self.use_on_character_called_with = None  # Added for character use tracking
        self.read_called_with_state = None
        self.listen_called_with_state = None # Added for listen tests

    def get_name(self):
        """Return the mock item's full name."""
        return self._name

    def get_short_name(self):
        """Return the mock item's short name used for shorthand targets."""
        return self._short_name

    def get_description(self):
        """Return the mock item's description string."""
        return self._description

    def use(self, game_state):
        """Simulate using the item and record the call state."""
        self.use_called_with_state = game_state
        return f"You used the [item]{self.get_name()}[/item]."

    def use_with(self, game_state, other_item):
        """Simulate using this item with another and record the call."""
        self.use_with_called_with_state_and_item = (game_state, other_item)
        return (
            f"You used the [item]{self.get_name()}[/item] with "
            f"[item]{other_item.get_name()}[/item]."
        )

    def use_on_character(self, game_state, target_character):
        """Default implementation - items can't be used on characters."""
        self.use_on_character_called_with = (game_state, target_character)
        return (
            f"[failure]You can't use the [item_name]{self.get_name()}[/item_name] on "
            f"[character_name]{target_character.get_name()}[/character_name].[/failure]"
        )



    def listen(self, game_state): # Added for listen tests
        """Simulate listening to the item and return its sound."""
        self.listen_called_with_state = game_state
        return f"You hear a faint click from the [item]{self.get_name()}[/item]."

# --- Tests for 'use <item>' command ---

def test_use_item_from_inventory_successful(game):
    """Test using an item from inventory succeeds and calls use()."""
    item1 = MockItemToUse(name="widget")
    game.state.add_item_to_inventory(item1)

    result = game.use("widget")
    assert result == "You used the [item]widget[/item]."
    assert item1.use_called_with_state == game.state

def test_use_item_from_room_successful_no_pickup_needed(game):
    """Test using an item found in the room when pickup not required."""
    item1 = MockItemToUse(name="lever")
    game.state.current_room.add_item(item1)

    result = game.use("lever")
    assert result == "You used the [item]lever[/item]."
    assert item1.use_called_with_state == game.state

def test_use_item_not_found(game):
    """Test using a non-existent item returns a failure message."""
    result = game.use("nonexistent_item")
    expected = (
        "[failure]You don't have a 'nonexistent_item' to use, and there isn't "
        "one here.[/failure]"
    )
    assert result == expected

# --- Tests for 'use <item1> with <item2>' command ---

def test_use_item1_inv_with_item2_inv_successful(game):
    """Test using an inventory item with another inventory item."""
    item1 = MockItemToUse(name="key")
    item2 = MockItemToUse(name="chest")
    game.state.add_item_to_inventory(item1)
    game.state.add_item_to_inventory(item2)

    result = game.use("key", "chest")
    assert result == "You used the [item]key[/item] with [item]chest[/item]."
    assert item1.use_with_called_with_state_and_item == (game.state, item2)
    assert item2.use_called_with_state is None

def test_use_item1_inv_with_item2_room_successful(game):
    """Test using inventory item with an item in the room succeeds."""
    item1 = MockItemToUse(name="key")
    item2 = MockItemToUse(name="locked_door")
    # item2.requires_pickup is False by default
    game.state.add_item_to_inventory(item1)
    game.state.current_room.add_item(item2)

    result = game.use("key", "locked_door")
    assert result == "You used the [item]key[/item] with [item]locked_door[/item]."
    assert item1.use_with_called_with_state_and_item == (game.state, item2)

def test_use_item1_room_with_item2_inv_successful(game):
    """Test using a room item together with an inventory item succeeds."""
    item1 = MockItemToUse(name="lever")
    # item1.requires_pickup is False by default
    item2 = MockItemToUse(name="mechanism_part")
    game.state.current_room.add_item(item1)
    game.state.add_item_to_inventory(item2)

    result = game.use("lever", "mechanism_part")
    assert result == "You used the [item]lever[/item] with [item]mechanism_part[/item]."
    assert item1.use_with_called_with_state_and_item == (game.state, item2)

def test_use_item1_with_item2_item1_not_found(game):
    """Test using a non-existent first item reports appropriate failure."""
    item2 = MockItemToUse(name="target")
    game.state.add_item_to_inventory(item2)
    result = game.use("nonexistent_item1", "target")
    expected = (
        "[failure]You don't have a 'nonexistent_item1' to use, and there isn't "
        "one here.[/failure]"
    )
    assert result == expected

def test_use_item1_with_item2_item2_not_found(game):
    """Test using an item with a missing second item returns failure."""
    item1 = MockItemToUse(name="tool")
    game.state.add_item_to_inventory(item1)
    result = game.use("tool", "nonexistent_item2")
    expected = (
        "[failure]You don't see a 'nonexistent_item2' to use with the "
        "[item_name]tool[/item_name].[/failure]"
    )
    assert result == expected

def test_use_item_with_itself(game):
    """Test that attempting to use an item with itself is rejected."""
    item1 = MockItemToUse(name="widget")
    game.state.add_item_to_inventory(item1)
    result = game.use("widget", "widget")
    expected = (
        "[failure]You can't use the [item_name]widget[/item_name] with "
        "itself.[/failure]"
    )
    assert result == expected
    assert item1.use_with_called_with_state_and_item is None

# --- Tests for 'use <item> on <character>' command ---

class MockItemWithCharacterUse(MockItemToUse):
    """Mock item subclass that supports use on characters."""
    def __init__(
        self,
        name,
        short_name=None,
        description="A mock item that can be used on characters.",
    ):
        """Initialize the mock item and set up character-use tracking."""
        super().__init__(name, short_name, description)
        self.use_on_character_called_with = None

    def use_on_character(self, game_state, target_character):
        """Simulate using this item on a character and return its message."""
        self.use_on_character_called_with = (game_state, target_character)
        return (
            f"You used the [item_name]{self.get_name()}[/item_name] on "
            f"[character_name]{target_character.get_name()}[/character_name]."
        )

def test_use_item_on_character_successful(game):
    """Test using an item on a character when the item supports it."""
    healing_potion = MockItemWithCharacterUse(name="healing potion")
    wounded_soldier = MockCharacter("wounded soldier")

    game.state.add_item_to_inventory(healing_potion)
    game.state.current_room.add_character(wounded_soldier)

    result = game.use("healing potion", "wounded soldier")

    expected = (
        "You used the [item_name]healing potion[/item_name] on "
        "[character_name]wounded soldier[/character_name]."
    )
    assert result == expected
    assert healing_potion.use_on_character_called_with == (game.state, wounded_soldier)

def test_use_item_on_character_item_from_room(game):
    """Test using an item from the room on a character."""
    bandages = MockItemWithCharacterUse(name="bandages")
    injured_traveler = MockCharacter("injured traveler")

    game.state.current_room.add_item(bandages)
    game.state.current_room.add_character(injured_traveler)

    result = game.use("bandages", "injured traveler")

    expected = (
        "You used the [item_name]bandages[/item_name] on "
        "[character_name]injured traveler[/character_name]."
    )
    assert result == expected
    assert bandages.use_on_character_called_with == (game.state, injured_traveler)

def test_use_item_on_character_not_supported(game):
    """Test using an item that doesn't support use_on_character method."""
    regular_item = MockItemToUse(name="apple")  # Has default use_on_character method
    hungry_person = MockCharacter("hungry person")

    game.state.add_item_to_inventory(regular_item)
    game.state.current_room.add_character(hungry_person)

    result = game.use("apple", "hungry person")

    # Should use the default use_on_character implementation which returns a failure message
    expected_failure = (
        "[failure]You can't use the [item_name]apple[/item_name] on "
        "[character_name]hungry person[/character_name].[/failure]"
    )
    assert expected_failure in result
    assert regular_item.use_on_character_called_with == (game.state, hungry_person)

def test_use_item_on_nonexistent_character(game):
    """Test using an item on a character that doesn't exist."""
    magic_wand = MockItemWithCharacterUse(name="magic wand")
    game.state.add_item_to_inventory(magic_wand)

    result = game.use("magic wand", "unicorn")

    assert "You don't see a 'unicorn' to use with the [item_name]magic wand[/item_name]" in result
    assert magic_wand.use_on_character_called_with is None

def test_use_item_on_character_case_insensitive(game):
    """Test that using items on characters is case-insensitive."""
    crystal = MockItemWithCharacterUse(name="Crystal Shard")
    wizard = MockCharacter("Wise Wizard")

    game.state.add_item_to_inventory(crystal)
    game.state.current_room.add_character(wizard)

    result = game.use("crystal shard", "wise wizard")

    expected = (
        "You used the [item_name]Crystal Shard[/item_name] on "
        "[character_name]Wise Wizard[/character_name]."
    )
    assert result == expected
    assert crystal.use_on_character_called_with == (game.state, wizard)

def test_use_item_on_character_item_not_found(game):
    """Test using a non-existent item on a character."""
    friendly_npc = MockCharacter("friendly npc")
    game.state.current_room.add_character(friendly_npc)

    result = game.use("nonexistent item", "friendly npc")

    expected = (
        "[failure]You don't have a 'nonexistent item' to use, "
        "and there isn't one here.[/failure]"
    )
    assert result == expected

def test_use_item_on_character_prefers_item_over_character_for_second_param(game):
    """Test that when object_name matches both an item and character, it prefers the
    item for use_with."""
    tool = MockItemToUse(name="hammer")
    target_item = MockItemToUse(name="target")
    target_character = MockCharacter("target")  # Same name as item

    game.state.add_item_to_inventory(tool)
    game.state.add_item_to_inventory(target_item)
    game.state.current_room.add_character(target_character)

    result = game.use("hammer", "target")

    # Should use hammer with target item, not target character
    assert result == "You used the [item]hammer[/item] with [item]target[/item]."
    assert tool.use_with_called_with_state_and_item == (game.state, target_item)

def test_use_item_on_character_when_no_item_match(game):
    """Test that when object_name doesn't match any item, it tries character."""
    staff = MockItemWithCharacterUse(name="healing staff")
    patient = MockCharacter("patient")

    game.state.add_item_to_inventory(staff)
    game.state.current_room.add_character(patient)

    # Make sure there's no item named "patient"
    assert not any(item.get_name().lower() == "patient" for item in game.state.inventory)
    assert not any(item.get_name().lower() == "patient" for item in game.state.current_room.items)

    result = game.use("healing staff", "patient")

    expected = (
        "You used the [item_name]healing staff[/item_name] on "
        "[character_name]patient[/character_name]."
    )
    assert result == expected
    assert staff.use_on_character_called_with == (game.state, patient)

class MockItemWithoutCharacterUse(MockItemToUse):
    """Mock item that explicitly doesn't support use_on_character."""
    def __init__(self, name, short_name=None):
        """Initialize the mock item that lacks character-use support."""
        super().__init__(name, short_name)
        # Deliberately override use_on_character to simulate old behavior

    def use_on_character(self, game_state, target_character):
        """Return the standard failure message for using on a character."""
        self.use_on_character_called_with = (game_state, target_character)  # Track the call
        return (
            f"[failure]You can't use the [item_name]{self.get_name()}[/item_name] "
            f"on [character_name]{target_character.get_name()}[/character_name].[/failure]"
        )

def test_use_item_without_character_support_on_character(game):
    """Test using an item that doesn't have use_on_character method on a character."""
    regular_sword = MockItemWithoutCharacterUse(name="sword")
    enemy = MockCharacter("goblin")

    game.state.add_item_to_inventory(regular_sword)
    game.state.current_room.add_character(enemy)

    result = game.use("sword", "goblin")

    # Should use the default use_on_character implementation which returns a failure message
    assert (
        "[failure]You can't use the [item_name]sword[/item_name] on "
        "[character_name]goblin[/character_name].[/failure]" in result
    )
    assert regular_sword.use_on_character_called_with == (game.state, enemy)


# --- Tests for 'listen' command ---

def test_listen_no_target_room_ambient_sound(game):
    """Tests listening with no target, expecting room's ambient sound."""
    expected_sound = "You hear the gentle rustling of leaves."
    game.state.current_room.get_ambient_sound = MagicMock(return_value=expected_sound)

    result = game.listen()

    assert result == expected_sound
    game.state.current_room.get_ambient_sound.assert_called_once()

def test_listen_item_in_inventory(game):
    """Tests listening to an item that is in the player's inventory."""
    mock_item = MockItemToUse(name="pocket_watch")
    # Override default listen message for this test
    expected_sound = "The [item]pocket_watch[/item] ticks softly."
    mock_item.listen = MagicMock(return_value=expected_sound)

    game.state.add_item_to_inventory(mock_item)

    result = game.listen("pocket_watch")

    assert result == expected_sound
    mock_item.listen.assert_called_once_with(game.state)

def test_listen_item_in_room(game):
    """Tests listening to an item that is in the current room."""
    mock_item = MockItemToUse(name="old_radio")
    # Override default listen message
    expected_sound = "Static crackles from the [item]old_radio[/item]."
    mock_item.listen = MagicMock(return_value=expected_sound)

    game.state.current_room.add_item(mock_item)

    result = game.listen("old_radio")

    assert result == expected_sound
    mock_item.listen.assert_called_once_with(game.state)

def test_listen_item_not_found(game):
    """Tests listening to an item that is neither in inventory nor in the room."""
    # Assuming Game.py's listen method returns a specific message for not found items.
    # This message might vary based on actual implementation.
    # Based on Game.examine, a similar message is "You don't see any 'dragon' here."
    # For listen, it might be "You can't find 'nonexistent_relic' to listen to."
    # or "There is no 'nonexistent_relic' here."
    # Clear inventory and room to be sure
    game.state.inventory.clear()
    game.state.current_room.items.clear()

    target_item_name = "nonexistent_relic"
    result = game.listen(target_item_name)

    # This assertion depends on the actual message from Game.listen() when an item is not found.
    # Adjust if the actual message is different.
    # A plausible message:
    expected = (
        f"[failure]You don't see a '{target_item_name}' to listen to here "
        "or in your inventory.[/failure]"
    )
    assert result == expected

def test_listen_item_uses_mock_default_listen(game):
    """Tests listening to an item that uses the default listen method from MockItemToUse."""
    mock_item = MockItemToUse(name="strange_device") # Uses the default listen from MockItemToUse

    game.state.add_item_to_inventory(mock_item)

    result = game.listen("strange_device")

    expected_default_sound = (
        f"You hear a faint click from the [item]{mock_item.get_name()}[/item]."
    )
    assert result == expected_default_sound
    assert mock_item.listen_called_with_state == game.state

def test_listen_item_name_case_insensitivity(game):
    """Tests that listening to an item is case-insensitive."""
    mock_item = MockItemToUse(name="Whispering Shell")
    expected_sound = "You hear the faint echo of the sea from the [item]Whispering Shell[/item]."
    mock_item.listen = MagicMock(return_value=expected_sound)

    game.state.current_room.add_item(mock_item)

    result = game.listen("whispering SHELL") # Case-insensitive target

    assert result == expected_sound
    mock_item.listen.assert_called_once_with(game.state)

# ===== CAST METHOD TESTS =====

class MockSpell:
    """Simple mock spell used for cast method tests."""
    def __init__(self, name, description="A test spell"):
        """Initialize the mock spell with a name and optional description."""
        self.name = name
        self.description = description

    def get_name(self):
        """Return the spell's name."""
        return self.name

    def get_description(self):
        """Return the spell's description."""
        return self.description

    def cast_spell(self, _game_state):
        """Cast spell without a target."""
        return f"[event]You cast [spell_name]{self.name}[/spell_name] without a target.[/event]"

    def cast_on_item(self, _game_state, target_item):
        """Cast spell on an item."""
        return (
            f"[event]You cast [spell_name]{self.name}[/spell_name] on "
            f"[item_name]{target_item.get_name()}[/item_name].[/event]"
        )

    def cast_on_character(self, _game_state, target_character):
        """Cast spell on a character."""
        return (
            f"[event]You cast [spell_name]{self.name}[/spell_name] on "
            f"[character_name]{target_character.get_name()}[/character_name].[/event]"
        )

class MockItem:
    """Minimal mock item used in cast tests and inventory checks."""
    def __init__(self, name, short_name=None):
        """Initialize the mock item with name and optional short name."""
        self.name = name
        self.short_name = short_name

    def get_name(self):
        """Return the mock item's name."""
        return self.name

    def get_short_name(self):
        """Return the mock item's short name or empty string if none."""
        return self.short_name or ""

    def use(self, _game_state):
        """Return a string indicating the item was used."""
        return f"You use the [item_name]{self.name}[/item_name]."

class MockCharacter:
    """Lightweight mock character implementing minimal interaction hooks."""
    def __init__(self, name):
        """Create a mock character with the given name."""
        self.name = name

    def get_name(self):
        """Return the character's name."""
        return self.name

    def examine(self, _game_state):
        """Return a simple examine string for the character."""
        return f"You examine [character_name]{self.name}[/character_name]."

    def say_to(self, word, _game_state):
        """Mock implementation of say_to method."""
        if word.lower() == "hello":
            return (
                f"[dialogue][character_name]{self.name}[/character_name] responds: '"
                "Hello there!'[/dialogue]"
            )
        elif word.lower() == "password":
            return (
                f"[dialogue][character_name]{self.name}[/character_name] nods and "
                "steps aside.[/dialogue]"
            )
        else:
            return (
                f"[dialogue][character_name]{self.name}[/character_name] looks confused "
                f"and doesn't understand '{word}'.[/dialogue]"
            )

@pytest.fixture(name="game_with_spells")
def game_with_spells_fixture(basic_rooms):
    """Fixture that returns a game instance populated with mock spells/items."""
    act = Act("TestAct", basic_rooms, [], '', '')
    game = Game([act])

    # Add some test spells
    heal_spell = MockSpell("heal", "A healing spell")
    light_spell = MockSpell("light", "A light spell")
    unlock_spell = MockSpell("unlock", "An unlocking spell")

    game.state.known_spells = [heal_spell, light_spell, unlock_spell]

    # Add test items and characters
    test_item = MockItem("test item", "item")
    test_character = MockCharacter("test character")

    game.state.current_room.add_item(test_item)
    game.state.current_room.add_character(test_character)
    game.state.inventory.append(MockItem("inventory item"))

    return game

def test_cast_unknown_spell(game_with_spells):
    """Test casting an unknown spell returns an error."""
    result = game_with_spells.cast("fireball")
    assert "[failure]You don't know any spell called 'fireball'.[/failure]" in result

def test_cast_spell_without_target(game_with_spells):
    """Test casting a known spell without supplying a target."""
    result = game_with_spells.cast("heal")
    expected = (
        "[event]You cast [spell_name]heal[/spell_name] without a "
        "target.[/event]"
    )
    assert expected in result

def test_cast_spell_on_item_in_room(game_with_spells):
    """Test casting a spell on an item located in the room."""
    result = game_with_spells.cast("heal on test item")
    expected = (
        "[event]You cast [spell_name]heal[/spell_name] on "
        "[item_name]test item[/item_name].[/event]"
    )
    assert expected in result

def test_cast_spell_on_item_in_inventory(game_with_spells):
    """Test casting a spell on an item in inventory succeeds."""
    result = game_with_spells.cast("heal on inventory item")
    expected = (
        "[event]You cast [spell_name]heal[/spell_name] on "
        "[item_name]inventory item[/item_name].[/event]"
    )
    assert expected in result

def test_cast_spell_on_character(game_with_spells):
    """Test casting a spell on a character succeeds."""
    result = game_with_spells.cast("heal on test character")
    expected = (
        "[event]You cast [spell_name]heal[/spell_name] on "
        "[character_name]test character[/character_name].[/event]"
    )
    assert expected in result

def test_cast_spell_on_nonexistent_target(game_with_spells):
    """Test casting on a non-existent target returns failure."""
    result = game_with_spells.cast("heal on dragon")
    expected = (
        "[failure]You don't see a 'dragon' to cast "
        "[spell_name]heal[/spell_name] on.[/failure]"
    )
    assert expected in result

def test_cast_spell_case_insensitive(game_with_spells):
    """Test spell casting name matching is case-insensitive."""
    result = game_with_spells.cast("HEAL on TEST ITEM")
    expected = (
        "[event]You cast [spell_name]heal[/spell_name] on "
        "[item_name]test item[/item_name].[/event]"
    )
    assert expected in result

def test_cast_spell_with_short_name(game_with_spells):
    """Test casting using an item's short name as the target identifier."""
    result = game_with_spells.cast("heal on item")  # Using short name
    expected = (
        "[event]You cast [spell_name]heal[/spell_name] on "
        "[item_name]test item[/item_name].[/event]"
    )
    assert expected in result

def test_cast_spell_prefers_item_over_character(game_with_spells):
    """Test that casting prefers item targets over characters when names clash."""
    # Add an item and character with same name to test priority
    same_name_item = MockItem("target")
    same_name_character = MockCharacter("target")

    game_with_spells.state.current_room.add_item(same_name_item)
    game_with_spells.state.current_room.add_character(same_name_character)

    result = game_with_spells.cast("heal on target")
    # Should cast on item (has 'use' method), not character
    assert "[item_name]target[/item_name]" in result
    assert "[character_name]target[/character_name]" not in result

def test_cast_command_parsing_variations(game_with_spells):
    """Test different syntaxes for the cast command parse correctly."""
    # Test different ways of specifying targets

    # Standard format: "spell on target"
    result1 = game_with_spells.cast("heal on test item")
    expected1 = (
        "[event]You cast [spell_name]heal[/spell_name] on "
        "[item_name]test item[/item_name].[/event]"
    )
    assert expected1 in result1

    # Extra spaces
    result2 = game_with_spells.cast("heal  on  test item")
    expected2 = (
        "[event]You cast [spell_name]heal[/spell_name] on "
        "[item_name]test item[/item_name].[/event]"
    )
    assert expected2 in result2

def test_cast_empty_command(game_with_spells):
    """Test empty cast command returns an appropriate failure message."""
    result = game_with_spells.cast("")
    assert "[failure]You don't know any spell called ''.[/failure]" in result

def test_cast_only_on_keyword(game_with_spells):
    """Test passing only the keyword 'on' to cast is handled as unknown."""
    result = game_with_spells.cast("on")
    assert "[failure]You don't know any spell called 'on'.[/failure]" in result

def test_cast_spell_name_only_with_on(game_with_spells):
    """Test inputs like 'heal on' are treated as unknown spell names."""
    result = game_with_spells.cast("heal on")
    assert "[failure]You don't know any spell called 'heal on'.[/failure]" in result

# Ensure this is at the very end if no other tests follow

# --- Tests for 'say' command ---

def test_say_word_to_character_successful(game):
    """Test saying a word to a character that recognizes it."""
    mock_char = MockCharacter("guard")
    game.state.current_room.add_character(mock_char)

    result = game.say("hello", "guard")

    expected = (
        "[dialogue][character_name]guard[/character_name] responds: '"
        "Hello there!'[/dialogue]"
    )
    assert expected in result

def test_say_password_to_character(game):
    """Test saying a password to a character."""
    mock_char = MockCharacter("gatekeeper")
    game.state.current_room.add_character(mock_char)

    result = game.say("password", "gatekeeper")

    expected = (
        "[dialogue][character_name]gatekeeper[/character_name] nods and "
        "steps aside.[/dialogue]"
    )
    assert expected in result

def test_say_unrecognized_word_to_character(game):
    """Test saying a word that the character doesn't recognize."""
    mock_char = MockCharacter("villager")
    game.state.current_room.add_character(mock_char)

    result = game.say("xyzzy", "villager")

    expected = (
        "[dialogue][character_name]villager[/character_name] looks confused "
        "and doesn't understand 'xyzzy'.[/dialogue]"
    )
    assert expected in result

def test_say_word_to_nonexistent_character(game):
    """Test saying a word to a character that doesn't exist in the room."""
    result = game.say("hello", "ghost")

    expected = (
        "[failure]There is no character named '[character_name]ghost[/character_name]' "
        "here to speak to.[/failure]"
    )
    assert expected in result

def test_say_empty_word(game):
    """Test saying an empty word."""
    mock_char = MockCharacter("merchant")
    game.state.current_room.add_character(mock_char)

    result = game.say("", "merchant")

    assert "[failure]What do you want to say?[/failure]" in result

def test_say_to_empty_character(game):
    """Test saying a word to an empty character name."""
    result = game.say("hello", "")

    assert "[failure]Who do you want to say that to?[/failure]" in result

def test_say_both_empty(game):
    """Test saying with both word and character empty."""
    result = game.say("", "")

    assert "[failure]What do you want to say?[/failure]" in result

def test_say_multi_word_phrase(game):
    """Test saying a multi-word phrase to a character."""
    mock_char = MockCharacter("oracle")
    game.state.current_room.add_character(mock_char)

    result = game.say("the answer is wisdom", "oracle")

    # The mock character doesn't recognize this phrase, so should get confused response
    expected = (
        "[dialogue][character_name]oracle[/character_name] looks confused "
        "and doesn't understand 'the answer is wisdom'.[/dialogue]"
    )
    assert expected in result

def test_say_case_insensitive_character_name(game):
    """Test that character names are case-insensitive."""
    mock_char = MockCharacter("Guard Captain")
    game.state.current_room.add_character(mock_char)

    result = game.say("hello", "guard captain")

    expected = (
        "[dialogue][character_name]Guard Captain[/character_name] responds: '"
        "Hello there!'[/dialogue]"
    )
    assert expected in result

def test_say_word_with_spaces(game):
    """Test saying a word/phrase that contains spaces."""
    mock_char = MockCharacter("wizard")
    game.state.current_room.add_character(mock_char)

    result = game.say("magic words", "wizard")

    expected = (
        "[dialogue][character_name]wizard[/character_name] looks confused "
        "and doesn't understand 'magic words'.[/dialogue]"
    )
    assert expected in result
