"""Unit tests for EchoesOfTheHiddenBond quest."""

import unittest
from retroquest.act3.quests.EchoesOfTheHiddenBond import EchoesOfTheHiddenBondQuest
from retroquest.act3.Act3 import Act3
from retroquest.engine.Game import Game


class TestEchoesOfTheHiddenBondQuest(unittest.TestCase):
    """Test the Echoes of the Hidden Bond storytelling quest."""

    def setUp(self):
        """Set up test fixtures."""
        self.act3 = Act3()
        self.act3.music_file = ''
        self.game = Game([self.act3])
        self.quest = EchoesOfTheHiddenBondQuest()

    def test_quest_initialization(self):
        """Test that the quest initializes correctly."""
        assert self.quest.name == "Echoes of the Hidden Bond"
        assert not self.quest.is_main()
        assert "Your parents once walked" in self.quest.description

    def test_quest_trigger(self):
        """Test that the quest triggers when Act III main quest starts."""
        from retroquest.act3.Act3StoryFlags import FLAG_ACT3_ECHOES_QUEST_STARTED

        # Initially should not trigger
        assert not self.quest.check_trigger(self.game.state)

        # After main quest starts, should trigger
        self.game.state.set_story_flag(FLAG_ACT3_ECHOES_QUEST_STARTED, True)
        assert self.quest.check_trigger(self.game.state)

    def test_quest_updates_with_discoveries(self):
        """Test that the quest updates as discoveries are made."""
        from retroquest.act3.Act3StoryFlags import (
            FLAG_ACT3_MAIN_STARTED,
            FLAG_ACT3_SEA_SEALED_LETTER_READ,
            FLAG_ACT3_CHARRED_INSCRIPTION_READ,
            FLAG_ACT3_DRAGONS_MEMORY_RECEIVED,
        )

        # Start the quest
        self.game.state.set_story_flag(FLAG_ACT3_MAIN_STARTED, True)

        # Find Sea-Sealed Letter
        self.game.state.set_story_flag(FLAG_ACT3_SEA_SEALED_LETTER_READ, True)
        updated = self.quest.check_update(self.game.state)
        assert updated
        assert "✓ Depths of the Sunken Ruins" in self.quest.description
        assert "Malakar's apprentices" in self.quest.description

        # Read Charred Inscription
        self.game.state.set_story_flag(FLAG_ACT3_CHARRED_INSCRIPTION_READ, True)
        updated = self.quest.check_update(self.game.state)
        assert updated
        assert "✓ Heights of Mount Ember" in self.quest.description
        assert "protective ward they forged" in self.quest.description

        # Hear Dragon's Memory
        self.game.state.set_story_flag(FLAG_ACT3_DRAGONS_MEMORY_RECEIVED, True)
        updated = self.quest.check_update(self.game.state)
        assert updated
        assert "✓ Shadows of the Caverns" in self.quest.description
        assert "ancient dragon shared memories" in self.quest.description

    def test_quest_completion(self):
        """Test that the quest completes when all testimonies are found."""
        from retroquest.act3.Act3StoryFlags import (
            FLAG_ACT3_SEA_SEALED_LETTER_READ,
            FLAG_ACT3_CHARRED_INSCRIPTION_READ,
            FLAG_ACT3_DRAGONS_MEMORY_RECEIVED,
            FLAG_ACT3_ECHOES_QUEST_COMPLETED,
        )

        # Initially should not be complete
        assert not self.quest.check_completion(self.game.state)

        # With only some discoveries, should not be complete
        self.game.state.set_story_flag(FLAG_ACT3_SEA_SEALED_LETTER_READ, True)
        self.game.state.set_story_flag(FLAG_ACT3_CHARRED_INSCRIPTION_READ, True)
        assert not self.quest.check_completion(self.game.state)

        # With all discoveries, should be complete
        self.game.state.set_story_flag(FLAG_ACT3_DRAGONS_MEMORY_RECEIVED, True)
        assert self.quest.check_completion(self.game.state)

        # Should set completion flag
        assert self.game.state.get_story_flag(FLAG_ACT3_ECHOES_QUEST_COMPLETED)

        # Should not complete again
        assert not self.quest.check_completion(self.game.state)

    def test_quest_completion_text(self):
        """Test that the quest has appropriate completion text."""
        completion_text = self.quest.completion
        assert "three testimonies have revealed the truth" in completion_text
        assert "once apprentices to Malakar" in completion_text
        assert "hid Elior from Malakar's sight" in completion_text


if __name__ == "__main__":
    unittest.main()
