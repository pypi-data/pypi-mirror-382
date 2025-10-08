from ...engine.Quest import Quest
from ...engine.GameState import GameState

class CuriosityKilledTheCatQuest(Quest):
    def __init__(self) -> None:
        super().__init__(
            name="Curiosity killed the cat",
            description="You stand before a locked shed, its secrets hidden from you. What will you discover if you find a way inside?",
            completion="You have unlocked the Abandoned Shed and revealed its secrets. Your curiosity has led you deeper into the mysteries of Willowbrook."
        )

    def check_trigger(self, game_state: GameState) -> bool:
        return "Abandoned Shed" in game_state.visited_rooms

    def check_completion(self, game_state: GameState) -> bool:
        # Assume a story flag is set when the shed door is unlocked
        return game_state.get_room('Abandoned Shed').locked == False
