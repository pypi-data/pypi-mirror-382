"""Unit tests for LowerSwitchbacks room in Act 3."""

from retroquest.act3.Act3 import Act3
from retroquest.engine.Game import Game


def test_lower_switchbacks_contains_canteen_and_scholar():
    """Lower Switchbacks should include an Emberwater Canteen and the Ash Scholar."""
    act3 = Act3()
    act3.music_file = ''
    _game = Game([act3])

    room = act3.rooms['LowerSwitchbacks']
    # check items and characters
    item_names = [i.get_name().lower() for i in room.get_items()]
    char_names = [c.get_name().lower() for c in room.get_characters()]

    assert 'emberwater canteen' in item_names
    assert 'ash scholar' in char_names
