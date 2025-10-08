"""Tests for the AshScholar character in Act 3."""

from retroquest.act3.characters.AshScholar import AshScholar
from retroquest.act3.items.BrassMirrorSegment import BrassMirrorSegment
from retroquest.engine.GameState import GameState


class DummyRoom:
    """Minimal dummy room used when constructing a GameState for tests."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.items = []


def _make_gs() -> GameState:
    """Create a minimal GameState for character tests."""
    return GameState(DummyRoom("TestRoom"), all_rooms={}, all_quests=[])


def test_ashscholar_gives_one_when_none_in_inventory() -> None:
    """The scholar should give a Brass Mirror Segment exactly once."""
    g = _make_gs()
    scholar = AshScholar()

    # ensure inventory empty at start
    assert g.get_item_count('Brass Mirror Segment') == 0

    res1 = scholar.talk_to(g)
    assert 'brass' in res1.lower() or 'scrap' in res1.lower()
    # one segment should now be present
    assert g.get_item_count('Brass Mirror Segment') == 1

    # talking again should not add another
    res2 = scholar.talk_to(g)
    assert 'terraces' in res2.lower() or 'seek' in res2.lower()
    assert g.get_item_count('Brass Mirror Segment') == 1


def test_ashscholar_gives_one_even_if_player_has_one() -> None:
    """If the player already has a segment, the scholar still gives one, but only once."""
    g = _make_gs()
    scholar = AshScholar()

    # pre-populate inventory with a segment
    g.add_item_to_inventory(BrassMirrorSegment())
    assert g.get_item_count('Brass Mirror Segment') == 1

    res1 = scholar.talk_to(g)
    assert 'brass' in res1.lower() or 'scrap' in res1.lower()
    # now two segments should be present (one pre-existing + one from scholar)
    assert g.get_item_count('Brass Mirror Segment') == 2

    # second talk should not add another (still 2)
    res2 = scholar.talk_to(g)
    assert 'terraces' in res2.lower() or 'seek' in res2.lower()
    assert g.get_item_count('Brass Mirror Segment') == 2
