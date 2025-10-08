"""Unit tests for KeepsakeNote item."""

import unittest
from retroquest.act3.items.KeepsakeNote import KeepsakeNote
from retroquest.act3.Act3 import Act3
from retroquest.engine.Game import Game


class TestKeepsakeNote(unittest.TestCase):
    """Test the Keepsake Note item."""

    def setUp(self):
        """Set up test fixtures."""
        self.act3 = Act3()
        self.act3.music_file = ''
        self.game = Game([self.act3])
        self.note = KeepsakeNote()

    def test_note_initialization(self):
        """Test that the note initializes correctly."""
        assert self.note.name == "Keepsake Note"
        assert self.note.short_name == "note"
        assert self.note.can_be_carried_flag
        assert "small, worn piece of parchment" in self.note.description

    def test_note_examine(self):
        """Test examining the note."""
        from retroquest.act3.Act3StoryFlags import FLAG_ACT3_ECHOES_QUEST_STARTED

        # Initially flag should not be set
        assert not self.game.state.get_story_flag(FLAG_ACT3_ECHOES_QUEST_STARTED)

        result = self.note.examine(self.game.state)

        # Flag should now be set
        assert self.game.state.get_story_flag(FLAG_ACT3_ECHOES_QUEST_STARTED)

        assert "Mira's words" in result
        assert "fragments of their story" in result
        assert "three testimonies will reveal" in result
        assert "depths where courage is tested" in result
        assert "heights where wisdom burns" in result
        assert "shadows where sacrifice echoes" in result


if __name__ == "__main__":
    unittest.main()
