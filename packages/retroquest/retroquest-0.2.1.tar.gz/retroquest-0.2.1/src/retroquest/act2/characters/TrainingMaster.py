"""Training Master NPC definition.

Role:
    Veteran instructor who seeds the "Cedric's Lost Honor" investigation by
    setting ``FLAG_CEDRIKS_HONOR_ACCEPTED`` and providing contextual suspicion.

Design Notes:
    Dialogue intentionally embeds moral framing (truth, injustice) to motivate
    engagement with investigation mechanics and diary/document retrieval loops.
"""

from ...engine.Character import Character
from ...engine.GameState import GameState
from ..Act2StoryFlags import FLAG_CEDRIKS_HONOR_ACCEPTED

class TrainingMaster(Character):
    """Veteran instructor who seeds the Cedric honor investigation."""

    def __init__(self) -> None:
        super().__init__(
            name="training master",
            description=(
                "A grizzled veteran knight responsible for training the castle's squires "
                "and maintaining combat readiness. His weathered face and battle-scarred "
                "armor speak of many years of military service. He observes the training "
                "grounds with a critical eye, ensuring every move is precise and disciplined."
            ),
        )

    def talk_to(self, game_state: GameState) -> str:
        if not game_state.get_story_flag(FLAG_CEDRIKS_HONOR_ACCEPTED):
            # First time talking - trigger the quest
            game_state.set_story_flag(FLAG_CEDRIKS_HONOR_ACCEPTED, True)

            return (
                "[character_name]Training Master[/character_name]: Ah, a visitor to our "
                "training grounds. I've been instructing knights and squires here for "
                "many years. *He glances toward Sir Cedric with a troubled expression.* "
                "It pains me to see a fine knight like Sir Cedric carrying such a heavy "
                "burden. There are whispers about his past military service - accusations "
                "of cowardice during a critical battle. But I've known Cedric for years, "
                "and cowardice is not in his nature. Something about that whole affair "
                "never sat right with me. The official reports seemed... incomplete.\n\n"

                "[character_name]Training Master[/character_name]: *He leans closer, lowering "
                "his voice.* I've heard rumors that there were supposed to be documents - "
                "evidence that would clear his name. Perhaps someone with your skills could "
                "help uncover the truth and restore honor to a good man who has suffered "
                "long enough."
            )
        else:
            # Subsequent conversations
            return (
                "[character_name]Training Master[/character_name]: *He nods respectfully.* "
                "You're looking into Sir Cedric's situation? Good. That man has suffered "
                "under false accusations for far too long. The truth needs to come to "
                "light. Perhaps the squires might know more about what happened - they "
                "sometimes hear things that we older knights miss."
            )
