from ...engine.Quest import Quest
from ...engine.GameState import GameState
from ..Act1StoryFlags import FLAG_DEER_CAN_BE_OBSERVED

class OhDeerOhDeerQuest(Quest):
    def __init__(self) -> None:
        super().__init__(
            name="Oh deer, oh deer",
            description="You have heard tales of a magical deer from the Blacksmith. Perhaps you will witness something extraordinary yourself!",
            completion="You have observed the magical deer, gaining a deeper understanding of the wonders and mysteries of Eldoria."
        )

    def check_trigger(self, game_state: GameState) -> bool:
        return game_state.get_story_flag(FLAG_DEER_CAN_BE_OBSERVED)

    def check_completion(self, game_state: GameState) -> bool:
        return bool(game_state.get_item("rare flower"))
