"""Unit tests for the Shoreline Markers room and rune shard discovery."""

from typing import Optional

from retroquest.act3.Act3 import Act3
from retroquest.engine.Game import Game

from ...utils.utils import (
    execute_commands,
    check_item_in_room,
    check_item_in_inventory,
)


class TestShorelineMarkers:
    """Tests for searching the steles and collecting Moon Rune Shards.

    Each test documents preconditions, actions, expected outcomes and
    failure modes. Tests operate by jumping the game state directly to the
    Shoreline Markers room so that the suite focuses on room mechanics.
    """
    act3: Optional[Act3] = None
    game: Optional[Game] = None

    def setup_method(self):
        """Set up act and game instances used by each test method."""
        self.act3 = Act3()
        self.act3.music_file = ''
        self.game = Game([self.act3])
        # Focus tests on the Shoreline Markers
        self.game.state.current_room = self.game.state.all_rooms['ShorelineMarkers']

    def test_search_reveals_moon_rune_shards_and_take(self):
        """Verify that searching reveals Moon Rune Shards and they can be taken.

        Preconditions: player is in Shoreline Markers, holds no shards, and none
        are present in the room.

        Actions: execute 'search', then 'take moon rune shards'.

        Expected: search output references shards, shards appear in the room,
        and taking them moves them into the player's inventory.
        """
        check_item_in_room(self.game.state.current_room, 'Moon Rune Shards', False)
        check_item_in_inventory(self.game.state, 'Moon Rune Shards', False)

        out = execute_commands(self.game, ['search'])
        assert 'moon' in out.lower() or 'shard' in out.lower()

        check_item_in_room(self.game.state.current_room, 'Moon Rune Shards', True)

        execute_commands(self.game, ['take moon rune shards'])
        check_item_in_inventory(self.game.state, 'Moon Rune Shards', True)

    def test_research_is_idempotent(self):
        """Ensure repeated searches do not create duplicate shards.

        Preconditions: player is in Shoreline Markers.

        Actions: search twice (without taking) and assert the second result
        signals that the shards are already available.

        Expected: only one instance of Moon Rune Shards remains after both
        searches and the second output contains an 'already' style message.
        """
        first = execute_commands(self.game, ['search'])
        assert 'moon' in first.lower() or 'shard' in first.lower()

        second = execute_commands(self.game, ['search'])
        assert 'already' in second.lower() or 'again' in second.lower()

        # Only one instance should be present
        items = [
            i.get_name()
            for i in self.game.state.current_room.get_items()
        ]
        assert items.count('Moon Rune Shards') == 1


    def test_search_does_not_recreate_shards_after_removal(self):
        """Once revealed, later searches should not recreate shards after removal.

        Flow: search -> shards revealed -> remove shards from room and
        inventory -> search again -> no new shards should be created.
        """
        # Reveal shards via search
        self.game.state.current_room.search(self.game.state)
        items_here = self.game.state.current_room.get_items()
        assert any(
            i.get_name() == 'Moon Rune Shards' for i in items_here
        )

        # Remove shards from room and ensure not in inventory
        self.game.state.current_room.remove_item('Moon Rune Shards')
        self.game.state.remove_all_items_from_inventory('Moon Rune Shards')
        items_here = self.game.state.current_room.get_items()
        assert not any(
            i.get_name() == 'Moon Rune Shards' for i in items_here
        )
        assert self.game.state.get_item_count('Moon Rune Shards') == 0

        # Subsequent search should not recreate shards
        out = self.game.state.current_room.search(self.game.state)
        assert 'already' in out.lower() or 'again' in out.lower()
        items_here = self.game.state.current_room.get_items()
        assert not any(
            i.get_name() == 'Moon Rune Shards' for i in items_here
        )
