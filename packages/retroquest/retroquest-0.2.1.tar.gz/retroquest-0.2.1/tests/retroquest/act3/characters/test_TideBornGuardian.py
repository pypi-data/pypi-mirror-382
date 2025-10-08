"""Tests for the TideBornGuardian character in Act 3."""

from retroquest.act3.characters.TideBornGuardian import TideBornGuardian
from retroquest.act3.Act3StoryFlags import FLAG_ACT3_VOW_OF_COURAGE_MADE
from retroquest.engine.GameState import GameState


class DummyRoom:
    """Minimal dummy room used when constructing a GameState for tests."""

    def __init__(self, name: str) -> None:
        """Initialize a dummy room with a name and empty items list."""
        self.name = name
        self.items = []


def _make_gs() -> GameState:
    """Create a minimal GameState for character tests."""
    return GameState(DummyRoom("TestRoom"), all_rooms={}, all_quests=[])


def test_tidebornguardian_talk_to_returns_prompt() -> None:
    """talk_to should return the guardian's prompt for a vow."""
    g = _make_gs()
    guardian = TideBornGuardian()

    res = guardian.talk_to(g)

    assert "will not abandon" in res


def test_tidebornguardian_say_to_sets_flag_on_myself() -> None:
    """say_to with 'myself' sets the vow flag and returns success text."""
    g = _make_gs()
    guardian = TideBornGuardian()

    # ensure flag is initially False/absent
    assert not g.get_story_flag(FLAG_ACT3_VOW_OF_COURAGE_MADE)

    res = guardian.say_to("myself", g)

    assert "Crystal of Light" in res
    assert g.get_story_flag(FLAG_ACT3_VOW_OF_COURAGE_MADE)


def test_tidebornguardian_say_to_rejects_other_words() -> None:
    """say_to with other words should not set the flag and returns dialogue."""
    g = _make_gs()
    guardian = TideBornGuardian()

    res = guardian.say_to("not the vow", g)

    assert "not the vow" in res
    assert not g.get_story_flag(FLAG_ACT3_VOW_OF_COURAGE_MADE)
