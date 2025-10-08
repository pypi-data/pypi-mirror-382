from ...engine.Quest import Quest
from ...engine.GameState import GameState

class MagnetFishingExpeditionQuest(Quest):
    def __init__(self) -> None:
        super().__init__(
            name="Magnet fishing expedition",
            description="You have assembled a strange fishing rod with a magnet. Time to go on another fishing expedition!",
            completion="You have retrieved the shiny ring from the well, proving your ingenuity and determination."
        )

    def check_trigger(self, game_state: GameState) -> bool:
        return bool(game_state.get_item("magnetic fishing rod"))

    def check_completion(self, game_state: GameState) -> bool:
        return bool(game_state.get_item("shiny ring"))
