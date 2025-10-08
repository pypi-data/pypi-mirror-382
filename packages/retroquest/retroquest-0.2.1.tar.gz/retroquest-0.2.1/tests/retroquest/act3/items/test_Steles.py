"""Tests for Steles item and searching behavior."""

from retroquest.act3.Act3 import Act3
from retroquest.engine.Game import Game


def test_steles_in_room_and_searchable():
    """Assert Steles exist in the ShorelineMarkers room and can be examined."""
    act3 = Act3()
    act3.music_file = ''
    game = Game([act3])

    room = game.state.all_rooms['ShorelineMarkers']
    steles = next((i for i in room.items if i.__class__.__name__ == 'Steles'), None)
    assert steles is not None
    out = steles.examine(game.state)
    assert isinstance(out, str)
