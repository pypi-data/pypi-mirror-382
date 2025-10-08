"""Tests for AncientAmulet item."""

from retroquest.act3.Act3 import Act3
from retroquest.engine.Game import Game


def test_ancient_amulet_exists():
    """Ancient Amulet should instantiate and provide a name."""
    act3 = Act3()
    act3.music_file = ''
    _game = Game([act3])

    from retroquest.act3.items.AncientAmulet import AncientAmulet
    am = AncientAmulet()
    assert am.get_name() is not None
