"""Tests for OathOfStillness quest."""
import unittest
from unittest.mock import Mock

from retroquest.engine.GameState import GameState
from retroquest.act3.quests.OathOfStillness import OathOfStillness
from retroquest.act3.Act3StoryFlags import (
    FLAG_ACT3_OATH_OF_STILLNESS_COMPLETED,
    FLAG_ACT3_OATH_OF_STILLNESS_STARTED,
)


class TestOathOfStillness(unittest.TestCase):
    """Test the OathOfStillness quest."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.quest = OathOfStillness()
        self.game_state = Mock(spec=GameState)

    def test_quest_initialization(self) -> None:
        """Test quest is properly initialized."""
        assert self.quest.name == "Oath of Stillness"
        assert "Echo Chambers whisper" in self.quest.description
        assert "illusions have fallen silent" in self.quest.completion
        assert not self.quest.is_main()

    def test_trigger_requires_miners_rescue_completed(self) -> None:
        """Test quest triggers when miners rescue is completed."""
        # Should not trigger without miners rescue completion
        self.game_state.get_story_flag.return_value = False
        assert not self.quest.check_trigger(self.game_state)

        # Should trigger when echo stones are examined
        self.game_state.get_story_flag.return_value = True
        assert self.quest.check_trigger(self.game_state)
        self.game_state.get_story_flag.assert_called_with(FLAG_ACT3_OATH_OF_STILLNESS_STARTED)

    def test_completion_requires_oath_flag(self) -> None:
        """Test quest completion depends on the oath completed flag."""
        # Should not be complete without the flag
        self.game_state.get_story_flag.return_value = False
        assert not self.quest.check_completion(self.game_state)

        # Should be complete with the flag
        self.game_state.get_story_flag.return_value = True
        assert self.quest.check_completion(self.game_state)
        self.game_state.get_story_flag.assert_called_with(FLAG_ACT3_OATH_OF_STILLNESS_COMPLETED)


if __name__ == "__main__":
    unittest.main()
