"""Unit tests for PhoenixCrater room in Act 3."""
from retroquest.act3.rooms.PhoenixCrater import PhoenixCrater


class DummyPhoenix:
    """Dummy Phoenix character for testing PhoenixCrater room."""
    def get_name(self):
        """Return the name of the dummy Phoenix."""
        return "Phoenix"


class DummyGameState:
    """Minimal dummy game state for PhoenixCrater tests."""

def test_phoenixcrater_init():
    """Test initialization of PhoenixCrater room."""
    room = PhoenixCrater()
    assert room.name == "Phoenix Crater"
    assert "vitrified rock" in room.description or "crater" in room.description
    assert "north" in room.exits
    assert room.items == []
    assert room.characters == []


def test_phoenixcrater_rest_reveals_phoenix():
    """Test that resting in PhoenixCrater reveals the Phoenix only once and updates description."""
    room = PhoenixCrater()
    gs = DummyGameState()
    # First rest: should add Phoenix and update description
    result = room.rest(gs)
    assert any(c.get_name().lower() == "phoenix" for c in room.characters)
    assert "phoenix of living ember" in result or "ancient, knowing patience" in result
    assert "molten fan" in room.description or "plumage" in room.description
    # Second rest: should not add another Phoenix
    prev_count = sum(1 for c in room.characters if c.get_name().lower() == "phoenix")
    result2 = room.rest(gs)
    assert sum(1 for c in room.characters if c.get_name().lower() == "phoenix") == prev_count
    assert "gathering your strength" in result2
