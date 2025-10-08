"""Basic tests for the Lanterns of the Deeps quest lifecycle."""

from retroquest.act3.Act3 import Act3
from retroquest.engine.Game import Game
from retroquest.act3.Act3StoryFlags import (
    FLAG_ACT3_LANTERNS_OF_THE_DEEPS_LIT,
    FLAG_ACT3_TIDEWARD_SIGILS_COMPLETED
)
from retroquest.act3.Act3StoryFlags import FLAG_ACT3_LANTERN_BRACKETS_FOUND
from retroquest.act3.quests.LanternsOfTheDeeps import LanternsOfTheDeepsQuest
from ...utils.utils import check_quests, check_story_flag


def test_trigger_only_after_sigils_and_in_correct_rooms():
    """Quest should not trigger before sigils complete; triggers in two rooms after."""
    act3 = Act3()
    act3.music_file = ''
    game = Game([act3])

    quest = LanternsOfTheDeepsQuest()

    # No sigils -> no trigger regardless of room
    game.state.current_room = game.state.all_rooms['CollapsedPier']
    game.state.set_story_flag(FLAG_ACT3_TIDEWARD_SIGILS_COMPLETED, False)
    assert quest.check_trigger(game.state) is False

    # After sigils complete -> triggers in Collapsed Pier
    game.state.set_story_flag(FLAG_ACT3_TIDEWARD_SIGILS_COMPLETED, True)
    # But brackets not yet found -> still no trigger
    assert quest.check_trigger(game.state) is False

    # Discover brackets via SubmergedAntechamber.search which should set flag
    game.state.current_room = game.state.all_rooms['SubmergedAntechamber']
    game.state.current_room.search(game.state)
    assert game.state.get_story_flag(FLAG_ACT3_LANTERN_BRACKETS_FOUND) is True

    # Now the quest should trigger in the Collapsed Pier and the Antechamber
    game.state.current_room = game.state.all_rooms['CollapsedPier']
    assert quest.check_trigger(game.state) is True

    # Triggers in Submerged Antechamber as well
    game.state.current_room = game.state.all_rooms['SubmergedAntechamber']
    assert quest.check_trigger(game.state) is True


def test_check_completion_reflects_lanterns_flag():
    """Completion follows the FLAG_ACT3_LANTERNS_OF_THE_DEEPS_LIT flag."""
    act3 = Act3()
    act3.music_file = ''
    game = Game([act3])

    quest = LanternsOfTheDeepsQuest()

    # Initially not completed
    game.state.set_story_flag(FLAG_ACT3_LANTERNS_OF_THE_DEEPS_LIT, False)
    assert quest.check_completion(game.state) is False

    # Once flag is set, quest is complete
    game.state.set_story_flag(FLAG_ACT3_LANTERNS_OF_THE_DEEPS_LIT, True)
    assert quest.check_completion(game.state) is True


def test_lanterns_of_the_deeps_flag_set_on_light():
    """Manually setting lanterns flag should reflect in game state and not error."""
    act3 = Act3()
    act3.music_file = ''
    game = Game([act3])

    # Start act and ensure quest list may or may not include this quest depending
    # on external triggers; just ensure flag interactions work.
    check_quests(game.state, [])

    # Set the lanterns flag and assert
    game.state.set_story_flag(FLAG_ACT3_LANTERNS_OF_THE_DEEPS_LIT, True)
    check_story_flag(game.state, FLAG_ACT3_LANTERNS_OF_THE_DEEPS_LIT, True)
