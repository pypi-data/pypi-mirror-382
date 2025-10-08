"""Tests for Act 3 Light spell."""

from retroquest.act3.spells.LightSpell import LightSpell
from retroquest.act3.items.PrismLantern import PrismLantern
from retroquest.act3.Act3 import Act3
from retroquest.engine.Game import Game


def test_cast_spell_no_hook_returns_event():
    """Ensure cast_spell returns an event-like string when no room hook exists."""
    act3 = Act3()
    act3.music_file = ''
    game = Game([act3])

    spell = LightSpell()
    # Ensure current room has no cast_light_here hook
    game.state.current_room = game.state.all_rooms['OuterWards']
    out = spell.cast_spell(game.state)
    assert '[event]' in out.lower() or '[failure]' in out.lower()


def test_cast_on_item_with_lantern_triggers_cast_spell():
    """Casting Light on a PrismLantern should trigger the spell's room-path output."""
    act3 = Act3()
    act3.music_file = ''
    game = Game([act3])

    spell = LightSpell()
    lantern = PrismLantern()
    game.state.current_room = game.state.all_rooms['OuterWards']
    out = spell.cast_on_item(game.state, lantern)
    assert '[event]' in out.lower() or '[failure]' in out.lower()
