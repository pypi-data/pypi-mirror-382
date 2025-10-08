from ...engine.Quest import Quest
from ...engine.GameState import GameState

class KnowYourVillageQuest(Quest):
    def __init__(self) -> None:
        super().__init__(
            name="Know your village",
            description="You are encouraged to explore and get to know every corner of Willowbrook. The village holds many secrets for you to discover.",
            completion="You have explored every corner of Willowbrook. The village feels more like home, and you are ready for what lies ahead."
        )

    def check_trigger(self, game_state: GameState) -> bool:
        # Triggered when the player leaves Elior's Cottage for the first time
        return len(game_state.visited_rooms) > 1

    def check_completion(self, game_state: GameState) -> bool:
        # Completed when all village rooms have been visited
        return len(game_state.all_rooms) == len(game_state.visited_rooms)
