"""Tests for MirrorMount item and mirror repair flow in Act 3."""

from retroquest.act3.Act3 import Act3
from retroquest.engine.Game import Game


def setup_game():
    """Set up a Game instance with Act 3 for MirrorMount tests."""
    act3 = Act3()
    act3.music_file = ''
    game = Game([act3])
    return game


def test_mount_examine_reveals_segment_once():
    """Test that examining the mount reveals a brass mirror segment only once."""
    game = setup_game()
    mount = __import__(
        'retroquest.act3.items.MirrorMount', fromlist=['MirrorMount']
    ).MirrorMount()

    # Ensure room is set up and current_room is available
    room = game.state.current_room
    # No segments in room initially
    assert all(i.get_name() != 'Brass Mirror Segment' for i in room.items)

    out = mount.examine(game.state)
    assert 'brass mirror segment' in out.lower()
    # Segment should now be present in the current room
    assert any(i.get_name() == 'Brass Mirror Segment' for i in room.items)

    # Examining again should not create another segment
    out2 = mount.examine(game.state)
    assert 'brass mirror segment' not in out2.lower()
    assert sum(1 for i in room.items if i.get_name() == 'Brass Mirror Segment') == 1


def test_install_resin_mend_flow():
    """Test the full install, resin, and mend flow for the MirrorMount item."""
    game = setup_game()
    state = game.state


    # Create mount and items using direct imports
    from retroquest.act3.items.MirrorMount import MirrorMount
    from retroquest.act3.items.BrassMirrorSegment import BrassMirrorSegment
    from retroquest.act3.items.BindingResin import BindingResin
    from retroquest.act3.spells.MendSpell import MendSpell

    mount = MirrorMount()

    # Add four segments and one resin to player's inventory
    for _ in range(4):
        state.add_item_to_inventory(BrassMirrorSegment())
    state.add_item_to_inventory(BindingResin())

    # Using a segment with the mount should install it (consume 4)
    seg = BrassMirrorSegment()
    res = mount.use_with(state, seg)
    assert 'success' in res.lower()
    # Inventory should have no Brass Mirror Segments left
    assert state.get_item_count('Brass Mirror Segment') == 0

    # Try to mend before applying resin -> should inform player to apply resin
    mend = MendSpell()
    out = mend.cast_on_item(state, mount)
    assert 'apply binding resin' in out.lower() or 'should apply' in out.lower()

    # Apply resin to the mount
    resin = BindingResin()
    out2 = mount.use_with(state, resin)
    assert 'success' in out2.lower()

    # Now mend should succeed and set the completion flag
    out3 = mend.cast_on_item(state, mount)
    assert 'success' in out3.lower()
    # Completion flag should be set in the game state
    from retroquest.act3.Act3StoryFlags import FLAG_ACT3_MIRRORS_OF_EMBER_LIGHT_COMPLETED
    assert state.get_story_flag(FLAG_ACT3_MIRRORS_OF_EMBER_LIGHT_COMPLETED)
