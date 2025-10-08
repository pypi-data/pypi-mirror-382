"""Basic tests for the Tideward Sigils quest trigger and completion."""

from retroquest.act3.Act3 import Act3
from retroquest.engine.Game import Game
from retroquest.act3.Act3StoryFlags import FLAG_ACT3_TIDEWARD_SIGILS_STARTED, \
    FLAG_ACT3_TIDEWARD_SIGILS_COMPLETED
from retroquest.act3.quests.TidewardSigils import TidewardSigilsQuest

def test_tideward_sigils_start_and_complete():
    """Quest trigger follows the started flag and completion follows completed flag."""
    act3 = Act3()
    act3.music_file = ''
    game = Game([act3])

    quest = TidewardSigilsQuest()

    # By default, not started
    game.state.set_story_flag(FLAG_ACT3_TIDEWARD_SIGILS_STARTED, False)
    assert quest.check_trigger(game.state) is False

    # When started flag set -> trigger true
    game.state.set_story_flag(FLAG_ACT3_TIDEWARD_SIGILS_STARTED, True)
    assert quest.check_trigger(game.state) is True

    # Completion follows completed flag
    game.state.set_story_flag(FLAG_ACT3_TIDEWARD_SIGILS_COMPLETED, False)
    assert quest.check_completion(game.state) is False

    game.state.set_story_flag(FLAG_ACT3_TIDEWARD_SIGILS_COMPLETED, True)
    assert quest.check_completion(game.state) is True
