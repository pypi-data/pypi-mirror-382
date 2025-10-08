"""Unit tests for CharredInscription item."""

import unittest
from retroquest.act3.items.CharredInscription import CharredInscription
from retroquest.act3.Act3 import Act3
from retroquest.engine.Game import Game


class TestCharredInscription(unittest.TestCase):
    """Test the Charred Inscription item."""

    def setUp(self):
        """Set up test fixtures."""
        self.act3 = Act3()
        self.act3.music_file = ''
        self.game = Game([self.act3])
        self.inscription = CharredInscription()

    def test_inscription_initialization(self):
        """Test that the inscription initializes correctly."""
        assert self.inscription.name == "Charred Inscription"
        assert self.inscription.short_name == "inscription"
        assert not self.inscription.can_be_carried_flag
        assert "Words burned deep into cooled lava" in self.inscription.description

    def test_inscription_examine_sets_flag(self):
        """Test that examining the inscription sets the story flag."""
        from retroquest.act3.Act3StoryFlags import FLAG_ACT3_CHARRED_INSCRIPTION_READ

        # Initially flag should not be set
        assert not self.game.state.get_story_flag(FLAG_ACT3_CHARRED_INSCRIPTION_READ)

        # Examine the inscription
        result = self.inscription.examine(self.game.state)

        # Flag should now be set
        assert self.game.state.get_story_flag(FLAG_ACT3_CHARRED_INSCRIPTION_READ)

        # Should contain the inscription text
        assert "In fire and flame we forge the final ward" in result
        assert "Should our son face the darkness" in result
        assert "courage from the depths" in result
        assert "wisdom from the heights" in result
        assert "sacrifice from the heart" in result

    def test_inscription_examine_multiple_times(self):
        """Test that examining multiple times works correctly."""
        from retroquest.act3.Act3StoryFlags import FLAG_ACT3_CHARRED_INSCRIPTION_READ

        # First examine
        result1 = self.inscription.examine(self.game.state)
        assert self.game.state.get_story_flag(FLAG_ACT3_CHARRED_INSCRIPTION_READ)

        # Second examine should still work
        result2 = self.inscription.examine(self.game.state)
        assert result1 == result2
        assert self.game.state.get_story_flag(FLAG_ACT3_CHARRED_INSCRIPTION_READ)


if __name__ == "__main__":
    unittest.main()
