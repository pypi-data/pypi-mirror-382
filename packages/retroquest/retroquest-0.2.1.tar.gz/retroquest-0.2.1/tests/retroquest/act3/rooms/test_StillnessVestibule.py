"""Unit tests for StillnessVestibule room in Act 3."""
from retroquest.act3.rooms.StillnessVestibule import StillnessVestibule
from retroquest.act3.items.EchoStones import EchoStones
from retroquest.act3.characters.SilenceKeeper import SilenceKeeper
from retroquest.act3.characters.WanderingPhantoms import WanderingPhantoms
from retroquest.act3.Act3StoryFlags import FLAG_ACT3_OATH_OF_STILLNESS_COMPLETED


class DummyGameState:
    """Dummy game state for testing."""

    def __init__(self):
        """Initialize with empty story flags."""
        self.story_flags = {}

    def get_story_flag(self, flag_name):
        """Get a story flag value."""
        return self.story_flags.get(flag_name, False)

    def set_story_flag(self, flag_name, value):
        """Set a story flag value."""
        self.story_flags[flag_name] = value


def test_stillness_vestibule_init():
    """Test initialization of StillnessVestibule."""
    room = StillnessVestibule()
    assert room.name == "Stillness Vestibule"

    # Check items
    item_names = [item.get_name() for item in room.items]
    assert "echo stones" in item_names
    assert "stillwater phial" in item_names
    assert "quiet charm" in item_names

    # Check character
    assert any(isinstance(char, SilenceKeeper) for char in room.characters)

    # Check that phantoms are initially present
    assert any(isinstance(char, WanderingPhantoms) for char in room.characters)


def test_stillness_vestibule_exits_blocked():
    """Test that Dragon's Hall exit is blocked initially."""
    room = StillnessVestibule()
    gs = DummyGameState()

    exits = room.get_exits(gs)
    assert "north" in exits  # CollapsedGalleries
    assert "west" in exits   # CavernMouth
    assert "east" not in exits  # DragonsHall should be blocked


def test_stillness_vestibule_exits_open():
    """Test that Dragon's Hall exit opens after Oath completion."""
    room = StillnessVestibule()
    gs = DummyGameState()
    gs.set_story_flag(FLAG_ACT3_OATH_OF_STILLNESS_COMPLETED, True)

    exits = room.get_exits(gs)
    assert "north" in exits  # CollapsedGalleries
    assert "west" in exits   # CavernMouth
    assert "east" in exits   # DragonsHall should be open
    assert exits["east"] == "DragonsHall"


def test_echo_stones_in_room():
    """Test that echo stones are properly configured in the room."""
    room = StillnessVestibule()

    # Find echo stones
    echo_stones = None
    for item in room.items:
        if isinstance(item, EchoStones):
            echo_stones = item
            break

    assert echo_stones is not None
    assert not echo_stones.are_blessed()  # Should start unblessed


def test_phantoms_only_whisper():
    """Test that phantoms only respond with undecipherable whispers."""
    room = StillnessVestibule()
    gs = DummyGameState()

    # Find the phantoms
    phantoms = None
    for char in room.characters:
        if isinstance(char, WanderingPhantoms):
            phantoms = char
            break

    assert phantoms is not None

    # Test that they only respond with whispers
    response = phantoms.talk_to(gs)
    # Check for mystical/ethereal response elements that indicate undecipherable speech
    mystical_indicators = [
        "whisper", "ethereal", "spectral", "sibilant", "half-formed",
        "cannot grasp", "slip away", "mist", "beyond understanding"
    ]
    assert any(indicator in response.lower() for indicator in mystical_indicators)

    # Make sure it's ethereal/mystical dialogue, not normal conversation
    assert "hello" not in response.lower()
    assert "greetings" not in response.lower()
