"""Room unit tests for Act 3 to verify room definitions and exits."""

from typing import Optional
from retroquest.act3.Act3 import Act3
from retroquest.act3.Act3StoryFlags import (
    FLAG_ACT3_LANTERNS_OF_THE_DEEPS_LIT,
    FLAG_ACT3_MIRRORS_OF_EMBER_LIGHT_COMPLETED,
    FLAG_ACT3_TIDEWARD_SIGILS_COMPLETED,
    FLAG_ACT3_BREATH_OF_THE_MOUNTAIN_COMPLETED,
    FLAG_ACT3_MINERS_RESCUE_COMPLETED,
    FLAG_ACT3_OATH_OF_STILLNESS_COMPLETED,
)
from retroquest.engine.Game import Game

class TestAct3Rooms:
    """Tests for Act 3 room functionality."""
    act3: Optional[Act3] = None
    game: Optional[Game] = None

    def setup_method(self):
        """Set up test fixtures."""
        self.act3 = Act3()
        self.act3.music_file = ''

    def test_act3_has_rooms(self):
        """Test that Act 3 has rooms defined."""
        assert isinstance(self.act3.rooms, dict)
        assert len(self.act3.rooms) > 0

    def test_all_exits_are_bidirectional(self):
        """Ensure every cardinal exit has a matching reverse exit back to the origin room."""
        game = Game([self.act3])
        reverse = {"north": "south", "south": "north", "east": "west", "west": "east"}

        # Enable Act 3 gating flags so conditional exits (like the sanctum)
        # are visible for the purpose of validating bidirectionality.
        game.state.set_story_flag(FLAG_ACT3_LANTERNS_OF_THE_DEEPS_LIT, True)
        game.state.set_story_flag(FLAG_ACT3_TIDEWARD_SIGILS_COMPLETED, True)
        game.state.set_story_flag(FLAG_ACT3_MIRRORS_OF_EMBER_LIGHT_COMPLETED, True)
        # Breath of the Mountain must be considered completed so the south exit
        # from Fumarole Passages is visible during the bidirectionality check.
        game.state.set_story_flag(FLAG_ACT3_BREATH_OF_THE_MOUNTAIN_COMPLETED, True)
        # Miners rescue must be completed so the east exit from CollapsedGalleries
        # to EchoChambers is visible during the bidirectionality check.
        game.state.set_story_flag(FLAG_ACT3_MINERS_RESCUE_COMPLETED, True)
        # Oath of Stillness must be completed so the east exit from StillnessVestibule
        # to DragonsHall is visible during the bidirectionality check.
        game.state.set_story_flag(FLAG_ACT3_OATH_OF_STILLNESS_COMPLETED, True)

        # Iterate through rooms by key so we can validate target links precisely
        for room_key, room in self.act3.rooms.items():
            exits = room.get_exits(game.state)
            for direction, target_key in exits.items():
                # Only enforce bi-directionality for standard cardinal directions
                if direction not in reverse:
                    continue
                assert target_key in self.act3.rooms, (
                    f"Exit from {room_key} via '{direction}' points to unknown room "
                    f"'{target_key}'."
                )
                target_room = self.act3.rooms[target_key]
                target_exits = target_room.get_exits(game.state)
                reverse_dir = reverse[direction]
                assert reverse_dir in target_exits, (
                    f"Room '{target_key}' must have a '{reverse_dir}' exit back to '{room_key}'."
                )
                assert target_exits[reverse_dir] == room_key, (
                    f"Reverse exit mismatch: from '{target_key}' via '{reverse_dir}'"
                    f" should go back to '{room_key}', "
                    f"but goes to '{target_exits[reverse_dir]}'."
                )
