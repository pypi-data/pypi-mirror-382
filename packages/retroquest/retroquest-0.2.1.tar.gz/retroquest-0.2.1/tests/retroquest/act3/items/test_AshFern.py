"""Unit tests for AshFern item in Act 3."""
from retroquest.act3.items.AshFern import AshFern


class DummyGameState:
    """Minimal dummy game state for AshFern tests."""
    def __init__(self):
        """Initialize dummy game state with empty inventory."""
        self.inventory = []


class DummyItem:
    """Dummy item for use_with tests."""
    def __init__(self, name):
        """Initialize dummy item with a name."""
        self._name = name
    def get_name(self):
        """Return the name of the dummy item."""
        return self._name


def test_ashfern_init():
    """Test initialization of AshFern item."""
    ash = AshFern()
    assert ash.get_name() == "ash-fern"
    assert "brittle frond" in ash.description
    assert ash.can_be_carried_flag is True


def test_ashfern_use_with_non_slag():
    """Test AshFern use_with a non-slag item (should fail)."""
    ash = AshFern()
    gs = DummyGameState()
    other = DummyItem("not slag")
    result = ash.use_with(gs, other)
    assert "can't use" in result
    assert "ash-fern" in result
    assert "not slag" in result


def test_ashfern_use_with_slag_adds_mix():
    """Test AshFern use_with cooled slag adds HeatWardMix and removes both items."""
    from retroquest.act3.items.CooledSlag import CooledSlag
    ash = AshFern()
    gs = DummyGameState()
    slag = CooledSlag()
    gs.inventory = [ash, slag]
    result = ash.use_with(gs, slag)
    # Should remove both from inventory and add HeatWardMix
    assert ash not in gs.inventory
    assert slag not in gs.inventory
    # Check for HeatWardMix by name
    found = any(getattr(i, 'get_name', lambda: None)() == 'heat-ward mix' for i in gs.inventory)
    assert found
    assert "heat-ward mix" in result or "heat-ward" in result
    assert "combine the ash-fern with cooled slag" in result
