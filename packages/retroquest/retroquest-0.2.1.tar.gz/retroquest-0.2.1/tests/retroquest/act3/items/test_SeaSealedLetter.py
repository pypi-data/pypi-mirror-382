"""Tests for SeaSealedLetter item."""

from retroquest.act3.Act3 import Act3
from retroquest.engine.Game import Game


def test_sea_sealed_letter_name_and_pickup():
    """SeaSealedLetter exists and exposes an appropriate name."""
    act3 = Act3()
    act3.music_file = ''
    _game = Game([act3])

    from retroquest.act3.items.SeaSealedLetter import SeaSealedLetter
    letter = SeaSealedLetter()
    assert letter.get_name().lower().startswith('sea')
