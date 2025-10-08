"""Unit tests for VentStone item in Act 3."""
from retroquest.act3.items.VentStone import VentStone

class DummyGameState:
    """Dummy game state for testing current room context."""

    def __init__(self):
        """Initialize with no current room."""
        self.current_room = None

class DummyRoom:
    """Dummy room for testing room-specific item interactions."""

    def __init__(self, name="Fumarole Passages"):
        """Initialize with a name and no calls to calibrate_with_stone."""
        self.name = name
        self.called_with = None

    def calibrate_with_stone(self, game_state, stone):
        """Simulate calibrating the vent with the stone."""
        self.called_with = (game_state, stone)
        return "[event]You calibrate the vent with the stone.[/event]"

def test_ventstone_init():
    """Test initialization and properties of VentStone item."""
    stone = VentStone()
    assert stone.get_name() == "vent stone"
    assert "stone" in stone.description.lower() or "vent" in stone.description.lower()
    assert stone.can_be_carried_flag is True

def test_ventstone_use_wrong_room():
    """Test using VentStone in the wrong room returns appropriate message."""
    stone = VentStone()
    gs = DummyGameState()
    gs.current_room = DummyRoom(name="Not Fumarole Passages")
    result = stone.use(gs)
    assert "can't use" in result or "usefully here" in result

def test_ventstone_use_in_fumarole_passages_delegates():
    """Test using VentStone in Fumarole Passages delegates to room's calibrate_with_stone method."""
    stone = VentStone()
    gs = DummyGameState()
    room = DummyRoom(name="Fumarole Passages")
    gs.current_room = room
    result = stone.use(gs)
    assert room.called_with == (gs, stone)
    assert "calibrate the vent" in result or "vent" in result
