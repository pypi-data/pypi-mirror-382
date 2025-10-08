"""Unit tests for the Outer Wards room and tideward sigil mechanics."""

from typing import Optional

from retroquest.act3.Act3 import Act3
from retroquest.engine.Game import Game

from ...utils.utils import execute_commands


class TestOuterWards:
    """Tests for purifying pillars and completing the Tideward Sigils quest.

    Tests focus on the interaction between the Purify spell, WardingPillars and
    Moon Rune Shards. They set up the room state directly and exercise the
    spell/item hooks used by the Act 3 quest.
    """
    act3: Optional[Act3] = None
    game: Optional[Game] = None

    def setup_method(self):
        """ Sets up act and game for testing """
        self.act3 = Act3()
        self.act3.music_file = ''
        self.game = Game([self.act3])
        # Jump to Outer Wards for focused testing
        self.game.state.current_room = self.game.state.all_rooms['OuterWards']

    def test_search_mentions_pillars(self):
        """Searching the Outer Wards mentions the pillars.

        Preconditions: Player is positioned in the Outer Wards.
        Actions: execute 'search'.
        Expected: The returned text references the warding pillars (contains
        the substring 'pillar').
        """
        out = execute_commands(self.game, ['search'])
        assert 'pillar' in out.lower()
