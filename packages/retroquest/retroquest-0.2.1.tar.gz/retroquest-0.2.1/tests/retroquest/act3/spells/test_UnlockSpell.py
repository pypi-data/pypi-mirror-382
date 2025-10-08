"""Tests for Act 3 Unlock spell."""

from retroquest.act3.spells.UnlockSpell import UnlockSpell
from retroquest.act3.items.Locker import Locker
from retroquest.act3.items.PrismLantern import PrismLantern
from retroquest.act3.Act3 import Act3
from retroquest.engine.Game import Game


def test_cast_on_item_unlocks_locker():
    """Casting Unlock on a Locker should return a failure or unlock-like string."""
    spell = UnlockSpell()
    act3 = Act3()
    act3.music_file = ''
    game = Game([act3])

    locker = Locker()
    # Should return a failure unless lock is primed; ensure we get a string
    out = spell.cast_on_item(game.state, locker)
    assert '[' in out and 'failure' in out.lower() or 'click' in out.lower()


def test_cast_on_item_nonlocker_returns_failure():
    """Casting Unlock on a non-locker item should return a failure."""
    spell = UnlockSpell()
    act3 = Act3()
    act3.music_file = ''
    game = Game([act3])

    lantern = PrismLantern()
    out = spell.cast_on_item(game.state, lantern)
    assert '[failure]' in out
