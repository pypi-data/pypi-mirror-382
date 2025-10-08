"""Unit tests for EmberwaterCanteen item in Act 3."""
from retroquest.act3.items.EmberwaterCanteen import EmberwaterCanteen

class DummyRoom:
    """Dummy room for testing item placement."""

    def __init__(self):
        """Initialize with empty items list."""
        self.items = []

class DummyGameState:
    """Dummy game state for testing current room context."""

    def __init__(self):
        """Initialize with a DummyRoom as the current room."""
        self.current_room = DummyRoom()


def test_canteen_init():
    """Test initialization and properties of EmberwaterCanteen item."""
    canteen = EmberwaterCanteen()
    assert canteen.get_name() == "Emberwater Canteen"
    assert "canteen" in canteen.description.lower()
    assert canteen.can_be_carried_flag is True

def test_canteen_examine_first_time_adds_segment():
    """Test examining EmberwaterCanteen adds segment only once and updates description."""
    canteen = EmberwaterCanteen()
    gs = DummyGameState()
    result = canteen.examine(gs)
    # Should add a Brass Mirror Segment to the room
    found = any(
        getattr(i, 'get_name', lambda: None)() == 'Brass Mirror Segment'
        for i in gs.current_room.items
    )
    assert found
    assert "pry free" in result or "falls to the ground" in result
    # Should not add another segment on second examine
    before = len(gs.current_room.items)
    result2 = canteen.examine(gs)
    after = len(gs.current_room.items)
    assert after == before
    assert "pry free" not in result2
    assert "canteen's lining" in result2 or "broth" in result2
