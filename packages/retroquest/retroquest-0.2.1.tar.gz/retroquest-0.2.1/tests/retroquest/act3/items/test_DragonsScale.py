"""Unit tests for DragonsScale item in Act 3."""
from retroquest.act3.items.DragonsScale import DragonsScale
from retroquest.act3.Act3StoryFlags import FLAG_ACT3_DRAGONS_SCALE_ACQUIRED


class DummyGameState:
    """Dummy game state for testing."""

    def __init__(self):
        """Initialize with empty story flags and inventory."""
        self.story_flags = {}
        self.inventory = []

    def get_story_flag(self, flag_name):
        """Get a story flag value."""
        return self.story_flags.get(flag_name, False)

    def set_story_flag(self, flag_name, value):
        """Set a story flag value."""
        self.story_flags[flag_name] = value


def test_dragons_scale_init():
    """Test initialization of DragonsScale."""
    scale = DragonsScale()
    assert scale.get_name() == "Dragon's Scale"
    assert "dark as midnight" in scale.description and "deep gold" in scale.description
    assert scale.can_be_carried_flag is True


def test_dragons_scale_pickup_with_all_prerequisites():
    """Test successful pickup with all prerequisites."""
    scale = DragonsScale()
    gs = DummyGameState()

    # Add scale to inventory to simulate pickup attempt
    gs.inventory.append(scale)

    # Try to pick up with all prerequisites
    result = scale.picked_up(gs)
    assert "settles into your hands" in result.lower()
    assert "burden of responsibility" in result.lower()
    assert "pulses warmly" in result.lower()
    assert scale in gs.inventory  # Should remain in inventory
    assert gs.get_story_flag(FLAG_ACT3_DRAGONS_SCALE_ACQUIRED)
