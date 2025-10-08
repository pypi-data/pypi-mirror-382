"""Shadows Over Willowbrook main quest for Act I."""

from ...engine.Quest import Quest
from ...engine.GameState import GameState
from ..Act1StoryFlags import (
    FLAG_INVESTIGATED_WITHERED_CROPS,
    FLAG_VILLAGER_TALKED_TO,
    FLAG_WELL_EXAMINED,
    FLAG_CONNECT_WITH_NATURE,
    FLAG_MAGIC_FULLY_UNLOCKED,
    FLAG_SHADOWS_OVER_WILLOWBROOK_COMPLETED,
)

class ShadowsOverWillowbrookQuest(Quest):
    """Main Act I quest tracking the unfolding village corruption mystery.

    Rebuilds `self.description` on update, dimming prior segments and highlighting the
    newest narrative beat. Uses an internal `_flag_state` dict to avoid repeating the
    same revelation more than once.
    """
    def __init__(self) -> None:
        super().__init__(
            name="Shadows Over Willowbrook",
            description=(
                "Strange events are plaguing the village: crops are withering, animals are "
                "restless, and villagers whisper of a shadowy figure seen at night. "
                "Investigate the source of these disturbances."
            ),
            completion=(
                "You have confirmed that a dark force is at work in Willowbrook. Mira "
                "warns you that your magical abilities may be the key to protecting "
                "the village."
            )
        )
        self._flag_state = {}

    def check_trigger(self, game_state: GameState) -> bool:
        return True

    def check_update(self, game_state: GameState) -> bool:
        updated = False
        self.description = ''
        new_desc = (
            "Elior dreams of a shadowy figure lurking in the fields, its presence felt "
            "even in the waking world. The dream is unsettling, leaving him with a sense "
            "of foreboding that something is wrong in Willowbrook."
        )
        if game_state.get_story_flag(FLAG_INVESTIGATED_WITHERED_CROPS):
            if not self._flag_state.get(FLAG_INVESTIGATED_WITHERED_CROPS):
                self._flag_state[FLAG_INVESTIGATED_WITHERED_CROPS] = True
                updated = True
            self.description += '[dim]' + new_desc + '[/dim]'
            new_desc = (
                "\nElior has witnessed the devastation firsthand: once lush rows of crops now "
                "stand wilted and brown, their leaves curled and brittle. The earth beneath "
                "his feet is cracked and dry, and the air is thick with the scent of decay. "
                "Where there was once the promise of a bountiful harvest, there is now only "
                "ruin."
            )
        if game_state.get_story_flag(FLAG_VILLAGER_TALKED_TO):
            if not self._flag_state.get(FLAG_VILLAGER_TALKED_TO):
                self._flag_state[FLAG_VILLAGER_TALKED_TO] = True
                updated = True
            self.description += '[dim]' + new_desc + '[/dim]'
            new_desc = (
                "\nVillagers speak in hushed tones of strange happenings: animals refusing to "
                "leave their shelters, and shadows moving where none should be. Elior senses "
                "the fear growing among his neighbors, and the mystery deepens."
            )
        if game_state.get_story_flag(FLAG_WELL_EXAMINED):
            if not self._flag_state.get(FLAG_WELL_EXAMINED):
                self._flag_state[FLAG_WELL_EXAMINED] = True
                updated = True
            self.description += '[dim]' + new_desc + '[/dim]'
            new_desc = (
                "\nRumors spread of the village well: a foul stench rising from its depths, "
                "and water that no one dares to drink. Elior wonders if the source of the "
                "corruption lies beneath the surface."
            )
        if game_state.get_story_flag(FLAG_CONNECT_WITH_NATURE):
            if not self._flag_state.get(FLAG_CONNECT_WITH_NATURE):
                self._flag_state[FLAG_CONNECT_WITH_NATURE] = True
                updated = True
            self.description += '[dim]' + new_desc + '[/dim]'
            new_desc = (
                "\nMira has urged Elior to connect with the living world and learn from its "
                "magic. The path forward is uncertain, but hope stirs in the heart of "
                "Willowbrook."
            )
        if game_state.get_story_flag(FLAG_MAGIC_FULLY_UNLOCKED):
            if not self._flag_state.get(FLAG_MAGIC_FULLY_UNLOCKED):
                self._flag_state[FLAG_MAGIC_FULLY_UNLOCKED] = True
                updated = True
            self.description += '[dim]' + new_desc + '[/dim]'
            new_desc = (
                "\nElior has proven his magical abilities are real. The villagers will look to "
                "him with new hope, and Mira believes he may be the key to dispelling the "
                "darkness. Mira tells Elior that his journey must continue to Greendale, where "
                "he is to seek out the old druid at the forest's edge. Only there can he learn "
                "the deeper mysteries of nature's magic and find the knowledge needed to "
                "save Willowbrook."
            )
        self.description += new_desc
        return updated

    def check_completion(self, game_state: GameState) -> bool:
        return game_state.get_story_flag(FLAG_SHADOWS_OVER_WILLOWBROOK_COMPLETED)

    def is_main(self) -> bool:
        return True
