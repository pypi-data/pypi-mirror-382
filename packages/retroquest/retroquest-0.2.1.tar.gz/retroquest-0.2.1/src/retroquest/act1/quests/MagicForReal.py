from ...engine.Quest import Quest
from ...engine.GameState import GameState
from ..Act1StoryFlags import FLAG_MAGIC_FULLY_UNLOCKED

class MagicForRealQuest(Quest):
    def __init__(self) -> None:
        super().__init__(
            name="Magic for real",
            description=(
                "You discover that you possess mysterious magical abilities. "
                "Strange phenomena begin to occur around you, hinting at a power you never knew you had. "
                "You must seek guidance and understanding to unlock the secrets of your newfound magic and learn what it means for your destiny."
            ),
            completion="You have embraced your magical abilities and taken your first steps on a path filled with wonder and danger. The world will never be the same for you."
        )

    def check_trigger(self, game_state: GameState) -> bool:
        return len(game_state.known_spells) > 0

    def check_completion(self, game_state: GameState) -> bool:
        return game_state.get_story_flag(FLAG_MAGIC_FULLY_UNLOCKED)
