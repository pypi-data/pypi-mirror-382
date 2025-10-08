"""Tests for Mural item."""

from retroquest.act3.Act3 import Act3
from retroquest.engine.Game import Game


def test_mural_examine_returns_text():
    """Mural in the Tidal Causeway should return descriptive text on examine."""
    act3 = Act3()
    act3.music_file = ''
    game = Game([act3])

    room = game.state.all_rooms['TidalCauseway']
    mural = next((i for i in room.items if i.__class__.__name__ == 'Mural'), None)
    assert mural is not None
    # Ensure current_room is the mural room so examine side-effects affect it
    game.state.current_room = room
    out = mural.examine(game.state)
    assert 'sea' in out.lower() or 'reliquary' in out.lower()


def test_mural_examine_reveals_sea_sealed_letter_and_sets_flag():
    """First examine reveals Sea-Sealed Letter and sets the story flag."""
    act3 = Act3()
    act3.music_file = ''
    game = Game([act3])

    room = game.state.all_rooms['TidalCauseway']
    mural = next((i for i in room.items if i.__class__.__name__ == 'Mural'), None)
    assert mural is not None

    # Ensure examine uses the test room as current_room for side-effects
    game.state.current_room = room
    out = mural.examine(game.state)
    assert '[item_name]Sea-Sealed Letter' in out or 'sea-sealed letter' in out.lower()
    # letter should be added to the room
    letters = [i for i in room.items if i.__class__.__name__ == 'SeaSealedLetter']
    assert len(letters) == 1
    # Subsequant examine should not add another letter
    mural.examine(game.state)
    letters = [i for i in room.items if i.__class__.__name__ == 'SeaSealedLetter']
    assert len(letters) == 1
