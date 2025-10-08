"""Caravan Master Thorne NPC and lost caravan side quest hook (Act II)."""

from ...engine.Character import Character
from ...engine.GameState import GameState
from ..Act2StoryFlags import (
    FLAG_SPOKEN_TO_CARAVAN_MASTER,
    FLAG_FOUND_LOST_CARAVAN,
    FLAG_LOST_CARAVAN_COMPLETED,
)
from ..items.SecretDocuments import SecretDocuments

class CaravanMasterThorne(Character):
    """Merchant NPC who triggers and rewards the lost caravan side quest."""
    def __init__(self) -> None:
        super().__init__(
            name="caravan master thorne",
            description=(
                "A weather-beaten man with worried eyes who oversees merchant caravans. "
                "He paces anxiously, clearly distressed about some urgent matter."
            ),
        )
        self.has_given_documents = False

    def talk_to(self, game_state: GameState) -> str:
        if game_state.get_story_flag(FLAG_FOUND_LOST_CARAVAN):
            if not self.has_given_documents:
                # Give Secret Documents as reward
                secret_docs = SecretDocuments()
                game_state.inventory.append(secret_docs)
                self.has_given_documents = True
                # Set the flag indicating the lost caravan quest is completed
                game_state.set_story_flag(FLAG_LOST_CARAVAN_COMPLETED, True)
                prefix = f"[character_name]{self.get_name()}[/character_name]: You've found them! "
                middle = (
                    "I cannot express my gratitude enough for bringing my people back safely. "
                    "As promised, here is your reward - but this is more than just payment. "
                    "These documents came into my possession years ago, and I believe they "
                    "contain evidence that could clear a good man's name. Perhaps you'll "
                    "know what to do with them.\n\n"
                )
                return prefix + middle + (
                    f"Thorne hands you a stack of [item_name]{secret_docs.get_name()}[/item_name]."
                )
            else:
                return (
                    f"[character_name]{self.get_name()}[/character_name]: I'm still processing "
                    "the relief of having my caravan safely returned. Those documents I "
                    "gave you - I hope they prove useful. Sometimes the right evidence "
                    "can restore honor where it was unjustly lost."
                )
        elif not game_state.get_story_flag(FLAG_SPOKEN_TO_CARAVAN_MASTER):
            game_state.set_story_flag(FLAG_SPOKEN_TO_CARAVAN_MASTER, True)
            return (
                f"[character_name]{self.get_name()}[/character_name]: Thank the gods, someone "
                "who looks capable! I desperately need help - one of my most valuable "
                "caravans has gone missing in the Enchanted Forest. It was carrying rare "
                "goods and several merchants. I fear the worst, but I must know their fate. "
                "Would you be willing to search for them? I would be forever in your debt."
            )
        else:
            return (
                f"[character_name]{self.get_name()}[/character_name]: Any word on my missing "
                "caravan? Every day that passes makes me fear the worst for those poor "
                "souls."
            )
