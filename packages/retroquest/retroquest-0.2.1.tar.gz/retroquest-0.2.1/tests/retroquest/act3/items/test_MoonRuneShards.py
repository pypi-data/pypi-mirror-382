"""Tests for MoonRuneShards item basic behaviors."""

from retroquest.act3.Act3 import Act3
from retroquest.engine.Game import Game


def test_moon_rune_shards_can_be_added_to_inventory():
    """Moon Rune Shards should be addable to player inventory."""
    act3 = Act3()
    act3.music_file = ''
    game = Game([act3])

    from retroquest.act3.items.MoonRuneShards import MoonRuneShards
    shards = MoonRuneShards()
    game.state.add_item_to_inventory(shards)
    assert game.state.has_item('Moon Rune Shards')


def test_moon_rune_shards_use_with_pillars_flow():
    """Using shards with WardingPillars fails until pillars are purified, then
    consumes shards and sets the tideward sigils flag.
    """
    act3 = Act3()
    act3.music_file = ''
    game = Game([act3])

    from retroquest.act3.items.MoonRuneShards import MoonRuneShards
    from retroquest.act3.items.WardingPillars import WardingPillars
    from retroquest.act3.Act3StoryFlags import FLAG_ACT3_TIDEWARD_SIGILS_COMPLETED

    shards = MoonRuneShards()
    pillars = WardingPillars()

    # Attempt to use shards on unpurified pillars -> should fail
    result_fail = shards.use_with(game.state, pillars)
    assert '[failure]' in result_fail or 'clogged' in result_fail.lower()
    assert game.state.get_story_flag(FLAG_ACT3_TIDEWARD_SIGILS_COMPLETED) is False

    # Purify the pillars, add shards to inventory, then use -> should succeed
    purify_result = pillars.purify(game.state)
    assert 'rinse' in purify_result.lower() or 'cleansed' in purify_result.lower()
    # add shards to inventory so they can be consumed
    game.state.add_item_to_inventory(shards)
    assert game.state.has_item('Moon Rune Shards')

    result_ok = shards.use_with(game.state, pillars)
    assert '[event]' in result_ok
    # shards consumed
    assert not game.state.has_item('Moon Rune Shards')
    # flag set
    assert game.state.get_story_flag(FLAG_ACT3_TIDEWARD_SIGILS_COMPLETED) is True
