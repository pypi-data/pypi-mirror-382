"""Mira character for Act I."""

from ...engine.Character import Character
from ...engine.Item import Item
from ..items.RareFlower import RareFlower
from ..items.AncientAmulet import AncientAmulet
from ..spells.HealSpell import HealSpell
from ..spells.UnlockSpell import UnlockSpell
from ..spells.LightSpell import LightSpell
from ...engine.GameState import GameState
from ..Act1StoryFlags import (
    FLAG_MAGIC_FULLY_UNLOCKED,
    FLAG_INVESTIGATED_WITHERED_CROPS,
    FLAG_VILLAGER_TALKED_TO,
    FLAG_WELL_EXAMINED,
    FLAG_CONNECT_WITH_NATURE,
)

class Mira(Character):
    """Village healer and wise woman who teaches spells and guides quests."""

    def __init__(self) -> None:
        super().__init__(
            name="Mira",
            description=(
                "The village healer and wise woman, Mira is known for her knowledge "
                "of herbs and magic. She guides Elior on his journey."
            ),
        )
        # Flag set when the rare flower is given to Mira
        self.quest_prepare_for_journey_given = False
        self.amulet_given = False

        self.dialogue_states = {
            "initial": (
                f"[character_name]{self.get_name()}[/character_name] smiles warmly as "
                f"you enter her fragrant hut. [dialogue]'Welcome, "
                f"[character_name]Elior[/character_name]. I sense a stirring of the "
                f"old powers within you. What brings you to my door?'" "[/dialogue]"
            ),
            "quest_conditions_not_met": (
                f"[character_name]{self.get_name()}[/character_name] looks at you "
                f"thoughtfully. [dialogue]'You have made progress, "
                f"[character_name]Elior[/character_name], but you are not yet fully "
                f"prepared for what lies ahead. Ensure you have all necessary items, "
                f"learned the essential spells, and received a blessing for your "
                f"journey.'[/dialogue]"
            ),
            "quest_complete_amulet_given": (
                f"[character_name]{self.get_name()}[/character_name] smiles, a deep "
                f"wisdom in her eyes. [dialogue]'You have done well, "
                f"[character_name]Elior[/character_name]. You have gathered your "
                f"supplies, honed your magical skills, and prepared your spirit. "
                f"You are ready.'[/dialogue] She presents you with the "
                f"[item_name]Ancient Amulet[/item_name]. [dialogue]'May this guide and "
                f"protect you.'[/dialogue] [event]([item_name]Ancient Amulet[/item_name] "
                f"added to inventory!)[/event]"
            ),
            "post_amulet": (
                f"[character_name]{self.get_name()}[/character_name] looks at you kindly. "
                f"[dialogue]'The journey of a thousand miles begins with a single step. You "
                f"have taken many already. Go now, and may your path be clear.'[/dialogue]"
            )
        }

    def give_item(self, game_state: GameState, item_object: Item) -> str:
        if isinstance(item_object, RareFlower):
            game_state.remove_item_from_inventory(item_object.get_name())

            spells_to_teach = [HealSpell(), UnlockSpell(), LightSpell()]
            for spell_instance in spells_to_teach:
                game_state.learn_spell(spell_instance)

            game_state.set_story_flag(FLAG_MAGIC_FULLY_UNLOCKED, True)

            # Combined dialogue for receiving flower, teaching spells, and giving quest.
            return (
                "[character_name]Mira[/character_name] smiles, accepting the "
                "[item_name]flower[/item_name]. [dialogue]'This bloom,' she says, her "
                "voice soft, 'is a testament to your growing bond with the living world, "
                "Elior. It shows you are ready to truly channel the energies around us.'"
                "[/dialogue] She then guides you through ancient words and gestures, "
                "awakening your innate abilities. [event]You feel a new understanding "
                "dawn as she imparts the knowledge of [spell_name]heal[/spell_name] to mend, "
                "[spell_name]unlock[/spell_name] to reveal, and [spell_name]light[/spell_name] to "
                "illuminate the path.[/event] [dialogue]'The spark was always within "
                "you,'[/dialogue] [character_name]Mira[/character_name] explains, "
                "[dialogue]'but now, you can truly command these magics.'[/dialogue] With "
                "your newfound power, she tasks you with preparing for the journey ahead, "
                "mentioning that the [item_name]Ancient Amulet[/item_name] will be yours once "
                "you are truly ready. She tells you that you will need:\n"
                "- Warm clothing\n"
                "- Magical protection\n"
                "- Food for the road\n"
                "- Sturdy footwear\n"
                "- A [item_name]map[/item_name] to find your way\n"
                "- To have learned all the basic magic the village elders can teach you.\n"
                "[dialogue]'Your journey will take you to Greendale,' she continues, her "
                "tone serious. 'There, you must seek out the old druid who dwells at the "
                "forest's edge. He alone can teach you the deeper mysteries of nature's magic "
                "and help you understand the darkness threatening Willowbrook. Trust in "
                "yourself, Elior, and remember: the fate of our village, or even more, may "
                "rest in your hands.'[/dialogue]"
            )
        return (
            "[character_name]Mira[/character_name] looks at the [item_name]"
            + item_object.get_name()
            + "[/item_name] but shakes her head gently. "
            + "[dialogue]'I have no need for this, child.'[/dialogue]"
        )

    def talk_to(self, game_state: GameState) -> str:
        event_msg = "[event]You speak with [character_name]Mira[/character_name].[/event]"
        # 1. Give the post_amulet message if amulet is in inventory
        if game_state.has_item("Ancient Amulet"):
            return event_msg + "\n" + self.dialogue_states["post_amulet"]

        # 2. Give the initial message if the story flag 'magic_fully_unlocked' is not set
        #    (i.e., flower hasn't been given yet)
        if not game_state.get_story_flag(FLAG_MAGIC_FULLY_UNLOCKED):
            # Check if all three story flags are set
            if (game_state.get_story_flag(FLAG_INVESTIGATED_WITHERED_CROPS)
                and game_state.get_story_flag(FLAG_VILLAGER_TALKED_TO)
                and game_state.get_story_flag(FLAG_WELL_EXAMINED)):
                game_state.set_story_flag(FLAG_CONNECT_WITH_NATURE, True)
                extra = (
                    "\n[dialogue]You describe to Mira the withered crops, the villagers' "
                    "fears, and the foul stench from the well. Her expression grows "
                    "troubled as she listens.[/dialogue] "
                    "[dialogue]'These are signs of a darkness that has long slumbered "
                    "beneath Willowbrook,'[/dialogue] she says sadly. "
                    "[dialogue]'The land is suffering, and so are its people. But there "
                    "is hope, Elior. You must connect with the living world—listen to "
                    "the wind, the water, the roots beneath your feet. Only by "
                    "understanding the magic of nature can you hope to confront what "
                    "is coming.'[/dialogue]"
                )
                return event_msg + "\n" + self.dialogue_states["initial"] + extra
            else:
                return event_msg + "\n" + self.dialogue_states["initial"]

        # 3. If 'magic_fully_unlocked' is set (flower given) and player doesn't have amulet:
        #    Quest is active or completable.
        if game_state.get_quest("Preparing for the Road").check_completion(game_state):
            # Conditions are fulfilled: give amulet and quest_complete_amulet_given message
            game_state.add_item_to_inventory(AncientAmulet())
            self.amulet_given = True
            return event_msg + "\n" + self.dialogue_states["quest_complete_amulet_given"]
        else:
            # Conditions not fulfilled: give quest_conditions_not_met message
            return event_msg + "\n" + self.dialogue_states["quest_conditions_not_met"]
