"""Tests for WardingPillars item behavior."""

from retroquest.act3.Act3 import Act3
from retroquest.engine.Game import Game
from retroquest.act3.Act3StoryFlags import (
    FLAG_ACT3_WARDING_PILLARS_PURIFIED,
    FLAG_ACT3_TIDEWARD_SIGILS_COMPLETED,
)
from ...utils.utils import check_story_flag


def test_purify_sets_flag():
    """Purifying Warding PIllars should set the purification story flag."""
    act3 = Act3()
    act3.music_file = ''
    game = Game([act3])

    room = game.state.all_rooms['OuterWards']
    # Find the pillars in the room object
    pillars = next((i for i in room.items if i.__class__.__name__ == 'WardingPillars'), None)
    assert pillars is not None

    # Purify and ensure the flag is set
    out = pillars.purify(game.state)
    assert 'clean' in out.lower() or 'rins' in out.lower() or 'breathe' in out.lower()
    check_story_flag(game.state, FLAG_ACT3_WARDING_PILLARS_PURIFIED, True)


def test_examine_changes_with_purification():
    """Examine should return different text depending on purified state.

    When unpurified, the description mentions crust and a faint hum. After
    calling purify(), the examine text should reflect a radiant/pulsing state.
    """
    act3 = Act3()
    act3.music_file = ''
    game = Game([act3])

    room = game.state.all_rooms['OuterWards']
    pillars = next((i for i in room.items if i.__class__.__name__ == 'WardingPillars'), None)
    assert pillars is not None

    # Initial unpurified examine
    out_before = pillars.examine(game.state)
    assert 'crust' in out_before.lower() or 'mute' in out_before.lower()

    # Purify and then examine should show the purified description
    game.state.current_room = room
    purify_out = pillars.purify(game.state)
    assert 'rins' in purify_out.lower() or 'cleans' in purify_out.lower()

    out_after = pillars.examine(game.state)
    assert 'pulse' in out_after.lower() or 'radiant' in out_after.lower()


def test_name_changes_on_purify():
    """After purification the item's name should indicate purified state."""
    act3 = Act3()
    act3.music_file = ''
    game = Game([act3])

    room = game.state.all_rooms['OuterWards']
    pillars = next((i for i in room.items if i.__class__.__name__ == 'WardingPillars'), None)
    assert pillars is not None

    # Name before purification
    assert pillars.get_name() == 'Warding Pillars'

    # Purify and verify name changed
    game.state.current_room = room
    pillars.purify(game.state)
    assert pillars.get_name() == 'Warding Pillars (purified)'
    assert pillars.get_short_name() == 'Pillars'


def test_use_with_shards_before_and_after_purify():
    """Using MoonRuneShards on unpurified pillars fails; succeeds after purify.

    The shards should be consumed on successful engraving and the sigils flag
    should be set. Before purification, the use should return a failure and
    leave inventory untouched.
    """
    act3 = Act3()
    act3.music_file = ''
    game = Game([act3])

    room = game.state.all_rooms['OuterWards']
    pillars = next((i for i in room.items if i.__class__.__name__ == 'WardingPillars'), None)
    assert pillars is not None

    # Create shards and add to inventory
    from retroquest.act3.items.MoonRuneShards import MoonRuneShards

    shards = MoonRuneShards()
    game.state.add_item_to_inventory(shards)

    # Attempt to use shards on unpurified pillars -> failure, inventory unchanged
    fail_out = shards.use_with(game.state, pillars)
    assert '[failure]' in fail_out
    # Shards still present
    assert game.state.get_item_count('Moon Rune Shards') > 0

    # Now purify pillars, then use shards -> success, shards consumed, flag set
    game.state.current_room = room
    pillars.purify(game.state)

    success_out = shards.use_with(game.state, pillars)
    assert '[event]' in success_out
    # Shards consumed
    assert game.state.get_item_count('Moon Rune Shards') == 0
    # Sigils completed flag set
    check_story_flag(game.state, FLAG_ACT3_TIDEWARD_SIGILS_COMPLETED, True)
