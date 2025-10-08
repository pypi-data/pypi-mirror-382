"""The Gathering Storm (Act II Main Quest) Module.

Primary narrative backbone for Act II, aggregating progression across multiple
side quests and developmental threads.

Always Active:
- Becomes available immediately upon Act II start (``check_trigger`` returns True).

Progression Sources (monitored flags):
1. ``FLAG_SPOKEN_TO_SIR_CEDRIC`` – establishes quest framing & need for allies.
2. ``FLAG_DEMONSTRATED_COMBAT_SKILLS`` – validates martial readiness.
3. ``FLAG_SUPPLIES_QUEST_COMPLETED`` – confirms expedition preparedness.
4. ``FLAG_ANCIENT_LIBRARY_COMPLETED`` – injects prophetic / heritage revelations.
5. ``FLAG_HERMITS_WARNING_COMPLETED`` – transitions to deeper forest access.
6. ``FLAG_NYX_TRIALS_COMPLETED`` – culmination of forest spiritual trials.

Dynamic Description:
- ``check_update`` composes layered narrative segments, dimming earlier stages
    while appending the newest active phase text for player clarity.

Completion Logic:
- Final resolution monitored through ``FLAG_GATHERING_STORM_COMPLETED`` (set
    externally once all act narrative beats resolve).
"""

from ...engine.Quest import Quest
from ...engine.GameState import GameState
from ..Act2StoryFlags import (
    FLAG_GATHERING_STORM_COMPLETED,
    FLAG_SPOKEN_TO_SIR_CEDRIC,
    FLAG_DEMONSTRATED_COMBAT_SKILLS,
    FLAG_SUPPLIES_QUEST_COMPLETED,
    FLAG_ANCIENT_LIBRARY_COMPLETED,
    FLAG_HERMITS_WARNING_COMPLETED,
    FLAG_NYX_TRIALS_COMPLETED,
)

class TheGatheringStormQuest(Quest):
    """Quest tracking the main narrative arc of Act II."""
    def __init__(self) -> None:
        super().__init__(
            name="The Gathering Storm",
            description=(
                "Having just arrived in the bustling city of Greendale, Elior senses an "
                "ominous presence growing in the shadows. Strange whispers speak of dark "
                "forces gathering strength, threatening the peace of both the city and "
                "the surrounding lands. To understand the true nature of this emerging "
                "threat and find a way to combat it, Elior must seek out Sir Cedric, the "
                "respected knight commander, who may hold crucial knowledge about the "
                "darkness that approaches."
            ),
        )
        self._flag_state = {}

    def is_main(self) -> bool:
        """This is the main quest for Act II."""
        return True

    def check_trigger(self, game_state: GameState) -> bool:
        return True  # This quest is always active once Act II begins

    def check_update(self, game_state: GameState) -> bool:
        updated = False
        self.description = ''
        new_desc = (
            "Having just arrived in the bustling city of Greendale, Elior senses an "
            "ominous presence growing in the shadows. Strange whispers speak of dark "
            "forces gathering strength, threatening the peace of both the city and "
            "the surrounding lands. To understand the true nature of this emerging "
            "threat and find a way to combat it, Elior must seek out Sir Cedric, the "
            "respected knight commander, who may hold crucial knowledge about the "
            "darkness that approaches."
        )
        if game_state.get_story_flag(FLAG_SPOKEN_TO_SIR_CEDRIC):
            if not self._flag_state.get(FLAG_SPOKEN_TO_SIR_CEDRIC):
                self._flag_state[FLAG_SPOKEN_TO_SIR_CEDRIC] = True
                updated = True
            self.description += '[dim]' + new_desc + '[/dim]'
            new_desc = (
                "\n\nSir Cedric has explained that dark forces are gathering and he needs "
                "allies with magical knowledge. "
            )
        if game_state.get_story_flag(FLAG_DEMONSTRATED_COMBAT_SKILLS):
            if not self._flag_state.get(FLAG_DEMONSTRATED_COMBAT_SKILLS):
                self._flag_state[FLAG_DEMONSTRATED_COMBAT_SKILLS] = True
                updated = True
            self.description += '[dim]' + new_desc + '[/dim]'
            new_desc = (
                "\n\nHaving proven your martial prowess with the training sword, you "
                "have earned Sir Cedric's trust in your combat abilities. This "
                "demonstration of skill has strengthened your position as a valuable "
                "ally in the fight against the growing darkness. Sir Cedric has "
                "revealed the true scope of the mission: you must journey into the "
                "enchanted forest to seek out the mystical being known as Nyx, who "
                "possesses ancient knowledge that could help combat the gathering "
                "shadows. Before attempting this dangerous quest, you need to gather "
                "essential supplies from the Market District: a forest survival kit, "
                "enhanced lantern, and quality rope. Time is of the essence, as the "
                "darkness grows stronger each day, and only Nyx's ancient wisdom may "
                "hold the key to understanding and defeating these otherworldly "
                "threats."
            )
        if game_state.get_story_flag(FLAG_SUPPLIES_QUEST_COMPLETED):
            if not self._flag_state.get(FLAG_SUPPLIES_QUEST_COMPLETED):
                self._flag_state[FLAG_SUPPLIES_QUEST_COMPLETED] = True
                updated = True
            self.description += '[dim]' + new_desc + '[/dim]'
            new_desc = (
                "\n\nWith all the essential supplies now gathered - the forest survival "
                "kit, enhanced lantern, and quality rope - you are properly equipped "
                "for the dangerous journey into the enchanted forest. The merchant's "
                "guidance and the quality of the equipment give you confidence that "
                "you can navigate the magical perils ahead. Now fully prepared, the "
                "path to finding Nyx and unlocking the ancient wisdom needed to "
                "combat the growing darkness lies before you. The forest awaits, and "
                "with it, the answers that could save both Greendale and the surrounding "
                "lands from the encroaching shadow."
            )
        if game_state.get_story_flag(FLAG_ANCIENT_LIBRARY_COMPLETED):
            if not self._flag_state.get(FLAG_ANCIENT_LIBRARY_COMPLETED):
                self._flag_state[FLAG_ANCIENT_LIBRARY_COMPLETED] = True
                updated = True
            self.description += '[dim]' + new_desc + '[/dim]'
            new_desc = (
                "\n\nThe ancient hidden library has revealed its secrets! Through the "
                "Spectral Librarian's guidance, you have uncovered crucial knowledge "
                "about your family heritage and learned the powerful dispel spell. "
                "The ancient prophecies speak of a Chosen One destined to face the "
                "returning darkness, and the revelation of your lineage suggests you "
                "may be central to this cosmic struggle. Armed with this newfound "
                "understanding of both your destiny and the magical arts, you now "
                "possess the knowledge and power needed to confront the gathering "
                "storm. The pieces of the puzzle are falling into place, and with "
                "each revelation, the path to finding Nyx and ultimately defeating "
                "the encroaching shadow becomes clearer."
            )

        if game_state.get_story_flag(FLAG_HERMITS_WARNING_COMPLETED):
            if not self._flag_state.get(FLAG_HERMITS_WARNING_COMPLETED):
                self._flag_state[FLAG_HERMITS_WARNING_COMPLETED] = True
                updated = True
            self.description += '[dim]' + new_desc + '[/dim]'
            new_desc = (
                "\n\nBy heeding the Hermit's warning and properly preparing with the "
                "survival kit, you have successfully navigated the threshold between "
                "the civilized world and the wild Enchanted Forest. The ancient "
                "protective runes have recognized your readiness, and the forest's "
                "guardians have granted you safe passage. With the hermit's blessing "
                "and proper preparation, you can now venture into the mystical realm "
                "where Nyx awaits. The path forward is clear, and the final phase of "
                "your quest to understand and combat the gathering darkness can begin."
            )

        if game_state.get_story_flag(FLAG_NYX_TRIALS_COMPLETED):
            if not self._flag_state.get(FLAG_NYX_TRIALS_COMPLETED):
                self._flag_state[FLAG_NYX_TRIALS_COMPLETED] = True
                updated = True
            self.description += '[dim]' + new_desc + '[/dim]'
            new_desc = (
                "\n\nThe trials are complete! You have successfully met with Nyx, the "
                "ancient forest sprite, and proven yourself worthy of her greatest "
                "gifts. Through your demonstration of wisdom, compassion, and "
                "courage throughout your journey, Nyx has blessed you with the "
                "sacred prophetic vision spell - the power to see glimpses of "
                "possible futures and understand the threads of fate. Along with "
                "this ultimate magical ability, you have received Nyx's Token as a "
                "symbol of your alliance with the forest spirits, and the Forest "
                "Heart Crystal containing the very essence of nature's power. With "
                "these powerful tools and newfound magical sight, you are now ready "
                "to face the gathering storm and protect both Greendale and the "
                "surrounding lands from the darkness that threatens to consume them "
                "all."
            )

        self.description += new_desc
        return updated

    def check_completion(self, game_state: GameState) -> bool:
        return game_state.get_story_flag(FLAG_GATHERING_STORM_COMPLETED)
