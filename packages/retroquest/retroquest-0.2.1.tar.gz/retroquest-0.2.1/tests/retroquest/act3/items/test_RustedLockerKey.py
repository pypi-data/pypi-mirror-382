"""Tests for RustedLockerKey item behavior."""

from retroquest.act3.Act3 import Act3
from retroquest.engine.Game import Game

def test_rusted_locker_key_name_and_pickup():
    """Check the Rusted Locker Key provides a plausible name."""
    act3 = Act3()
    act3.music_file = ''
    _game = Game([act3])

    from retroquest.act3.items.RustedLockerKey import RustedLockerKey
    key = RustedLockerKey()
    assert key.get_name().lower().startswith('rusted')

def test_rusted_locker_key_use_with_locker_fails_and_no_state_change():
    """Using the rusted key on the Locker should fail and not alter the room.

    The rusted key is a red herring: it cannot physically free the fused lock.
    Ensure the method returns a failure message, the locker remains locked, and
    no PrismLanterns are spawned into the room.
    """
    act3 = Act3()
    act3.music_file = ''
    game = Game([act3])

    room = game.state.all_rooms['CollapsedPier']
    locker = next((i for i in room.items if i.__class__.__name__ == 'Locker'), None)
    assert locker is not None

    # Find the rusted key item in the room (it may be present in the room by
    # default according to the act setup). If not present, create one via the
    # item's class to exercise use_with behaviour directly.
    rusted_key = next((i for i in room.items if i.__class__.__name__ == 'RustedLockerKey'), None)
    if rusted_key is None:
        # Import locally to avoid top-level import cycles in the test harness.
        from retroquest.act3.items.RustedLockerKey import RustedLockerKey

        rusted_key = RustedLockerKey()

    # Ensure the locker starts locked
    assert locker.locked is True

    # Set the game's current room so any side-effects would be added here.
    game.state.current_room = room

    # Use the rusted key on the locker and assert it fails with the expected
    # failure message and does not spawn lanterns or unlock the locker.
    out = rusted_key.use_with(game.state, locker)
    assert '[failure]' in out
    assert locker.locked is True

    # No PrismLanterns should have been added to the room as a result.
    lanterns = [i for i in room.items if i.__class__.__name__ == 'PrismLantern']
    assert len(lanterns) == 0
