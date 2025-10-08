"""Tests for PrismLantern item basic behaviors."""

from retroquest.act3.Act3 import Act3
from retroquest.engine.Game import Game


def test_prism_lantern_inventory_and_name():
    """Ensure Prism Lantern can be added to inventory and exposes a name."""
    act3 = Act3()
    act3.music_file = ''
    game = Game([act3])

    from retroquest.act3.items.PrismLantern import PrismLantern
    pl = PrismLantern()
    game.state.add_item_to_inventory(pl, count=2)
    assert game.state.get_item('Prism Lantern') is not None
    assert game.state.get_item('Prism Lantern').get_name() == 'Prism Lantern'


def test_prism_lantern_use_with_bracket_mounts_and_consumes():
    """Using a PrismLantern with a LanternBracket should mount it via room hook
    and remove it from inventory, setting the bracket's has_lantern to True.
    """
    act3 = Act3()
    act3.music_file = ''
    game = Game([act3])

    # Move player to Submerged Antechamber and reveal brackets by setting sigils flag
    room = game.state.all_rooms['SubmergedAntechamber']
    from retroquest.act3.Act3StoryFlags import FLAG_ACT3_TIDEWARD_SIGILS_COMPLETED
    game.state.set_story_flag(FLAG_ACT3_TIDEWARD_SIGILS_COMPLETED, True)
    game.state.current_room = room

    # Search to add brackets
    search_result = room.search(game.state)
    assert 'bracket' in search_result.lower() or 'niche' in search_result.lower()

    # Add a PrismLantern to inventory
    from retroquest.act3.items.PrismLantern import PrismLantern
    pl = PrismLantern()
    game.state.add_item_to_inventory(pl)
    assert game.state.has_item('Prism Lantern')

    # Find an empty bracket in the room
    from retroquest.act3.items.LanternBracket import LanternBracket
    bracket = next(
        (
            i
            for i in room.items
            if isinstance(i, LanternBracket) and not i.has_lantern
        ),
        None,
    )
    assert bracket is not None

    # Use the lantern with the bracket (should call room.mount_lantern)
    result = pl.use_with(game.state, bracket)
    assert '[event]' in result or 'seat' in result.lower()

    # Lantern removed from inventory and bracket updated
    assert not game.state.has_item('Prism Lantern')
    assert bracket.has_lantern is True
