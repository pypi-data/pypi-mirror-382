"""Unit tests for CooledSlag item in Act 3."""
from retroquest.act3.items.CooledSlag import CooledSlag

class DummyGameState:
    """Dummy game state for testing inventory interactions."""

    def __init__(self):
        """Initialize with empty inventory."""
        self.inventory = []

class DummyItem:
    """Dummy item for use in tests."""

    def get_name(self):
        """Return the name of the dummy item."""
        return "dummy item"

def test_cooledslag_init():
    """Test initialization and properties of CooledSlag item."""
    slag = CooledSlag()
    assert slag.get_name() == "cooled slag"
    assert "glassy" in slag.description or "slag" in slag.description.lower()
    assert slag.can_be_carried_flag is True

def test_cooledslag_use_with_non_ashfern():
    """Test using CooledSlag with a non-AshFern item returns appropriate message."""
    slag = CooledSlag()
    gs = DummyGameState()
    item = DummyItem()
    result = slag.use_with(gs, item)
    assert "can't use" in result or "cannot use" in result or "not compatible" in result.lower()
    assert "cooled slag" in result
    assert "dummy item" in result

def test_cooledslag_use_with_ashfern_delegates():
    """Test using CooledSlag with AshFern crafts HeatWardMix and updates inventory."""
    from retroquest.act3.items.AshFern import AshFern
    slag = CooledSlag()
    gs = DummyGameState()
    ash = AshFern()
    # Place both in inventory to allow crafting
    gs.inventory = [ash, slag]
    result = slag.use_with(gs, ash)
    # After use, both should be removed and a HeatWardMix added
    assert ash not in gs.inventory
    assert slag not in gs.inventory
    found = any(getattr(i, 'get_name', lambda: None)() == 'heat-ward mix' for i in gs.inventory)
    assert found
    assert "heat-ward mix" in result or "heat-ward" in result
