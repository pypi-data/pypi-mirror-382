"""Unit tests for AncientDragon character in Act 3."""

from retroquest.act3.characters.AncientDragon import AncientDragon
from retroquest.act3.items.DragonsScale import DragonsScale
from retroquest.act3.rooms.DragonsHall import DragonsHall
from retroquest.engine.GameState import GameState
from retroquest.act3.Act3StoryFlags import (
    FLAG_ACT3_DRAGONS_MEMORY_RECEIVED,
    FLAG_ACT3_DRAGON_OATH_SPOKEN,
    FLAG_ACT3_OATH_SCROLLS_EXAMINED
)


class DummyRoom:
    """Minimal dummy room used when constructing a GameState for tests."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.items = []

    def add_item(self, item) -> None:
        """Add item to room."""
        self.items.append(item)


def _make_gs() -> GameState:
    """Create a minimal GameState for character tests."""
    return GameState(DummyRoom("TestRoom"), all_rooms={}, all_quests=[])


def test_ancient_dragon_init():
    """Test initialization of AncientDragon."""
    dragon = AncientDragon()
    assert dragon.name == "ancient dragon"
    assert "magnificent dragon" in dragon.description.lower()
    assert "golden eyes" in dragon.description.lower()


def test_talk_to_dragon_first_time():
    """Test talking to dragon for the first time gives memory."""
    dragon = AncientDragon()
    game_state = _make_gs()
    # First talk should give memory
    result = dragon.talk_to(game_state)
    assert 'Lyra and Theron' in result
    assert 'ward—not of stone or steel, but of love' in result
    assert game_state.get_story_flag(FLAG_ACT3_DRAGONS_MEMORY_RECEIVED)


def test_talk_to_dragon_second_time():
    """Test talking to dragon second time gives shorter response."""
    dragon = AncientDragon()
    game_state = _make_gs()

    # Set flag as if already talked
    game_state.set_story_flag(FLAG_ACT3_DRAGONS_MEMORY_RECEIVED, True)

    result = dragon.talk_to(game_state)
    assert 'memory has been shared' in result.lower()
    assert 'scale awaits' in result.lower()


def test_say_oath_to_dragon():
    """Test saying oath to dragon adds scale to room."""
    dragon = AncientDragon()
    game_state = _make_gs()
    room = DragonsHall()
    game_state.current_room = room

    # First need to talk to get memory
    dragon.talk_to(game_state)

    # Need to examine oath scrolls first
    game_state.set_story_flag(FLAG_ACT3_OATH_SCROLLS_EXAMINED, True)

    # Initially no dragon's scale in room
    assert not any(isinstance(item, DragonsScale) for item in room.items)

    # Say oath to dragon
    result = dragon.say_to("oath", game_state)

    assert 'oath' in result.lower()
    assert 'scale is yours to bear' in result.lower()
    assert game_state.get_story_flag(FLAG_ACT3_DRAGON_OATH_SPOKEN)

    # Dragon's scale should now be in room
    assert any(isinstance(item, DragonsScale) for item in room.items)


def test_say_oath_twice():
    """Test saying oath twice gives already given response."""
    dragon = AncientDragon()
    game_state = _make_gs()
    room = DragonsHall()
    game_state.current_room = room

    # Set flags as if already done
    game_state.set_story_flag(FLAG_ACT3_DRAGONS_MEMORY_RECEIVED, True)
    game_state.set_story_flag(FLAG_ACT3_OATH_SCROLLS_EXAMINED, True)
    game_state.set_story_flag(FLAG_ACT3_DRAGON_OATH_SPOKEN, True)

    result = dragon.say_to("oath", game_state)
    assert 'oath has been given and accepted' in result.lower()
    assert 'scale is yours to claim' in result.lower()


def test_say_wrong_word_to_dragon():
    """Test saying wrong words to dragon."""
    dragon = AncientDragon()
    game_state = _make_gs()
    room = DragonsHall()
    game_state.current_room = room

    # Set dragons memory received flag first
    game_state.set_story_flag(FLAG_ACT3_DRAGONS_MEMORY_RECEIVED, True)

    result = dragon.say_to("hello", game_state)
    assert 'does not respond to those words' in result.lower()
    assert 'meaningful pledge' in result.lower()


def test_say_oath_without_examining_scrolls():
    """Test saying oath without examining scrolls first."""
    dragon = AncientDragon()
    game_state = _make_gs()
    room = DragonsHall()
    game_state.current_room = room

    # Set dragons memory received flag first
    game_state.set_story_flag(FLAG_ACT3_DRAGONS_MEMORY_RECEIVED, True)

    # Don't set the oath scrolls examined flag
    assert not game_state.get_story_flag(FLAG_ACT3_OATH_SCROLLS_EXAMINED)

    # Try to say oath
    result = dragon.say_to("oath", game_state)

    assert 'must first understand the weight of the oath' in result.lower()
    assert 'proves your selflessness' in result.lower()
    # Should not set the oath spoken flag
    assert not game_state.get_story_flag(FLAG_ACT3_DRAGON_OATH_SPOKEN)
    # Should not add dragon scale to room
    assert not any(isinstance(item, DragonsScale) for item in room.items)


def test_say_oath_after_examining_scrolls():
    """Test saying oath after examining scrolls allows the oath."""
    dragon = AncientDragon()
    game_state = _make_gs()
    room = DragonsHall()
    game_state.current_room = room

    # Set dragons memory received flag first
    game_state.set_story_flag(FLAG_ACT3_DRAGONS_MEMORY_RECEIVED, True)

    # Set the oath scrolls examined flag
    game_state.set_story_flag(FLAG_ACT3_OATH_SCROLLS_EXAMINED, True)

    # Say oath to dragon
    result = dragon.say_to("oath", game_state)

    assert 'speak your oath' in result.lower()
    assert 'scale is yours to bear' in result.lower()
    assert game_state.get_story_flag(FLAG_ACT3_DRAGON_OATH_SPOKEN)
    # Dragon's scale should now be in room
    assert any(isinstance(item, DragonsScale) for item in room.items)


def test_oath_requirements_case_insensitive():
    """Test that oath command is case insensitive."""
    dragon = AncientDragon()
    game_state = _make_gs()
    room = DragonsHall()
    game_state.current_room = room

    # Set dragons memory received flag first
    game_state.set_story_flag(FLAG_ACT3_DRAGONS_MEMORY_RECEIVED, True)

    # Set the oath scrolls examined flag
    game_state.set_story_flag(FLAG_ACT3_OATH_SCROLLS_EXAMINED, True)

    # Test different cases
    for oath_word in ["oath", "OATH", "Oath", "OaTh"]:
        # Reset flags for each test
        game_state.set_story_flag(FLAG_ACT3_DRAGON_OATH_SPOKEN, False)
        room.items.clear()

        result = dragon.say_to(oath_word, game_state)
        assert 'speak your oath' in result.lower()
        assert game_state.get_story_flag(FLAG_ACT3_DRAGON_OATH_SPOKEN)
