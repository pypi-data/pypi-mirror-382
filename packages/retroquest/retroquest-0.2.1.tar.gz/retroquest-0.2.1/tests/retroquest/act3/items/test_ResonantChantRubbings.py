"""Unit tests for ResonantChantRubbings item in Act 3."""
from retroquest.act3.items.ResonantChantRubbings import ResonantChantRubbings
from retroquest.act3.items.EchoStones import EchoStones
from retroquest.act3.rooms.StillnessVestibule import StillnessVestibule
from retroquest.act3.characters.WanderingPhantoms import WanderingPhantoms
from retroquest.act3.Act3StoryFlags import FLAG_ACT3_OATH_OF_STILLNESS_COMPLETED


class DummyGameState:
    """Dummy game state for testing."""

    def __init__(self):
        """Initialize with empty story flags."""
        self.story_flags = {}
        self.current_room = None

    def get_story_flag(self, flag_name):
        """Get a story flag value."""
        return self.story_flags.get(flag_name, False)

    def set_story_flag(self, flag_name, value):
        """Set a story flag value."""
        self.story_flags[flag_name] = value

    def get_current_room(self):
        """Get the current room."""
        return self.current_room

    def set_current_room(self, room):
        """Set the current room."""
        self.current_room = room

    def remove_item_from_inventory(self, item_name):
        """Remove an item from inventory (dummy implementation)."""
        # In real implementation, this would remove the item from inventory
        # For testing purposes, we just acknowledge the method was called
        # and verify the item_name is a string
        assert isinstance(item_name, str)


def test_resonant_chant_rubbings_init():
    """Test initialization of ResonantChantRubbings."""
    rubbings = ResonantChantRubbings()
    assert rubbings.get_name() == "Resonant Chant Rubbings"
    assert rubbings.can_be_carried_flag
    assert "Let stillness echo, let silence bind" in rubbings.description


def test_use_with_blessed_stones_removes_phantoms():
    """Test that using rubbings with blessed stones removes phantoms from StillnessVestibule."""
    rubbings = ResonantChantRubbings()
    echo_stones = EchoStones()
    room = StillnessVestibule()
    gs = DummyGameState()
    gs.set_current_room(room)

    # Bless the echo stones
    echo_stones.receive_spell("bless", gs)
    assert echo_stones.are_blessed()

    # Initially, phantoms should be present
    assert any(isinstance(char, WanderingPhantoms) for char in room.characters)

    # Use rubbings with blessed stones
    result = rubbings.use_with(gs, echo_stones)

    # Check that the quest flag is set
    assert gs.get_story_flag(FLAG_ACT3_OATH_OF_STILLNESS_COMPLETED)

    # Check that phantoms are removed from the room
    assert not any(isinstance(char, WanderingPhantoms) for char in room.characters)

    # Check the return message mentions banishing phantoms
    assert "banishes the wandering phantoms" in result


def test_use_with_unblessed_stones():
    """Test that using rubbings with unblessed stones fails."""
    rubbings = ResonantChantRubbings()
    echo_stones = EchoStones()
    gs = DummyGameState()

    # Don't bless the stones
    assert not echo_stones.are_blessed()

    # Use rubbings with unblessed stones
    result = rubbings.use_with(gs, echo_stones)

    # Check that the quest flag is not set
    assert not gs.get_story_flag(FLAG_ACT3_OATH_OF_STILLNESS_COMPLETED)

    # Check failure message
    assert "must be sanctified" in result


def test_use_with_other_item():
    """Test that using rubbings with other items fails."""
    rubbings = ResonantChantRubbings()
    gs = DummyGameState()

    # Create a mock item
    class MockItem:
        """Mock item for testing incompatible item usage."""
        def get_name(self):
            """Return the mock item name."""
            return "mock item"

    mock_item = MockItem()
    result = rubbings.use_with(gs, mock_item)

    # Check failure message
    assert "has no effect" in result
