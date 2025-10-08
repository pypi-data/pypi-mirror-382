"""Unit tests for BrassMirrorSegment item in Act 3."""
from retroquest.act3.items.BrassMirrorSegment import BrassMirrorSegment
from retroquest.act3.items.MirrorMount import MirrorMount

class DummyGameState:
    def __init__(self):
        self.inventory = []

class DummyItem:
    def get_name(self):
        return "dummy item"

def test_brassmirrorsegment_init():
    seg = BrassMirrorSegment()
    assert seg.get_name().lower() == "brass mirror segment"
    assert "brass segment" in seg.description.lower()
    assert seg.can_be_carried_flag is True

def test_brassmirrorsegment_use_with_non_mount():
    seg = BrassMirrorSegment()
    gs = DummyGameState()
    item = DummyItem()
    result = seg.use_with(gs, item)
    # Should fall back to Item's use_with, which may be a failure message
    assert "can't use" in result or "cannot use" in result or "not compatible" in result.lower()

def test_brassmirrorsegment_use_with_mirror_mount():
    seg = BrassMirrorSegment()
    gs = DummyGameState()
    mount = MirrorMount()
    # Mock the mount's use_with to verify delegation
    import types
    called = {}
    def mock_use_with(self, game_state, item):
        called['game_state'] = game_state
        called['item'] = item
        return "[event]You install the segment in the mount.[/event]"
    mount.use_with = types.MethodType(mock_use_with, mount)
    result = seg.use_with(gs, mount)
    assert called['game_state'] is gs
    assert called['item'] is seg
    assert "install the segment" in result or "segment" in result.lower()
