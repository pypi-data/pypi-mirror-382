"""Unit tests for the Submerged Antechamber lantern mounting and gating."""

from typing import Optional

from retroquest.act3.Act3 import Act3
from retroquest.engine.Game import Game
from retroquest.act3.Act3StoryFlags import (
    FLAG_ACT3_LANTERNS_OF_THE_DEEPS_LIT,
    FLAG_ACT3_TIDEWARD_SIGILS_COMPLETED,
)

from ...utils.utils import (
    execute_commands,
    check_item_count_in_inventory,
    check_story_flag,
)


class TestSubmergedAntechamber:
    """Tests for mounting prism lanterns, casting light, and exit gating.

    Tests ensure that mounting three Prism Lanterns consumes them from
    inventory, that casting light with all brackets set updates the lanterns
    flag, and that the east exit is only visible when both the lanterns and
    tideward sigils flags are true.
    """
    act3: Optional[Act3] = None
    game: Optional[Game] = None

    def setup_method(self):
        """ Sets up act and game for testing """
        self.act3 = Act3()
        self.act3.music_file = ''
        self.game = Game([self.act3])
        self.game.state.current_room = self.game.state.all_rooms['SubmergedAntechamber']

    def test_mounting_lanterns_and_casting_light_sets_flag(self):
        """Mount three Prism Lanterns and cast light to set the lanterns flag.

        Preconditions: Player is in Submerged Antechamber with three Prism
        Lanterns in inventory.
        Actions: use prism lantern with lantern bracket three times, then cast light.
        Expected: inventory no longer contains prism lanterns and
        FLAG_ACT3_LANTERNS_OF_THE_DEEPS_LIT is True after casting light.
        """
        # Ensure three lanterns in inventory by adding them
        lantern = self.game.state.get_item('Prism Lantern')
        if lantern:
            self.game.state.add_item_to_inventory(lantern, count=3)
        else:
            from retroquest.act3.items.PrismLantern import PrismLantern
            self.game.state.add_item_to_inventory(PrismLantern(), count=3)

        check_item_count_in_inventory(self.game.state, 'Prism Lantern', 3)

        # Reveal the lantern brackets before attempting to mount lanterns
        # The antechamber hides its features until the Tideward Sigils are done;
        # set that flag so search can reveal the brackets for the unit test.
        self.game.state.set_story_flag(FLAG_ACT3_TIDEWARD_SIGILS_COMPLETED, True)
        execute_commands(self.game, ['search'])

        execute_commands(self.game, ['use prism lantern with lantern bracket'])
        execute_commands(self.game, ['use prism lantern with lantern bracket'])
        execute_commands(self.game, ['use prism lantern with lantern bracket'])

        check_item_count_in_inventory(self.game.state, 'Prism Lantern', 0)

        light = execute_commands(self.game, ['cast light'])
        assert 'path' in light.lower() or 'lantern' in light.lower()
        check_story_flag(self.game.state, FLAG_ACT3_LANTERNS_OF_THE_DEEPS_LIT, True)

    def test_east_exit_is_gated_on_two_flags(self):
        """Verify that the east exit to Sanctum is only present when both flags are set.

        Preconditions: Player in Submerged Antechamber. Both flags are unset.
        Actions: Inspect get_exits with no flags, set only lanterns flag, then set both
        flags and verify the east exit appears only in the final case.
        Expected: east absent initially, still absent when only one flag is set, and
        present when both flags are set.
        """
        room = self.game.state.current_room
        exits_initial = room.get_exits(self.game.state)
        assert 'east' not in exits_initial

        # Set only lanterns flag -> still should not reveal east
        self.game.state.set_story_flag(FLAG_ACT3_LANTERNS_OF_THE_DEEPS_LIT, True)
        exits_one = room.get_exits(self.game.state)
        assert 'east' not in exits_one

        # Now set sigils flag too -> east should appear
        self.game.state.set_story_flag(FLAG_ACT3_TIDEWARD_SIGILS_COMPLETED, True)
        exits_both = room.get_exits(self.game.state)
        assert 'east' in exits_both

    def test_search_reveals_brackets(self):
        """Ensure lantern brackets are not considered active before search but
        are present after searching the antechamber.

        Preconditions: Player is in Submerged Antechamber.
        Actions: inspect room items, then execute 'search' and re-inspect.
        Expected: Before searching, the room's items should not include three
        Lantern Brackets; after searching, the room should contain three
        Lantern Bracket items (the mounting points for Prism Lanterns).
        """
        room = self.game.state.current_room
        before = [type(i).__name__ for i in room.get_items()]
        # Lantern brackets should NOT be present before searching
        assert before.count('LanternBracket') == 0

        # Perform search before sigils are complete: the water should be too deep
        out_blocked = execute_commands(self.game, ['search'])
        assert ('impossible' in out_blocked.lower() or 'murky' in out_blocked.lower() or
                'too deep' in out_blocked.lower())
        after_blocked = [type(i).__name__ for i in room.get_items()]
        # Still no brackets should be present
        assert after_blocked.count('LanternBracket') == 0

        # Now complete the sigils and search again to reveal brackets
        self.game.state.set_story_flag(FLAG_ACT3_TIDEWARD_SIGILS_COMPLETED, True)
        out = execute_commands(self.game, ['search'])
        assert 'bracket' in out.lower() or 'brackets' in out.lower()
        after = [type(i).__name__ for i in room.get_items()]
        # After searching with sigils complete, the room should include three brackets
        assert after.count('LanternBracket') == 3
