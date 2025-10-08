"""Tests for LanternBracket presence and state transitions."""

from retroquest.act3.Act3 import Act3
from retroquest.engine.Game import Game
from retroquest.act3.items.LanternBracket import LanternBracket

def test_lantern_bracket_default_state():
    """Verify that a new LanternBracket starts empty (no lantern mounted)."""
    act3 = Act3()
    act3.music_file = ''
    _game = Game([act3])

    lb = LanternBracket()
    assert hasattr(lb, 'has_lantern')
    assert lb.has_lantern is False

def test_lanternbracket_examine():
    """Verify examining the LanternBracket reflects its state correctly."""
    bracket = LanternBracket()
    # Examine with no lantern
    result_empty = bracket.examine(None)
    assert "empty bracket" in result_empty or "waits for a lantern" in result_empty
    # Place lantern and examine again
    bracket.put_lantern()
    result_with = bracket.examine(None)
    assert "prism lantern rests" in result_with or "ready to be lit" in result_with
