"""Integration test for Echoes of the Hidden Bond quest in Act 3."""

import unittest
from retroquest.act3.Act3 import Act3
from retroquest.engine.Game import Game


class TestEchoesIntegration(unittest.TestCase):
    """Test the Echoes quest integration in Act 3."""

    def setUp(self):
        """Set up test fixtures."""
        self.act3 = Act3()
        self.act3.music_file = ''
        self.game = Game([self.act3])

    def test_echoes_quest_is_included_in_act3(self):
        """Test that the Echoes quest is included in Act 3 quest list."""
        quest_names = [quest.name for quest in self.act3.quests]
        assert "Echoes of the Hidden Bond" in quest_names

    def test_keepsake_note_available_from_mira(self):
        """Test that the keepsake note is given by Mira during first conversation."""
        # First conversation should give the keepsake note
        mira = self.game.state.all_rooms['MirasHut'].get_character_by_name('Mira')
        mira.talk_to(self.game.state)

        # Check that the note is now in inventory
        item_names = [item.get_name() for item in self.game.state.inventory]
        assert "Keepsake Note" in item_names

    def test_charred_inscription_in_mirror_terraces(self):
        """Test that the charred inscription is available in Mirror Terraces."""
        mirror_terraces = self.game.state.all_rooms['MirrorTerraces']
        item_names = [item.get_name() for item in mirror_terraces.items]
        assert "Charred Inscription" in item_names

    def test_quest_progression_flow(self):
        """Test basic quest progression flow."""
        from retroquest.act3.Act3StoryFlags import (
            FLAG_ACT3_ECHOES_QUEST_STARTED,
            FLAG_ACT3_SEA_SEALED_LETTER_READ,
            FLAG_ACT3_CHARRED_INSCRIPTION_READ,
            FLAG_ACT3_DRAGONS_MEMORY_RECEIVED,
        )

        # Start main quest to trigger Echoes quest
        self.game.state.set_story_flag(FLAG_ACT3_ECHOES_QUEST_STARTED, True)

        # Process quest activations (might need multiple calls)
        while self.game.state.next_activated_quest() is not None:
            pass

        # Find the Echoes quest
        echoes_quest = None
        for quest in self.game.state.activated_quests:
            if quest.name == "Echoes of the Hidden Bond":
                echoes_quest = quest
                break

        assert echoes_quest is not None

        # Test discovery progression
        self.game.state.set_story_flag(FLAG_ACT3_SEA_SEALED_LETTER_READ, True)
        echoes_quest.check_update(self.game.state)
        assert "✓ Depths of the Sunken Ruins" in echoes_quest.description

        self.game.state.set_story_flag(FLAG_ACT3_CHARRED_INSCRIPTION_READ, True)
        echoes_quest.check_update(self.game.state)
        assert "✓ Heights of Mount Ember" in echoes_quest.description

        self.game.state.set_story_flag(FLAG_ACT3_DRAGONS_MEMORY_RECEIVED, True)
        echoes_quest.check_update(self.game.state)
        assert "✓ Shadows of the Caverns" in echoes_quest.description

        # Test completion
        assert echoes_quest.check_completion(self.game.state)


if __name__ == "__main__":
    unittest.main()
