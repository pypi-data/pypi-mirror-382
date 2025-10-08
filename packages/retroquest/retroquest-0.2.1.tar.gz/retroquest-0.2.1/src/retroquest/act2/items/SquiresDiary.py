"""Squire's Diary item for Act II; an investigative journal advancing Cedric's quest."""

from ...engine.Item import Item
from ...engine.GameState import GameState
from ..Act2StoryFlags import FLAG_READ_SQUIRES_DIARY


class SquiresDiary(Item):
    """A personal diary containing clues about Sir Cedric's past and missing documents."""
    def __init__(self) -> None:
        super().__init__(
            name="squire's diary",
            short_name="diary",
            description=(
                "A worn leather-bound diary belonging to a former squire. The pages are "
                "filled with observations about castle life and training exercises. There are "
                "also notes about Sir Cedric's supposed disgrace and details about events from "
                "years ago."
            ),
            can_be_carried=True,
        )

    def use(self, game_state: GameState) -> str:
        """Use the diary: set story flag, remove the item, and return narrative text."""
        # Set the flag that the squire's diary has been read
        game_state.set_story_flag(FLAG_READ_SQUIRES_DIARY, True)

        # Remove the diary from inventory and/or current room after use
        if self in game_state.inventory:
            game_state.inventory.remove(self)
        if self in game_state.current_room.items:
            game_state.current_room.items.remove(self)

        # The quest should already be accepted by talking to Training Master
        return (
            "[event]You carefully read through the squire's diary. The entries reveal a "
            "troubling story...[/event]\n\n"

            "*Entry from three years ago:* 'Sir Cedric has been accused of abandoning "
            "his post during the Battle of Thornfield Pass. Official reports claim he fled "
            "when the enemy charged, leaving his men behind. But this makes no sense - Sir "
            "Cedric is the most honorable knight I've ever known.'\n\n"

            "*Later entry:* 'I've been asking questions, and something doesn't add up. A "
            "merchant caravan was due from Heavensforth, carrying secret military documents "
            "that could prove Sir Cedric's innocence. Those documents contained witness "
            "testimonies and reports that showed the real truth about Thornfield Pass.'\n\n"

            "*Final entry:* 'The caravan arrived, but the secret documents were nowhere to "
            "be found. The merchants claimed they never received such documents. There were "
            "rumors of attacks and lost goods along the mountain roads. Without those "
            "documents, Sir Cedric's name could not be cleared. I pray someone will find the "
            "truth and restore his honor.'\n\n"

            "[success]The diary confirms what the Training Master suspected - secret "
            "documents from Heavensforth would clear Sir Cedric's name. They "
            "mysteriously went missing when the caravan arrived. The lost caravan's "
            "documents might still be out there...[/success]\n\n"

            "[event]After reading the diary, you place it back where you found it. This keeps "
            "the information safe while you no longer carry the diary.[/event]"
        )

    def examine(self, _game_state: GameState) -> str:
        """Return a short examination string describing the diary and its entries."""
        msg = (
            "[event]You examine the [item_name]squire's diary[/item_name]. {0} "
            "The handwriting is careful and deliberate. Several entries focus on Sir "
            "Cedric's disgrace and the missing evidence that could clear his name.[/event]"
        )
        return msg.format(self.description)
