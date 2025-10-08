"""Tests for Act 3 Purify spell."""

from retroquest.act3.spells.PurifySpell import PurifySpell
from retroquest.act3.items.WardingPillars import WardingPillars
from retroquest.act3.Act3 import Act3
from retroquest.engine.Game import Game


def test_cast_spell_returns_event_and_description():
    """Ensure cast_spell returns brine-related text or a cast acknowledgement."""
    spell = PurifySpell()
    act3 = Act3()
    act3.music_file = ''
    game = Game([act3])

    out = spell.cast_spell(game.state)
    assert 'brine' in out.lower() or 'you cast' in out.lower()


def test_cast_on_item_purifies_pillars():
    """Casting Purify on WardingPillars should produce an event and glyph text."""
    spell = PurifySpell()
    act3 = Act3()
    act3.music_file = ''
    game = Game([act3])

    pillars = WardingPillars()
    out = spell.cast_on_item(game.state, pillars)
    assert '[event]' in out.lower()
    assert 'glyph' in out.lower() or 'tideward' in out.lower()
