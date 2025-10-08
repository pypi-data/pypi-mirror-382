"""Tests for the Mirror Terraces room behaviour and quest gating."""

from retroquest.act3.Act3 import Act3
from retroquest.engine.Game import Game


def _find_mirror_terraces_room(game):
    # Accept either compact or spaced room keys depending on setup
    if "MirrorTerraces" in game.state.all_rooms:
        return game.state.all_rooms["MirrorTerraces"]
    return game.state.all_rooms["Mirror Terraces"]


def test_on_enter_sets_mirrors_started_flag():
    """Calling on_enter should set the mirrors-started story flag."""
    act3 = Act3()
    act3.music_file = ''
    game = Game([act3])
    room = _find_mirror_terraces_room(game)

    from retroquest.act3.Act3StoryFlags import FLAG_ACT3_MIRRORS_OF_EMBER_LIGHT_STARTED

    # ensure flag not set initially
    assert not game.state.get_story_flag(FLAG_ACT3_MIRRORS_OF_EMBER_LIGHT_STARTED)

    # call the room hook and verify the flag is set
    room.on_enter(game.state)
    assert game.state.get_story_flag(FLAG_ACT3_MIRRORS_OF_EMBER_LIGHT_STARTED)


def test_east_exit_hidden_until_mirrors_completed():
    """The east exit is hidden until the mirrors quest completion flag is set."""
    act3 = Act3()
    act3.music_file = ''
    game = Game([act3])
    room = _find_mirror_terraces_room(game)

    from retroquest.act3.Act3StoryFlags import (
        FLAG_ACT3_MIRRORS_OF_EMBER_LIGHT_COMPLETED,
    )

    # ensure completion flag is not set -> east exit should be hidden
    game.state.set_story_flag(FLAG_ACT3_MIRRORS_OF_EMBER_LIGHT_COMPLETED, False)
    exits_before = room.get_exits(game.state)
    assert "east" not in exits_before

    # set completion flag and verify east exit appears
    game.state.set_story_flag(FLAG_ACT3_MIRRORS_OF_EMBER_LIGHT_COMPLETED, True)
    exits_after = room.get_exits(game.state)
    assert "east" in exits_after
    assert exits_after["east"] == "FumarolePassages"

    # static mapping should still contain the east key
    assert "east" in room.exits
