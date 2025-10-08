"""Unit tests for the CommandParser component."""

import pytest
from engine.CommandParser import CommandParser

class DummyGame:
    """A minimal fake Game that records calls for CommandParser tests."""

    def __init__(self):
        """Create the fake game and a list to record calls."""
        self.calls = []

    def move(self, direction, arg=None):
        """Record a movement request."""
        self.calls.append(('move', direction, arg))

    def talk(self, target):
        """Record a talk/converse request."""
        self.calls.append(('talk', target))

    def say(self, word, character):
        """Record a player say action with text and target."""
        self.calls.append(('say', word, character))

    def ask(self, target):
        """Record an ask request."""
        self.calls.append(('ask', target))

    def give(self, item):
        """Record giving an item to someone."""
        self.calls.append(('give', item))

    def show(self, item):
        """Record showing an item."""
        self.calls.append(('show', item))

    def trade(self, item):
        """Record a trade intent for an item."""
        self.calls.append(('trade', item))

    def buy(self, args):
        """Record a buy request (raw args string)."""
        self.calls.append(('buy', args))

    def help(self, arg=None):
        """Record a help request; optional target argument."""
        self.calls.append(('help', arg))

    def look(self):
        """Record a look/examine-room request."""
        self.calls.append(('look',))

    def examine(self, target):
        """Record examining a target object."""
        self.calls.append(('examine', target))

    def search(self):
        """Record a search/investigate request."""
        self.calls.append(('search'))

    def listen(self, target=None):
        """Record a listen request directed at an optional target."""
        self.calls.append(('listen', target))

    def smell(self, target=None):
        """Record a smell request directed at an optional target."""
        self.calls.append(('smell', target))

    def taste(self, item):
        """Record tasting an item."""
        self.calls.append(('taste', item))

    def take(self, item):
        """Record picking up an item."""
        self.calls.append(('take', item))

    def drop(self, item):
        """Record dropping an item."""
        self.calls.append(('drop', item))

    def use(self, item1, item2=None):
        """Record using an item, optionally with a second item."""
        self.calls.append(('use', item1, item2))

    def eat(self, item):
        """Record eating an item."""
        self.calls.append(('eat', item))

    def drink(self, item):
        """Record drinking an item."""
        self.calls.append(('drink', item))

    def equip(self, item):
        """Record equipping an item."""
        self.calls.append(('equip', item))

    def unequip(self, item):
        """Record unequipping an item."""
        self.calls.append(('unequip', item))

    def inventory(self):
        """Record an inventory inspection request."""
        self.calls.append(('inventory',))

    def open(self, target):
        """Record opening a target (door, chest, etc.)."""
        self.calls.append(('open', target))

    def close(self, target):
        """Record closing a target (door, chest, etc.)."""
        self.calls.append(('close', target))

    def cast(self, spell_and_target):
        """Record a spell cast request (spell and optional target)."""
        self.calls.append(('cast', spell_and_target))

    def learn(self, spell):
        """Record learning a spell."""
        self.calls.append(('learn', spell))

    def spells(self):
        """Record a request to list available spells."""
        self.calls.append(('spells',))

    def save(self):
        """Record a save request."""
        self.calls.append(('save',))

    def load(self):
        """Record a load request."""
        self.calls.append(('load',))

    def quit(self):
        """Record a quit/exit request."""
        self.calls.append(('quit',))

    def restart(self):
        """Record a restart request."""
        self.calls.append(('restart',))

    def undo(self):
        """Record an undo request."""
        self.calls.append(('undo',))

    def redo(self):
        """Record a redo request."""
        self.calls.append(('redo',))

    def wait(self):
        """Record a wait/do-nothing request."""
        self.calls.append(('wait',))

    def rest(self):
        """Record a rest request."""
        self.calls.append(('rest',))

    def map(self):
        """Record a request to show the map."""
        self.calls.append(('map',))

    def stats(self):
        """Record a request to show player stats."""
        self.calls.append(('stats',))

    def unknown(self, command):
        """Record an unknown command invocation."""
        self.calls.append(('unknown', command))

    def dev_execute_commands(self, filename):
        """Record the dev-only command file execution request."""
        self.calls.append(('dev_execute_commands', filename))

@pytest.fixture(name="game_parser")
def game_parser_fixture():
    """Provide a DummyGame and its CommandParser for tests."""
    game = DummyGame()
    parser = CommandParser(game, True)
    return game, parser

def test_movement_commands(game_parser):
    """Movement-related commands should call move with correct args."""
    game, parser = game_parser
    commands = {
        "go north": ("move", "north", None),
        "move north": ("move", "north", None),
        "north": ("move", "north", None),
        "n": ("move", "north", None),
        "go south": ("move", "south", None),
        "move south": ("move", "south", None),
        "south": ("move", "south", None),
        "s": ("move", "south", None),
        "go east": ("move", "east", None),
        "move east": ("move", "east", None),
        "east": ("move", "east", None),
        "e": ("move", "east", None),
        "go west": ("move", "west", None),
        "move west": ("move", "west", None),
        "west": ("move", "west", None),
        "w": ("move", "west", None),
        # "enter cottage": ("move", "in", "cottage"), # CommandParser sends "cottage" as arg
        # "go in": ("move", "in", None),
        # "go inside": ("move", "in", None),
        # "leave cottage": ("move", "out", "cottage"), # CommandParser sends "cottage" as arg
        # "exit room": ("move", "out", "room"), # CommandParser sends "room" as arg
        # "go out": ("move", "out", None),
        # "climb tree": ("move", "up", "tree"), # CommandParser sends "tree" as arg
        # "ascend stairs": ("move", "up", "stairs"), # CommandParser sends "stairs" as arg
        # "descend ladder": ("move", "down", "ladder"), # CommandParser sends "ladder" as arg
        # "go down path": ("move", "down", "path"), # CommandParser sends "path" as arg
        # "follow trail": ("move", "follow", "trail"),
        # "walk road": ("move", "follow", "road"), # walk is alias for follow
    }
    expected_calls = []
    for cmd_text, expected_call in commands.items():
        parser.parse(cmd_text)
        expected_calls.append(expected_call)
    assert game.calls == expected_calls

def test_interaction_commands(game_parser):
    """Interaction commands (talk/say/give/buy) call the right methods."""
    game, parser = game_parser
    commands = {
        "talk to mira": ("talk", "mira"),
        "speak to blacksmith": ("talk", "blacksmith"),
        "converse with villager": ("talk", "villager"),
        "say hello to mira": ("say", "hello", "mira"),
        "say wisdom to nymph": ("say", "wisdom", "nymph"),
        "say magic word to guardian spirit": ("say", "magic word", "guardian spirit"),
        "give bread to grandmother": ("give", "bread to grandmother"),
        "hand coin to merchant": ("give", "coin to merchant"),
        "buy rope from shopkeeper": ("buy", "rope from shopkeeper"),
        "buy apple from merchant": ("buy", "apple from merchant"),
    }
    expected_calls = []
    for cmd_text, expected_call in commands.items():
        parser.parse(cmd_text)
        expected_calls.append(expected_call)
    assert game.calls == expected_calls

def test_examination_commands(game_parser):
    """Examination and look commands map to look/examine/search."""
    game, parser = game_parser
    commands = {
        "look": ("look",),
        "observe": ("look",),
        "survey": ("look",),
        "look at statue": ("examine", "statue"),
        "inspect scroll": ("examine", "scroll"),
        "examine book": ("examine", "book"),
        "search": ("search"),
        "investigate": ("search"),
        # "listen to door": ("listen", "door"),
    }
    expected_calls = []
    for cmd_text, expected_call in commands.items():
        parser.parse(cmd_text)
        expected_calls.append(expected_call)
    assert game.calls == expected_calls

def test_examination_additional_aliases(game_parser):
    """Covers shorthand and additional aliases not in the original test."""
    game, parser = game_parser
    commands = {
        "l": ("look",),  # shorthand alias
        "look statue": ("examine", "statue"),  # 'look <target>' form
        "check altar": ("examine", "altar"),   # 'check <target>' alias
    }
    expected_calls = []
    for cmd_text, expected_call in commands.items():
        parser.parse(cmd_text)
        expected_calls.append(expected_call)
    assert game.calls == expected_calls

def test_inventory_management_commands(game_parser):
    """Inventory and item-related commands should call correct methods."""
    game, parser = game_parser
    commands = {
        "take key": ("take", "key"),
        "pick up sword": ("take", "sword"),
        "grab apple": ("take", "apple"),
        "get shield": ("take", "shield"),
        "drop key": ("drop", "key"),
        "discard rock": ("drop", "rock"),
        "use lantern": ("use", "lantern", None),
        "use key with chest": ("use", "key", "chest"), # New test case
        "use bread with chicken": ("use", "bread", "chicken"), # New test case
        # "eat bread": ("eat", "bread"),
        # "consume apple": ("eat", "apple"),
        # "drink water": ("drink", "water"),
        # "equip sword": ("equip", "sword"),
        # "wear cloak": ("equip", "cloak"),
        # "unequip sword": ("unequip", "sword"),
        # "remove helmet": ("unequip", "helmet"),
        "inventory": ("inventory",),
        "i": ("inventory",),
        "inv": ("inventory",),
        "open chest": ("open", "chest"),
        "close door": ("close", "door"),
    }
    expected_calls = []
    for cmd_text, expected_call in commands.items():
        parser.parse(cmd_text)
        expected_calls.append(expected_call)
    assert game.calls == expected_calls

def test_use_command_error_no_item(game_parser):
    """Using with no item should return an informative error."""
    game, parser = game_parser
    # An empty item after 'use ' should return an error string
    result = parser.parse("use   ")
    assert "What do you want to use?" in result
    assert game.calls == []  # No game method invoked

def test_use_command_error_missing_second_item(game_parser):
    """Using with 'with' but missing second item should error."""
    game, parser = game_parser
    # Missing second item after 'with'
    result = parser.parse("use key with   ")
    assert "You need to specify two items to use with each other" in result
    assert game.calls == []

def test_magic_commands(game_parser):
    """Magic-related commands like cast and spells behave as expected."""
    game, parser = game_parser
    # Corrected expected calls based on CommandParser.py
    expected_calls = []
    parser.parse("cast fireball") # Generic cast
    expected_calls.append(("cast", "fireball"))
    parser.parse("cast fireball on goblin") # Generic cast with target
    expected_calls.append(("cast", "fireball on goblin"))
    parser.parse("spells")
    expected_calls.append(("spells",))

    assert game.calls == expected_calls

def test_dynamic_go_direction(game_parser):
    """Ensure 'go <custom>' passes the custom direction to move."""
    game, parser = game_parser
    parser.parse("go secret_passage")
    assert game.calls == [("move", "secret_passage", None)]


def test_game_management_commands(game_parser):
    """Game-management commands (save/load/help/quit) map correctly."""
    game, parser = game_parser
    commands = {
        "save": ("save",),
        "load": ("load",),
        "help": ("help", None), # Parameterless help
        "?": ("help", None),   # Parameterless help
        "quit": ("quit",),
        "exit": ("quit",),
    }
    expected_calls = []
    for cmd_text, expected_call in commands.items():
        parser.parse(cmd_text)
        expected_calls.append(expected_call)
    assert game.calls == expected_calls

def test_miscellaneous_commands(game_parser):
    """Misc commands like rest/map/stats are dispatched correctly."""
    game, parser = game_parser
    commands = {
        "sleep": ("rest",),
        "rest": ("rest",),
        "map": ("map",),
        "stats": ("stats",),
    }
    expected_calls = []
    for cmd_text, expected_call in commands.items():
        parser.parse(cmd_text)
        expected_calls.append(expected_call)
    assert game.calls == expected_calls

def test_dev_execute_commands(game_parser):
    """Test dev_execute_commands path when DEV_MODE is enabled."""
    game, parser = game_parser
    parser.parse("dev_execute_commands commands.txt")
    assert game.calls == [("dev_execute_commands", "commands.txt")]

def test_unknown_command(game_parser):
    """Unknown commands are forwarded to the game's unknown handler."""
    game, parser = game_parser
    parser.parse("xyzzy")
    assert game.calls == [("unknown", "xyzzy")]

def test_say_command_validation(game_parser):
    """Say command validation returns errors for malformed forms."""
    game, parser = game_parser

    # Test valid say commands
    parser.parse("say hello to mira")
    assert game.calls[-1] == ("say", "hello", "mira")

    parser.parse("say the answer is wisdom to water nymph")
    assert game.calls[-1] == ("say", "the answer is wisdom", "water nymph")

    # Test invalid say commands that should return error messages
    result = parser.parse("say hello")  # Missing "to character"
    assert "You need to specify who to say that to" in result

    result = parser.parse("say to mira")  # Missing word
    assert "You need to specify who to say that to" in result

    result = parser.parse("say  to ")  # Empty word and character
    assert "You need to specify who to say that to" in result
