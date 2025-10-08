"""Unit tests for HeatWardMix item in Act 3."""
from retroquest.act3.items.HeatWardMix import HeatWardMix

class DummyGameState:
    """Dummy game state for testing current room context."""

    def __init__(self):
        """Initialize with no current room."""
        self.current_room = None

class DummyItem:
    """Dummy item for use in tests."""

    def get_name(self):
        """Return the name of the dummy item."""
        return "dummy item"

class DummyRoom:
    """Dummy room for testing room-specific item interactions."""

    def __init__(self, name="Fumarole Passages"):
        """Initialize with a name and no calls to apply_heat_ward."""
        self.name = name
        self.called_with = None

    def get_name(self):
        """Return the name of the dummy room."""
        return self.name

    def apply_heat_ward(self, game_state, mix):
        """Simulate applying heat-ward mix to the room."""
        self.called_with = (game_state, mix)
        return "[event]You apply the heat-ward mix to the vents.[/event]"

def test_heatwardmix_init():
    """Test initialization and properties of HeatWardMix item."""
    mix = HeatWardMix()
    assert mix.get_name() == "heat-ward mix"
    assert "ash-fern" in mix.description or "slag" in mix.description
    assert mix.can_be_carried_flag is True

def test_heatwardmix_use_with_non_room():
    """Test using HeatWardMix with a non-room item returns appropriate message."""
    mix = HeatWardMix()
    gs = DummyGameState()
    item = DummyItem()
    result = mix.use_with(gs, item)
    assert "can't use" in result or "cannot use" in result or "not compatible" in result.lower()
    assert "heat-ward mix" in result
    assert "dummy item" in result

def test_heatwardmix_use_with_room_delegates():
    """Test using HeatWardMix with a room delegates to room's apply_heat_ward method."""
    mix = HeatWardMix()
    gs = DummyGameState()
    room = DummyRoom()
    result = mix.use_with(gs, room)
    assert room.called_with == (gs, mix)
    assert "apply the heat-ward mix" in result or "vents" in result

def test_heatwardmix_use_wrong_room():
    """Test using HeatWardMix in the wrong room returns appropriate message."""
    mix = HeatWardMix()
    gs = DummyGameState()
    gs.current_room = DummyRoom(name="Not Fumarole Passages")
    result = mix.use(gs)
    assert "can't use" in result or "usefully here" in result

def test_heatwardmix_use_in_fumarole_passages_delegates():
    """Test using HeatWardMix in Fumarole Passages delegates to room's apply_heat_ward method."""
    mix = HeatWardMix()
    gs = DummyGameState()
    room = DummyRoom(name="Fumarole Passages")
    gs.current_room = room
    result = mix.use(gs)
    assert room.called_with == (gs, mix)
    assert "apply the heat-ward mix" in result or "vents" in result
