"""Unit tests for the Collapsed Pier vault and rusted locker key."""

from typing import Optional

from retroquest.act3.Act3 import Act3
from retroquest.engine.Game import Game

class TestCollapsedPier:
    """Tests for discovering the rusted locker key and its idempotence.

    These tests jump to the Collapsed Pier and exercise the search mechanic
    that reveals the Rusted Locker Key, ensuring the reveal happens once and
    that taking the key moves it to the player's inventory.
    """
    act3: Optional[Act3] = None
    game: Optional[Game] = None

    def setup_method(self):
        """ Sets up act and game for testing """
        self.act3 = Act3()
        self.act3.music_file = ''
        self.game = Game([self.act3])
        self.game.state.current_room = self.game.state.all_rooms['CollapsedPier']
