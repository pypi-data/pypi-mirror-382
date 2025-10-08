"""Unit tests for PhoenixGuardian character in Act 3."""
from retroquest.act3.characters.PhoenixGuardian import PhoenixGuardian

class DummyGameState:
    """Minimal dummy game state for flag testing."""
    def __init__(self, flag_value=False):
        self._flag = flag_value
    def get_story_flag(self, _flag):
        """Return the dummy story flag value for testing."""
        return self._flag

def test_phoenix_guardian_initialization():
    """Test PhoenixGuardian initializes with correct name and description."""
    pg = PhoenixGuardian()
    assert pg.get_name() == "phoenix guardian"
    assert "fire-etched robes" in pg.description

def test_talk_to_before_quest_complete():
    """Test talk_to gives vent puzzle hint before quest completion."""
    pg = PhoenixGuardian()
    gs = DummyGameState(flag_value=False)
    response = pg.talk_to(gs)
    assert "bring the vents into harmony" in response
    assert "ward" in response
    assert "crater" in response
    assert "Phoenix Guardian studies you" in response

def test_talk_to_after_quest_complete():
    """Test talk_to gives post-completion advice after quest is done."""
    pg = PhoenixGuardian()
    gs = DummyGameState(flag_value=True)
    response = pg.talk_to(gs)
    assert "The way is open" in response
    assert "patience is your ally" in response
    assert "Phoenix will not appear" in response
