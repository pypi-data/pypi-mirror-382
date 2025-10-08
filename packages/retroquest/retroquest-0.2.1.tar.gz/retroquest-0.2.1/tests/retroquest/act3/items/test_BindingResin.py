"""Unit tests for BindingResin item in Act 3."""
from retroquest.act3.items.BindingResin import BindingResin


class DummyGameState:
    """Minimal dummy game state for inventory testing."""
    def __init__(self):
        """Initialize dummy game state with empty inventory."""
        self.inventory = []


class DummyItem:
    """Dummy item for use_with tests."""
    def get_name(self):
        """Return the name of the dummy item."""
        return "dummy item"


def test_bindingresin_init():
    """Test initialization of BindingResin item."""
    resin = BindingResin()
    assert resin.get_name().lower() == "binding resin"
    assert "sticky" in resin.description or "resin" in resin.description.lower()
    assert resin.can_be_carried_flag is True


def test_bindingresin_use_with_non_mount():
    """Test BindingResin use_with a non-mount item (should fail)."""
    resin = BindingResin()
    gs = DummyGameState()
    item = DummyItem()
    result = resin.use_with(gs, item)
    # Should fall back to Item's use_with, which may be a failure message
    assert "can't use" in result or "cannot use" in result or "not compatible" in result.lower()


def test_bindingresin_use_with_mirror_mount():
    """Test BindingResin use_with a MirrorMount (should delegate and succeed)."""
    import types
    from retroquest.act3.items.MirrorMount import MirrorMount
    resin = BindingResin()
    gs = DummyGameState()
    mount = MirrorMount()
    # Mock the use_with method
    called = {}
    def mock_use_with(_self, game_state, item):
        """Mock use_with to capture arguments and return a test event string."""
        called['game_state'] = game_state
        called['item'] = item
        return "[event]You apply the resin to the mirror mount.[/event]"
    mount.use_with = types.MethodType(mock_use_with, mount)
    result = resin.use_with(gs, mount)
    assert called['item'] is resin
    assert called['game_state'] is gs
    assert "apply the resin" in result or "resin" in result.lower()
