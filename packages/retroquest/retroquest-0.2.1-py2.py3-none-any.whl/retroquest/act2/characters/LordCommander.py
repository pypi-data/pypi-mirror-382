"""LordCommander module: military authority who can restore Sir Cedric's honor."""

from typing import TYPE_CHECKING
from ...engine.Character import Character
from ..Act2StoryFlags import FLAG_CEDRIKS_HONOR_COMPLETED, FLAG_EXAMINED_SECRET_DOCUMENTS
from ..items.SecretDocuments import SecretDocuments

if TYPE_CHECKING:
    from ...engine.GameState import GameState

class LordCommander(Character):
    """The military leader of Greendale who can officially restore Sir Cedric's honor."""

    def __init__(self) -> None:
        super().__init__(
            name="lord commander",
            description=(
                "A distinguished military officer wearing elaborate ceremonial armor adorned "
                "with Greendale's coat of arms. His bearing speaks of years of command and "
                "the authority to make important decisions affecting the realm's knights."
            ),
        )

    def talk(self, game_state: 'GameState') -> str:
        """Handle talking to the Lord Commander (override matching base signature)."""
        if game_state.get_story_flag(FLAG_CEDRIKS_HONOR_COMPLETED):
            return (
                "The Lord Commander nods with satisfaction. "
                "\"Sir Cedric's honor has been fully restored. The false accusations against "
                "him have been officially stricken from the record. It brings me great "
                "pleasure to see justice served and a good knight vindicated.\""
            )
        if game_state.get_story_flag(FLAG_EXAMINED_SECRET_DOCUMENTS):
            # Player has the secret documents and should present them
            return (
                "The Lord Commander looks at you with interest. "
                "\"I understand you have evidence regarding Sir Cedric's case? If you have "
                "the secret documents that prove his innocence, please present them to me so "
                "I can officially restore his honor.\""
            )
        return (
            "The Lord Commander greets you formally. "
            "\"Welcome to Greendale's Great Hall. I oversee the military affairs of our "
            "realm and ensure that justice is served among our knights and soldiers.\""
        )

    def give_item(self, game_state: 'GameState', item_object) -> str:
        """Handle giving items to the Lord Commander (override matching base signature)."""
        if isinstance(item_object, SecretDocuments):
            if not game_state.get_story_flag(FLAG_EXAMINED_SECRET_DOCUMENTS):
                return (
                    "The Lord Commander examines the documents carefully but shakes his head. "
                    "\"These appear to be legal papers, but I need you to understand their "
                    "significance first. Please examine them thoroughly and then return to me.\""
                )

            # Player has examined the documents and understands their importance
            game_state.set_story_flag(FLAG_CEDRIKS_HONOR_COMPLETED, True)

            # Remove the documents from inventory
            game_state.inventory.remove(item_object)

            return (
                "[success]The Lord Commander carefully reviews the secret documents. "
                "His expression grows solemn as he reads the testimonies and evidence. "
                "\"These documents clearly prove Sir Cedric's innocence in the Battle of "
                "Thornfield Pass. The accusations of cowardice were completely unfounded - "
                "he was following direct orders and protecting civilians. I hereby officially "
                "restore Sir Cedric's honor and expunge all false charges from his record. "
                "Justice has been served at last.\"[/success]"
            )

        return f"The Lord Commander has no need for your {item_object.name}."
