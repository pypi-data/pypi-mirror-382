"""Sir Cedric NPC for Act II."""

from ...engine.Character import Character
from ...engine.GameState import GameState
from ..items.Coins import Coins
from ..items.NaturesCharm import NaturesCharm
from ..Act2StoryFlags import (
    FLAG_SPOKEN_TO_SIR_CEDRIC,
    FLAG_CEDRIKS_HONOR_COMPLETED,
    FLAG_NYX_TRIALS_COMPLETED,
)

class SirCedric(Character):
    """Noble knight who recruits allies and awards honor-based quests."""
    def __init__(self) -> None:
        super().__init__(
            name="sir cedric",
            description=(
                "A noble knight in gleaming armor, bearing the scars of many battles. "
                "His eyes hold wisdom and determination as he prepares for the "
                "challenges ahead."
            ),
        )
        self.received_natures_charm = False
        self.cedric_trusts_elior = False

    def talk_to(self, game_state: GameState) -> str:
        # Check if Nyx trials are completed - highest priority response
        if game_state.get_story_flag(FLAG_NYX_TRIALS_COMPLETED):
            return (
                "[character_name]Sir Cedric[/character_name]: My friend, I sense something "
                "extraordinary has happened."
                " You carry an aura of ancient magic, and your eyes hold depths I had "
                "not seen before."
                " Have you succeeded in your quest to find Nyx?"
                " The prophetic vision spell you learned is the sort of mystical "
                "knowledge we need."
                " With your ability to glimpse possible futures, we can better "
                "anticipate threats and develop strategies to counter them."
                " You have become a formidable ally in our fight against the "
                "darkness."
            )

        if (
            game_state.get_story_flag(FLAG_CEDRIKS_HONOR_COMPLETED)
            and not self.received_natures_charm
        ):
            # Honor has been restored, give Nature's Charm
            self.received_natures_charm = True
            charm = NaturesCharm()
            game_state.inventory.append(charm)

            return (
                "[character_name]Sir Cedric[/character_name]: My friend, I cannot express "
                "how grateful I am."
                " You have restored my honor and cleared my name of those terrible "
                "accusations."
                " The weight I carried for so long has been lifted from my shoulders."
                "\n\n*Sir Cedric reaches into his pack and withdraws an ancient wooden charm*"
                "\n\nPlease accept this Nature's Charm. It has been in my family for "
                "generations, blessed by the ancient knights who first made pacts "
                "with the forest spirits."
                " The old texts say this is one of three sacred charms needed to summon "
                "Nyx."
                " You have proven yourself a true friend, and I believe you will need "
                "this for the greater challenges ahead."
            )

        if game_state.get_story_flag(FLAG_CEDRIKS_HONOR_COMPLETED):
            return (
                "[character_name]Sir Cedric[/character_name]: Thanks to your efforts, my "
                "honor has been restored and the false accusations cleared from my record."
                " I stand ready to face the challenges ahead with renewed purpose and "
                "dignity."
            )

        if not game_state.get_story_flag(FLAG_SPOKEN_TO_SIR_CEDRIC):
            # First meeting - explain the main quest and give knight's test
            game_state.set_story_flag(FLAG_SPOKEN_TO_SIR_CEDRIC, True)
            return (
                "[character_name]Sir Cedric[/character_name]: Greetings, traveler. I am "
                "[character_name]Sir Cedric[/character_name]. I have been seeking "
                "individuals of courage and skill for a matter of great importance."
                " Dark forces are gathering; I call it the 'Gathering Storm', and I need "
                "allies with magical knowledge and proven abilities."
                " Before I can trust you with this responsibility, I need proof of your "
                "combat skills. Can you demonstrate your martial abilities?"
            )
        elif game_state.is_quest_completed("The Knight's Test") and not self.cedric_trusts_elior:
            self.cedric_trusts_elior = True

            # Give Elior 100 individual coins using the new batching system
            coin = Coins(1)  # Create a single coin worth 1 gold
            game_state.add_item_to_inventory(coin, count=100)  # Add 100 of them

            return (
                "[character_name]Sir Cedric[/character_name]: Excellent demonstration! Your "
                "combat skills are impressive. I can see you have the training and discipline "
                "needed for the challenges ahead.\n\n*Sir Cedric reaches into his pouch and "
                "hands you a bag of coins*\n\nPlease accept these 100 gold coins. I should have "
                "provided them earlier for your supply purchasing. You'll need proper equipment "
                "for the forest expedition: a survival kit, an enhanced lantern, and quality "
                "rope from the Market District."
                " The realm faces a great threat, and we must be prepared."
            )
        elif self.cedric_trusts_elior:
            return (
                "[character_name]Sir Cedric[/character_name]: How goes your preparation?"
                " The gathering storm grows stronger each day. I trust you are making "
                "good progress in gathering allies and supplies."
            )
        else:
            return (
                "[character_name]Sir Cedric[/character_name]: I await your demonstration of "
                "combat skills before we can proceed with more serious matters."
            )
