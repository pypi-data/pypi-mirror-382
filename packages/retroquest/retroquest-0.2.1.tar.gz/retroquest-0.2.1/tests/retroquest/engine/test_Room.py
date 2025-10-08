"""Tests for the Room class and room mechanics."""

import pytest
from retroquest.engine.Room import Room
from retroquest.engine.Item import Item
from retroquest.engine.Character import Character
from retroquest.engine.GameState import GameState

class DummyItem(Item):
    """Lightweight Item used in tests with an optional short name alias.

    The class provides a minimal get_short_name implementation to simulate
    items that expose both a full name and a short identifier used by the
    command parser and room lookup helpers.
    """

    def __init__(self, name, short_name=None, description="A dummy item"):
        super().__init__(name, description)
        self.short_name = short_name

    def get_short_name(self):
        return self.short_name or ""

class DummyCharacter(Character):
    """Minimal Character implementation for test assertions.

    Supplies only the constructor used by the tests; other interaction hooks
    can be monkeypatched when needed by individual test cases.
    """

    def __init__(self, name="Test Character", description="A test character"):
        super().__init__(name=name, description=description)

@pytest.fixture(name="game_state")
def game_state_fixture():
    """Provide a minimal GameState with a starting room for room tests."""
    # Create a minimal starting room and pass required mappings to GameState
    start_room = Room("Start", "Starting room")
    gs = GameState(start_room, {"Start": start_room}, [])
    return gs

# --- Initialization ---

def test_room_initialization_defaults():
    """Room initializes with expected default attributes."""
    r = Room("TestRoom", "A simple room.")
    assert r.name == "TestRoom"
    assert r.description == "A simple room."
    assert r.items == []
    assert r.characters == []
    assert r.exits == {}

# --- Item management ---

def test_add_and_get_items():
    """Added items are returned in insertion order by get_items()."""
    r = Room("R", "Desc")
    i1 = DummyItem("apple")
    i2 = DummyItem("apple")
    i3 = DummyItem("sword")
    r.add_item(i1)
    r.add_item(i2)
    r.add_item(i3)
    items = r.get_items()
    assert items == [i1, i2, i3]


def test_get_item_by_name_case_insensitive():
    """get_item_by_name performs case-insensitive name matching."""
    r = Room("R", "Desc")
    i = DummyItem("Golden Apple")
    r.add_item(i)
    assert r.get_item_by_name("golden apple") is i
    assert r.get_item_by_name("GOLDEN APPLE") is i
    assert r.get_item_by_name("nope") is None


def test_remove_item_success():
    """remove_item returns and removes the named item when present."""
    r = Room("R", "Desc")
    i = DummyItem("lantern")
    r.add_item(i)
    removed = r.remove_item("Lantern")
    assert removed is i
    assert r.items == []


def test_remove_item_not_found():
    """remove_item returns None when the named item is absent."""
    r = Room("R", "Desc")
    assert r.remove_item("ghost") is None

# --- Character management ---

def test_add_and_get_characters():
    """Characters can be added and retrieved from a room."""
    r = Room("R", "Desc")
    c1 = DummyCharacter("Villager")
    c2 = DummyCharacter("merchant")
    r.add_character(c1)
    r.add_character(c2)
    chars = r.get_characters()
    assert chars == [c1, c2]


def test_get_character_by_name_case_insensitive():
    """Character name lookup is case-insensitive."""
    r = Room("R", "Desc")
    c = DummyCharacter("Blacksmith John")
    r.add_character(c)
    assert r.get_character_by_name("blacksmith john") is c
    assert r.get_character_by_name("BLACKSMITH JOHN") is c
    assert r.get_character_by_name("wizard") is None

# --- Exits ---

def test_get_exits_returns_mapping(game_state):
    """get_exits returns the exit mapping provided at construction."""
    exits = {"north": "Forest", "south": "Village"}
    r = Room("R", "Desc", exits=exits)
    assert r.get_exits(game_state) == exits

# --- Describe ---

def test_describe_includes_items_grouped(game_state):
    """Room.describe groups identical items and includes counts."""
    r = Room("R", "Desc")
    r.add_item(DummyItem("apple"))
    r.add_item(DummyItem("apple"))
    r.add_item(DummyItem("sword"))
    desc = r.describe(game_state)
    # Should show grouped apples (2 apple) and single sword
    assert "2 apple" in desc
    assert "sword" in desc
    assert "Items you can see:" in desc


def test_describe_includes_characters(game_state):
    """Room.describe lists present characters by name."""
    r = Room("R", "Desc")
    r.add_character(DummyCharacter("Mira"))
    r.add_character(DummyCharacter("Blacksmith"))
    desc = r.describe(game_state)
    assert "Characters present:" in desc
    assert "Mira" in desc
    assert "Blacksmith" in desc


def test_describe_includes_exits(game_state):
    """Room.describe includes available exits and their destinations."""
    r = Room("R", "Desc", exits={"north": "Forest", "east": "River"})
    desc = r.describe(game_state)
    assert "Exits:" in desc
    assert "north" in desc and "Forest" in desc
    assert "east" in desc and "River" in desc


def test_describe_no_items_characters_or_exits(game_state):
    """Room.describe omits sections when there are no items, characters, or exits."""
    r = Room("R", "Desc")
    desc = r.describe(game_state)
    assert "Items you can see:" not in desc
    assert "Characters present:" not in desc
    assert "Exits:" not in desc

# --- Ambient Sound ---

def test_get_ambient_sound_default():
    """Default ambient sound is returned when none is overridden."""
    r = Room("R", "Desc")
    assert r.get_ambient_sound() == "It is quiet here."

# --- Hooks ---

def test_on_enter_returns_string(game_state):
    """on_enter executes without error and returns a string (possibly empty)."""
    r = Room("R", "Desc")
    # on_enter currently returns empty string; ensure no exception
    result = r.on_enter(game_state)
    assert result == ""


def test_enter_prints_description(capsys):
    """enter() prints the room description to stdout."""
    r = Room("R", "A printed description")
    r.enter()
    captured = capsys.readouterr()
    assert "A printed description" in captured.out

# --- Edge cases ---

def test_describe_item_name_collision_counts_separately(game_state):
    """describe counts identical item names correctly when many are present."""
    r = Room("R", "Desc")
    # Same name items should be grouped; ensure count increments
    for _ in range(4):
        r.add_item(DummyItem("coin"))
    desc = r.describe(game_state)
    assert "4 coin" in desc


def test_remove_item_case_preservation():
    """remove_item preserves the original item case when returned."""
    r = Room("R", "Desc")
    item = DummyItem("Lantern")
    r.add_item(item)
    removed = r.remove_item("lantern")
    assert removed.get_name() == "Lantern"


def test_get_item_by_name_empty_room():
    """get_item_by_name returns None when the room has no items."""
    r = Room("R", "Desc")
    assert r.get_item_by_name("anything") is None


def test_get_character_by_name_empty_room():
    """get_character_by_name returns None when the room has no characters."""
    r = Room("R", "Desc")
    assert r.get_character_by_name("anyone") is None
