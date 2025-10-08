"""Smoke tests for Sir Cedric character."""

from retroquest.act3.characters.SirCedric import SirCedric
from retroquest.act3.Act3 import Act3
from retroquest.engine.Game import Game


def test_sir_cedric_name_and_speak():
    """Sir Cedric reports the expected name in lowercase."""
    act3 = Act3()
    act3.music_file = ''
    _game = Game([act3])
    s = SirCedric()
    assert s.get_name().lower() == 'sir cedric'


def test_sir_cedric_directs_to_mira_before_quest():
    """Before the main quest, Sir Cedric points the player to Mira."""
    act3 = Act3()
    act3.music_file = ''
    game = Game([act3])
    s = SirCedric()
    out = s.talk_to(game.state)
    assert 'Mira' in out


def test_sir_cedric_tidal_causeway_responses():
    """Sir Cedric replies differently at Tidal Causeway based on flags."""
    act3 = Act3()
    act3.music_file = ''
    game = Game([act3])
    s = SirCedric()
    # start the main quest
    from retroquest.act3.Act3StoryFlags import FLAG_ACT3_MAIN_STARTED
    game.state.set_story_flag(FLAG_ACT3_MAIN_STARTED, True)
    # place player at Tidal Causeway
    game.state.current_room = game.state.all_rooms['TidalCauseway']
    from retroquest.act3.Act3StoryFlags import FLAG_ACT3_CRYSTAL_OF_LIGHT_ACQUIRED
    from retroquest.act3.Act3StoryFlags import FLAG_ACT3_VOW_OF_COURAGE_MADE

    # no crystal: tide advice
    game.state.set_story_flag(FLAG_ACT3_CRYSTAL_OF_LIGHT_ACQUIRED, False)
    out = s.talk_to(game.state)
    assert 'tide' in out.lower()

    # crystal acquired but no vow: ask to make vow
    game.state.set_story_flag(FLAG_ACT3_CRYSTAL_OF_LIGHT_ACQUIRED, True)
    game.state.set_story_flag(FLAG_ACT3_VOW_OF_COURAGE_MADE, False)
    out = s.talk_to(game.state)
    assert 'vow' in out.lower()

    # vow made: acknowledge and encourage
    game.state.set_story_flag(FLAG_ACT3_VOW_OF_COURAGE_MADE, True)
    out = s.talk_to(game.state)
    assert 'vow' in out.lower() or 'let us press onward' in out.lower()
