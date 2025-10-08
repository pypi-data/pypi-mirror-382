"""Historians NPC providing lore validation and archival review in Act II."""

from ...engine.Character import Character
from ...engine.GameState import GameState
from ...engine.Item import Item
from ..Act2StoryFlags import (
    FLAG_SHOWED_JOURNAL_TO_HISTORIANS,
    FLAG_READ_TRAVELERS_JOURNAL,
)

class Historians(Character):
    """Group of scholars who validate lore and inspect historical documents."""
    def __init__(self) -> None:
        super().__init__(
            name="historians",
            description=(
                "A group of learned scholars who maintain the court's historical records and "
                "genealogical archives. They are eager to examine any historical documents or "
                "artifacts."
            ),
        )
    def talk_to(self, game_state: GameState) -> str:
        """Return appropriate dialogue when the player talks to the Historians."""
        name = self.get_name()
        if game_state.get_story_flag(FLAG_SHOWED_JOURNAL_TO_HISTORIANS):
            prefix = (
                f"[character_name]{name}[/character_name]: "
                "The journal you showed us was most "
            )
            return prefix + (
                "illuminating! The references to Willowbrook's bloodlines confirm what "
                "we suspected from the ancient chronicles. Your heritage appears to be "
                "quite significant indeed."
            )
        else:
            return (
                f"[character_name]{name}[/character_name]: Welcome to the historical archives. We "
                "maintain records of regional history, family genealogies, and ancient "
                "chronicles. Do you have any historical documents or artifacts you'd like us "
                "to examine?"
            )

    def give_item(self, game_state: GameState, item_object: Item) -> str:
        """Handle giving items to the Historians."""
        from ..items.TravelersJournal import TravelersJournal

        if isinstance(item_object, TravelersJournal):
            if not game_state.get_story_flag(FLAG_READ_TRAVELERS_JOURNAL):
                return (
                    "[failure]You should not give things away that you know nothing about. "
                    "Perhaps you should ensure that you understand its contents before "
                    "sharing it with others.[/failure]"
                )

            game_state.set_story_flag(FLAG_SHOWED_JOURNAL_TO_HISTORIANS, True)
            hist_name = self.get_name()
            item_name = item_object.get_name()
            success_msg = (
                f"[success]You show the [item_name]{item_name}[/item_name] to the "
                f"[character_name]{hist_name}[/character_name]. "
                "They examine it with great interest, "
                "cross-referencing the records. "
                "Their study of the genealogical information reveals details "
                "that would take ordinary scholars years to compile. "
                "'This is fascinating! The journal confirms several theories about "
                "Willowbrook's significance and provides crucial context for the "
                "ancient chronicles.'[/success]"
            )
            return success_msg
        else:
            return super().give_item(game_state, item_object)
