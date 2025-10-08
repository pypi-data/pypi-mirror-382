"""Unit tests for EchoChambers room in Act 3."""
from retroquest.act3.rooms.EchoChambers import EchoChambers
from retroquest.act3.items.RunicWalls import RunicWalls
from retroquest.act3.items.ResonantChantRubbings import ResonantChantRubbings
from retroquest.act3.items.OldOathScrolls import OldOathScrolls


class DummyGameState:
    """Dummy game state for testing inventory interactions."""

    def __init__(self):
        """Initialize with empty inventory and current room."""
        self.inventory = []
        self.current_room = None

    def has_item(self, item_name):
        """Check if an item with the given name is in inventory."""
        return any(
            getattr(item, 'get_name', lambda: '')() == item_name
            for item in self.inventory
        )

    def add_item_to_inventory(self, item):
        """Add an item to the inventory."""
        self.inventory.append(item)

def test_echo_chambers_init():
    """Test initialization and properties of EchoChambers room."""
    room = EchoChambers()
    assert room.name == "Echo Chambers"
    assert "echo" in room.description.lower() or "cavern" in room.description.lower()
    assert any(isinstance(i, RunicWalls) for i in room.items)
    # Old Oath Scrolls should NOT be present initially
    assert not any(isinstance(i, OldOathScrolls) for i in room.items)
    assert "west" in room.exits


def test_runic_walls_examine():
    """Test examining runic walls reveals the chant and adds rubbings to room."""
    room = EchoChambers()
    walls = RunicWalls()
    gs = DummyGameState()
    gs.current_room = room
    # Check initial room items (should have runic walls but no rubbings)
    initial_items = [item.get_name() for item in room.get_items()]
    assert "runic walls" in initial_items
    assert "Resonant Chant Rubbings" not in initial_items
    result = walls.examine(gs)
    assert "Let stillness echo, let silence bind" in result
    assert "chant to quiet the phantoms" in result
    assert "rubbings" in result
    # Check that rubbings were added to the room
    final_items = [item.get_name() for item in room.get_items()]
    assert "Resonant Chant Rubbings" in final_items
    # Examine again - should not add duplicate rubbings using local flag
    initial_count = len([item for item in room.get_items()
                        if item.get_name() == "Resonant Chant Rubbings"])
    walls.examine(gs)
    final_count = len([item for item in room.get_items()
                      if item.get_name() == "Resonant Chant Rubbings"])
    assert initial_count == final_count == 1
    # Test that the local flag prevents discovery even in a different room
    room2 = EchoChambers()
    gs.current_room = room2
    walls.examine(gs)
    room2_items = [item.get_name() for item in room2.get_items()]
    # Should not have rubbings in room2 because they were already discovered
    assert "Resonant Chant Rubbings" not in room2_items

def test_runic_walls_discovery_behavior():
    """Test that the discovery flag works correctly with examine."""
    walls = RunicWalls()
    room1 = EchoChambers()
    room2 = EchoChambers()
    gs = DummyGameState()
    # First examine in room1 should discover rubbings
    gs.current_room = room1
    walls.examine(gs)
    room1_items = [item.get_name() for item in room1.get_items()]
    assert "Resonant Chant Rubbings" in room1_items
    # Second examine in room2 should not add rubbings due to flag
    gs.current_room = room2
    walls.examine(gs)
    room2_items = [item.get_name() for item in room2.get_items()]
    assert "Resonant Chant Rubbings" not in room2_items


def test_resonant_chant_rubbings_properties():
    """Test properties of ResonantChantRubbings item."""
    rubbings = ResonantChantRubbings()
    assert rubbings.get_name() == "Resonant Chant Rubbings"
    assert "Let stillness echo, let silence bind" in rubbings.description
    assert rubbings.can_be_carried_flag is True


def test_echo_chambers_search_reveals_scrolls():
    """Test that searching Echo Chambers reveals the Old Oath Scrolls."""
    room = EchoChambers()
    gs = DummyGameState()
    gs.current_room = room

    # Initially, Old Oath Scrolls should not be present
    initial_items = [item.get_name() for item in room.get_items()]
    assert "Old Oath Scrolls" not in initial_items

    # Search the room
    search_result = room.search(gs)
    assert "ancient scrolls" in search_result
    assert "stone niche" in search_result
    assert "sacred promises" in search_result

    # After searching, Old Oath Scrolls should be present
    final_items = [item.get_name() for item in room.get_items()]
    assert "Old Oath Scrolls" in final_items

    # Search again - should get different message
    search_again = room.search(gs)
    assert "already discovered" in search_again
    assert "no further secrets" in search_again

    # Should not add duplicate scrolls
    items_after_second_search = [item.get_name() for item in room.get_items()]
    scrolls_count = sum(1 for name in items_after_second_search if name == "Old Oath Scrolls")
    assert scrolls_count == 1
