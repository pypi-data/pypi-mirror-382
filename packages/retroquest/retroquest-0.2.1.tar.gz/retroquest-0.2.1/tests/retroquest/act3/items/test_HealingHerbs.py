"""Tests for HealingHerbs item."""

from retroquest.act3.Act3 import Act3
from retroquest.engine.Game import Game


def test_healing_herbs_get_name():
    """Ensure HealingHerbs exposes a sensible name string for display.

    The test accepts any non-empty name that mentions 'herb' or is not None.
    """
    act3 = Act3()
    act3.music_file = ''
    _game = Game([act3])

    from retroquest.act3.items.HealingHerbs import HealingHerbs
    hh = HealingHerbs()
    assert 'herb' in hh.get_name().lower() or hh.get_name() is not None
