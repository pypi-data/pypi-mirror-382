"""Unit tests for EmberGallery room in Act 3."""
from retroquest.act3.rooms.EmberGallery import EmberGallery


class DummyGameState:
    """Minimal dummy game state for testing EmberGallery."""


def test_embergallery_init():
    """Test initialization of EmberGallery room."""
    room = EmberGallery()
    assert room.name == "Ember Gallery"
    assert "charcoal" in room.description or "iron" in room.description
    assert "north" in room.exits and "west" in room.exits
    assert room.items == []
    assert room.characters == []


def test_embergallery_search_first_time_reveals_deposits():
    """Test that searching EmberGallery reveals deposits only once and does not duplicate items."""
    room = EmberGallery()
    gs = DummyGameState()
    result = room.search(gs)
    # Should add AshFern and CooledSlag to items
    names = [i.get_name() for i in room.items]
    assert any("ash-fern" in n for n in names)
    assert any("cooled slag" in n for n in names)
    assert "brittle frond" in result or "ash-fern" in result
    assert "cooled slag" in result
    # Should not reveal again
    result2 = room.search(gs)
    assert "find nothing new" in result2 or "worktables" in result2
    # Items should not be duplicated
    assert names == [i.get_name() for i in room.items]
