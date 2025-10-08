"""Basic tests for The Three Virtues quest activation."""

from retroquest.act3.Act3 import Act3
from retroquest.engine.Game import Game
from retroquest.act3.quests.TheThreeVirtues import TheThreeVirtuesQuest
from retroquest.act3.Act3StoryFlags import (
    FLAG_ACT3_MAIN_STARTED,
    FLAG_ACT3_MAIN_COMPLETED,
    FLAG_ACT3_CRYSTAL_OF_LIGHT_ACQUIRED,
    FLAG_ACT3_PHOENIX_FEATHER_ACQUIRED,
    FLAG_ACT3_DRAGONS_SCALE_ACQUIRED
)


def test_the_three_virtues_trigger_and_completion_flags():
    """Quest triggers when main started flag set and completes when main completed."""
    act3 = Act3()
    act3.music_file = ''
    _game = Game([act3])

    quest = TheThreeVirtuesQuest()

    # Not started by default
    _game.state.set_story_flag(FLAG_ACT3_MAIN_STARTED, False)
    assert quest.check_trigger(_game.state) is False

    # When main started flag set -> triggers
    _game.state.set_story_flag(FLAG_ACT3_MAIN_STARTED, True)
    assert quest.check_trigger(_game.state) is True

    # Completion follows main completed flag
    _game.state.set_story_flag(FLAG_ACT3_MAIN_COMPLETED, False)
    assert quest.check_completion(_game.state) is False

    _game.state.set_story_flag(FLAG_ACT3_MAIN_COMPLETED, True)
    assert quest.check_completion(_game.state) is True


def test_check_update_reflects_crystal_acquired():
    """When the Crystal of Light is acquired, check_update should return True
    and the quest description should be updated to acknowledge the player.
    """
    act3 = Act3()
    act3.music_file = ''
    game = Game([act3])

    quest = TheThreeVirtuesQuest()

    # Initially no crystal -> no update
    assert quest.check_update(game.state) is False

    # Now acquire the crystal -> should update once
    game.state.set_story_flag(FLAG_ACT3_CRYSTAL_OF_LIGHT_ACQUIRED, True)
    updated = quest.check_update(game.state)
    assert updated is True
    # Description should mention that the Crystal was claimed
    assert 'Crystal of Light' in quest.description

    # Subsequent calls should not report another update
    assert quest.check_update(game.state) is False


def test_check_update_reflects_phoenix_feather_acquired():
    """When the Phoenix Feather is acquired, check_update should return True
    and the quest description should be updated to acknowledge the player.
    """
    act3 = Act3()
    act3.music_file = ''
    game = Game([act3])
    quest = TheThreeVirtuesQuest()

    # Initially no feather -> no update
    assert quest.check_update(game.state) is False

    # Now acquire the feather -> should update once
    game.state.set_story_flag(FLAG_ACT3_PHOENIX_FEATHER_ACQUIRED, True)
    updated = quest.check_update(game.state)
    assert updated is True
    # Description should mention that the Phoenix Feather was obtained
    assert 'Phoenix Feather' in quest.description
    assert 'hope can rise' in quest.description

    # Subsequent calls should not report another update
    assert quest.check_update(game.state) is False


def test_check_update_reflects_both_crystal_and_feather():
    """When both the Crystal and Phoenix Feather are acquired, both should be acknowledged."""
    act3 = Act3()
    act3.music_file = ''
    game = Game([act3])
    quest = TheThreeVirtuesQuest()
    game.state.set_story_flag(FLAG_ACT3_CRYSTAL_OF_LIGHT_ACQUIRED, True)
    game.state.set_story_flag(FLAG_ACT3_PHOENIX_FEATHER_ACQUIRED, True)
    updated = quest.check_update(game.state)
    assert updated is True
    assert 'Crystal of Light' in quest.description
    assert 'Phoenix Feather' in quest.description
    assert 'hope can rise' in quest.description


def test_check_update_reflects_dragons_scale_acquired():
    """When the Dragon's Scale is acquired, check_update should return True
    and the quest description should be updated to acknowledge the player.
    """
    act3 = Act3()
    act3.music_file = ''
    game = Game([act3])
    quest = TheThreeVirtuesQuest()

    # Initially no scale -> no update
    assert quest.check_update(game.state) is False

    # Now acquire the scale -> should update once
    game.state.set_story_flag(FLAG_ACT3_DRAGONS_SCALE_ACQUIRED, True)
    updated = quest.check_update(game.state)
    assert updated is True
    # Description should mention that the Dragon's Scale was claimed
    assert "Dragon's Scale" in quest.description
    assert 'obsidian surface' in quest.description
    assert 'ancient power' in quest.description

    # Subsequent calls should not report another update
    assert quest.check_update(game.state) is False


def test_check_update_reflects_all_three_relics():
    """When all three relics are acquired, all should be acknowledged."""
    act3 = Act3()
    act3.music_file = ''
    game = Game([act3])
    quest = TheThreeVirtuesQuest()

    # Set all three flags
    game.state.set_story_flag(FLAG_ACT3_CRYSTAL_OF_LIGHT_ACQUIRED, True)
    game.state.set_story_flag(FLAG_ACT3_PHOENIX_FEATHER_ACQUIRED, True)
    game.state.set_story_flag(FLAG_ACT3_DRAGONS_SCALE_ACQUIRED, True)

    updated = quest.check_update(game.state)
    assert updated is True

    # All three relics should be mentioned
    assert 'Crystal of Light' in quest.description
    assert 'Phoenix Feather' in quest.description
    assert "Dragon's Scale" in quest.description

    # Final message should indicate all relics are obtained
    assert 'all three relics' in quest.description
    assert 'final trial awaits' in quest.description


def test_check_update_sequential_acquisition():
    """Test that acquiring relics sequentially updates correctly."""
    act3 = Act3()
    act3.music_file = ''
    game = Game([act3])
    quest = TheThreeVirtuesQuest()

    # First acquire Crystal
    game.state.set_story_flag(FLAG_ACT3_CRYSTAL_OF_LIGHT_ACQUIRED, True)
    assert quest.check_update(game.state) is True
    assert 'Crystal of Light' in quest.description
    assert 'steady brilliance' in quest.description
    # Should not have specific messages for other relics yet
    assert 'Phoenix Feather. Its warmth pulses' not in quest.description
    assert "Dragon's Scale, its obsidian surface" not in quest.description

    # Then acquire Phoenix Feather
    game.state.set_story_flag(FLAG_ACT3_PHOENIX_FEATHER_ACQUIRED, True)
    assert quest.check_update(game.state) is True
    assert 'steady brilliance' in quest.description
    assert 'Phoenix Feather. Its warmth pulses' in quest.description
    # Should not have Dragon's Scale specific message yet
    assert "Dragon's Scale, its obsidian surface" not in quest.description

    # Finally acquire Dragon's Scale
    game.state.set_story_flag(FLAG_ACT3_DRAGONS_SCALE_ACQUIRED, True)
    assert quest.check_update(game.state) is True
    assert 'steady brilliance' in quest.description
    assert 'Phoenix Feather. Its warmth pulses' in quest.description
    assert "Dragon's Scale, its obsidian surface" in quest.description
    assert 'all three relics' in quest.description
