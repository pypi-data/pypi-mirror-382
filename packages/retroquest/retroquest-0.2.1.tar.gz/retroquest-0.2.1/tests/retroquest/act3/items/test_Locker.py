"""Tests for Locker item behavior."""

from retroquest.act3.Act3 import Act3
from retroquest.engine.Game import Game
from retroquest.act3.items.RustedLockerKey import RustedLockerKey


def test_locker_examine_and_open_behaviour():
    """Locker in Collapsed Pier should be examinable and mention locks."""
    act3 = Act3()
    act3.music_file = ''
    game = Game([act3])

    room = game.state.all_rooms['CollapsedPier']
    locker = next((i for i in room.items if i.__class__.__name__ == 'Locker'), None)
    assert locker is not None
    out = locker.examine(game.state)
    assert 'lock' in out.lower() or 'fused' in out.lower()


def test_locker_open_fails_when_locked():
    """Attempting to open a locked locker should fail and not spawn lanterns."""
    act3 = Act3()
    act3.music_file = ''
    game = Game([act3])

    room = game.state.all_rooms['CollapsedPier']
    locker = next((i for i in room.items if i.__class__.__name__ == 'Locker'), None)
    assert locker is not None

    # Ensure initial locked state
    assert locker.locked is True
    # Ensure the game state's current room is the locker room so opened items
    # would be placed into the same room the locker inhabits.
    game.state.current_room = room
    result = locker.open(game.state)
    assert '[failure]' in result
    # No PrismLanterns should have been added
    lanterns = [i for i in room.items if i.__class__.__name__ == 'PrismLantern']
    assert len(lanterns) == 0
    assert locker.opened is False


def test_locker_unlock_and_open_spawns_lanterns():
    """Unlocking the locker then opening spawns three PrismLanterns and marks it opened."""
    act3 = Act3()
    act3.music_file = ''
    game = Game([act3])

    room = game.state.all_rooms['CollapsedPier']
    locker = next((i for i in room.items if i.__class__.__name__ == 'Locker'), None)
    assert locker is not None

    # Unlock then open
    game.state.current_room = room
    # Force the rusted key into the lock first so the mechanism can be freed
    rusted = RustedLockerKey()
    stuck_result = locker.use_with(game.state, rusted)
    assert '[failure]' in stuck_result
    unlock_result = locker.unlock(game.state)
    assert 'locker' in unlock_result.lower() or 'click' in unlock_result.lower()
    assert locker.locked is False

    open_result = locker.open(game.state)
    assert '[success]' in open_result
    # Three PrismLanterns should now be present in the room
    lanterns = [i for i in room.items if i.__class__.__name__ == 'PrismLantern']
    assert len(lanterns) == 3
    assert locker.opened is True

    # Subsequent open calls should report already open
    again = locker.open(game.state)
    assert 'already open' in again.lower()


def test_locker_unlock_fails_without_rusted_key():
    """Calling unlock without first jamming the rusted key should fail."""
    act3 = Act3()
    act3.music_file = ''
    game = Game([act3])

    room = game.state.all_rooms['CollapsedPier']
    locker = next((i for i in room.items if i.__class__.__name__ == 'Locker'), None)
    assert locker is not None

    # Ensure it's initially locked
    assert locker.locked is True
    game.state.current_room = room

    # Unlock attempt without a stuck rusted key should fail
    unlock_result = locker.unlock(game.state)
    assert '[failure]' in unlock_result
    assert locker.locked is True
