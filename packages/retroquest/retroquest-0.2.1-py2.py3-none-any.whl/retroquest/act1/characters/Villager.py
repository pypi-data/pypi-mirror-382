from ...engine.GameState import GameState
from ...engine.Character import Character
from ..Act1StoryFlags import FLAG_VILLAGER_TALKED_TO

class Villager(Character):
    def __init__(self) -> None:
        super().__init__(
            name="villager",
            description="A friendly Willowbrook local, always eager to share the latest gossip or rumors about the village."
        )
        self.dialogue_options = [
            "Have you seen the fields lately? The crops are withering overnight, and no one knows why. It's like the land itself is sick...",
            "Last night, someone spotted a cloaked stranger near the old well. Folks say he vanished when the moon went behind the clouds.",
            "The animals are restless. My neighbor's dog howled at nothing for hours, and the chickens refuse to leave their coop after dusk.",
            "Strange footprints appeared by the riverbank this morning—too large for any villager, and they led straight into the woods.",
            "Mira says the air feels heavy with magic, and the chapel bell rang by itself at midnight. Something's not right in Willowbrook."
        ]
        self.dialogue_index = 0

    def talk_to(self, game_state: GameState) -> str:
        game_state.set_story_flag(FLAG_VILLAGER_TALKED_TO, True)
        dialogue = self.dialogue_options[self.dialogue_index]
        self.dialogue_index = (self.dialogue_index + 1) % len(self.dialogue_options) # Cycle through dialogue
        event_msg = f"[event]You speak with the [character_name]{self.get_name()}[/character_name].[/event]"
        return event_msg + "\n" + f"'{dialogue}'"
