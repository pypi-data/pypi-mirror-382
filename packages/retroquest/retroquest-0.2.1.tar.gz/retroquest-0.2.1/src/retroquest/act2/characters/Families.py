"""Families (Act II)

Role:
    Collective civilian NPC representing Greendale's intergenerational community. Serves
    as moral validation layer and conditional giver of HealingHerbs reward after the player
    demonstrates kindness via aiding elderly residents.

Gating Mechanics:
    - Dialogue friendly state requires FLAG_HELPED_ELDERLY_RESIDENTS == True (earned by giving
      a WalkingStick to assist mobility) OR triggering via give_item logic with that stick.

Story Flags:
    - Reads: FLAG_HELPED_ELDERLY_RESIDENTS
        - Sets: FLAG_HELPED_ELDERLY_RESIDENTS when WalkingStick is donated (acts as both action
            and attestation).

Rewards:
        - On first friendly conversation post-flag, grants HealingHerbs (single-use boon, supports
            parallel cure arc flavor).

Design Notes:
    - Internal boolean healing_herbs_given prevents duplication without extra story flag.
    - Uses defer-import for HealingHerbs to avoid unnecessary load costs if player never qualifies.
    - Encourages exploratory altruism prior to more heroic plot escalations.
"""

from ...engine.Character import Character
from ...engine.GameState import GameState
from ...engine.Item import Item
from ..Act2StoryFlags import FLAG_HELPED_ELDERLY_RESIDENTS
from ..items.WalkingStick import WalkingStick

class Families(Character):
    """Collective NPC representing local families; grants rewards for civic help."""
    def __init__(self) -> None:
        super().__init__(
            name="families",
            description=(
                "Friendly local families who have lived in Greendale for generations. They know "
                "the city's history and are happy to share stories with helpful visitors."
            ),
        )
        self.healing_herbs_given = False

    def talk_to(self, game_state: GameState) -> str:
        if not game_state.get_story_flag(FLAG_HELPED_ELDERLY_RESIDENTS):
            return (
                f"[failure]The [character_name]{self.get_name()}[/character_name] seem busy "
                "with their own affairs and no one seems to want to talk to you. They give "
                "you polite but distant nods, clearly not interested in conversation with a "
                "stranger.[/failure]"
            )

        response = (
            f"[character_name]{self.get_name()}[/character_name]: Welcome to our neighborhood! "
            "It's lovely to meet someone who takes time to help others. Greendale has a rich "
            "history - our families have been here for generations. The city has always been "
            "a place where those with good hearts and magical talents find a home. We're "
            "grateful for folks like you who lend a hand to those in need."
        )

        # Give healing herbs on first conversation after helping elderly residents
        if not self.healing_herbs_given:
            self.healing_herbs_given = True
            from ..items.HealingHerbs import HealingHerbs
            herbs = HealingHerbs()
            game_state.add_item_to_inventory(herbs)
            response += (
                "\n\n[event]An elderly woman from one of the families approaches you with a warm "
                "smile. 'Here, dear,' she says, pressing a bundle into your hands. 'These are "
                "rare healing herbs that have been in our family for generations. Someone who "
                f"helps others as you do should have them.' You receive "
                f"[item_name]{herbs.get_name()}[/item_name]![/event]"
            )

        return response

    def give_item(self, game_state: GameState, item_object: Item) -> str:
        """Handle giving items to the Families"""
        if isinstance(item_object, WalkingStick):
            # Remove the walking stick from inventory and help elderly residents
            game_state.remove_item_from_inventory(item_object.get_name())
            game_state.set_story_flag(FLAG_HELPED_ELDERLY_RESIDENTS, True)
            return (
                "[success]You use your walking stick to help several elderly residents "
                "navigate the uneven cobblestones and carry their heavy loads. Your "
                "assistance is greatly appreciated, and the community takes note of your "
                "kind and helpful nature. Word spreads that you are someone who cares "
                "about others.[/success]"
            )
        else:
            # For all other items, use the default behavior
            return super().give_item(game_state, item_object)
