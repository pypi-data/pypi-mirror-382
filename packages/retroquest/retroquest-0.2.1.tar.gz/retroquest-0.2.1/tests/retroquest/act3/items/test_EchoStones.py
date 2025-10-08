"""Unit tests for EchoStones item in Act 3."""
from retroquest.act3.items.EchoStones import EchoStones
from retroquest.act3.items.ResonantChantRubbings import ResonantChantRubbings
from retroquest.act3.Act3StoryFlags import (
    FLAG_ACT3_OATH_OF_STILLNESS_COMPLETED,
    FLAG_ACT3_OATH_OF_STILLNESS_STARTED,
)


class DummyGameState:
    """Dummy game state for testing EchoStones functionality."""

    def __init__(self):
        """Initialize with empty story flags dictionary."""
        self.story_flags = {}
        self.current_room = None

    def get_story_flag(self, flag_name):
        """Get a story flag value.

        Args:
            flag_name: Name of the story flag to retrieve

        Returns:
            The flag value if set, False otherwise
        """
        return self.story_flags.get(flag_name, False)

    def set_story_flag(self, flag_name, value):
        """Set a story flag value.

        Args:
            flag_name: Name of the story flag to set
            value: Value to set for the flag
        """
        self.story_flags[flag_name] = value

    def remove_item_from_inventory(self, item_name):
        """Remove an item from inventory (dummy implementation)."""
        # In real implementation, this would remove the item from inventory
        # For testing purposes, we just acknowledge the method was called
        # and verify the item_name is a string
        assert isinstance(item_name, str)


def test_echo_stones_init():
    """Test initialization and basic properties of EchoStones."""
    stones = EchoStones()
    assert stones.get_name() == "echo stones"
    assert "carved" in stones.description and "channels" in stones.description
    assert stones.can_be_carried_flag is False
    assert not stones.are_blessed()


def test_echo_stones_bless_spell():
    """Test blessing the echo stones with the bless spell."""
    stones = EchoStones()
    gs = DummyGameState()

    # Initially the quest flag should not be set
    assert not gs.get_story_flag(FLAG_ACT3_OATH_OF_STILLNESS_STARTED)

    # First blessing should succeed and start the quest
    result = stones.receive_spell("bless", gs)
    assert "sacred luminescence" in result.lower() and "ancient chant" in result.lower()
    assert stones.are_blessed()
    assert gs.get_story_flag(FLAG_ACT3_OATH_OF_STILLNESS_STARTED)

    # Second blessing should indicate already blessed
    result = stones.receive_spell("bless", gs)
    assert "already blessed" in result.lower()


def test_echo_stones_examine_starts_quest():
    """Test that examining echo stones sets the oath of stillness started flag."""
    stones = EchoStones()
    gs = DummyGameState()

    # Initially the flag should not be set
    assert not gs.get_story_flag(FLAG_ACT3_OATH_OF_STILLNESS_STARTED)

    # Examine the stones
    result = stones.examine(gs)
    assert "carved" in result and "channels" in result

    # Flag should now be set
    assert gs.get_story_flag(FLAG_ACT3_OATH_OF_STILLNESS_STARTED)


def test_echo_stones_wrong_spell():
    """Test casting an incorrect spell on echo stones."""
    stones = EchoStones()
    gs = DummyGameState()

    result = stones.receive_spell("light", gs)
    assert "no effect" in result.lower()


def test_resonant_chant_rubbings_use_with_unblessed_stones():
    """Test using resonant chant rubbings with unblessed echo stones fails."""
    stones = EchoStones()
    rubbings = ResonantChantRubbings()
    gs = DummyGameState()

    result = rubbings.use_with(gs, stones)
    assert "cold and unresponsive" in result.lower()
    assert "sanctified" in result.lower()
    assert not gs.get_story_flag(FLAG_ACT3_OATH_OF_STILLNESS_COMPLETED)


def test_resonant_chant_rubbings_use_with_blessed_stones():
    """Test using resonant chant rubbings with blessed echo stones completes oath."""
    stones = EchoStones()
    rubbings = ResonantChantRubbings()
    gs = DummyGameState()

    # First bless the stones
    stones.receive_spell("bless", gs)

    # Then use chant rubbings with stones
    result = rubbings.use_with(gs, stones)
    assert "recite the resonant chant" in result.lower()
    assert "harmonious silence" in result.lower()
    assert "dragon's hall now lies open" in result.lower()
    assert gs.get_story_flag(FLAG_ACT3_OATH_OF_STILLNESS_COMPLETED)


def test_resonant_chant_rubbings_use_with_wrong_item():
    """Test using resonant chant rubbings with an incompatible item."""
    rubbings = ResonantChantRubbings()
    gs = DummyGameState()

    # Create a dummy item
    class DummyItem:
        """Dummy item for testing wrong item usage."""
        def get_name(self):
            """Return the dummy item name."""
            return "random item"

    dummy = DummyItem()
    result = rubbings.use_with(gs, dummy)
    assert "no effect" in result.lower()


def test_echo_stones_use_with_rubbings():
    """Test using echo stones with resonant chant rubbings delegates properly."""
    stones = EchoStones()
    rubbings = ResonantChantRubbings()
    gs = DummyGameState()

    # First bless the stones
    stones.receive_spell("bless", gs)
    assert stones.are_blessed()

    # Use echo stones with rubbings (should delegate to rubbings.use_with)
    result = stones.use_with(gs, rubbings)

    # Should complete the oath quest
    assert gs.get_story_flag(FLAG_ACT3_OATH_OF_STILLNESS_COMPLETED)
    assert "banishes the wandering phantoms" in result


def test_echo_stones_use_with_other_item():
    """Test using echo stones with other items fails gracefully."""
    stones = EchoStones()
    gs = DummyGameState()

    # Create a mock item
    class MockItem:
        """Mock item for testing incompatible item usage."""
        def get_name(self):
            """Return the mock item name."""
            return "mock item"

    mock_item = MockItem()
    result = stones.use_with(gs, mock_item)

    # Should fall back to base class behavior
    assert "can't use" in result and "echo stones" in result and "mock item" in result
