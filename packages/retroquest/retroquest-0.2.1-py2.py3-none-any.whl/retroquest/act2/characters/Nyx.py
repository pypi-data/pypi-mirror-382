"""Nyx NPC: forest guardian and reward-giver in Act II."""

from ...engine.Character import Character
from ..items.NyxToken import NyxToken
from ..items.ForestHeartCrystal import ForestHeartCrystal
from ..spells.PropheticVision import PropheticVision
from ..Act2StoryFlags import FLAG_NYX_TRIALS_COMPLETED
from ...engine.GameState import GameState

class Nyx(Character):
    """The ancient forest sprite who guards the deepest secrets of nature."""

    def __init__(self) -> None:
        super().__init__(
            name="nyx",
            description=(
                "An ethereal being of impossible beauty, with skin like moonlight and hair "
                "that shimmers with the colors of autumn leaves. Her eyes hold the wisdom "
                "of millennia, and when she moves, flowers bloom in her footsteps. She "
                "radiates an aura of ancient magic and natural power."
            ),
        )

    def talk_to(self, game_state: GameState) -> str:
        """Return dialogue for Nyx and grant rewards on first meeting."""
        # Check if this is the first time talking to Nyx
        if not game_state.get_story_flag(FLAG_NYX_TRIALS_COMPLETED):
            # First meeting - grant all rewards immediately
            game_state.set_story_flag(FLAG_NYX_TRIALS_COMPLETED, True)
            # Add Prophetic Vision spell
            prophetic_vision = PropheticVision()
            game_state.known_spells.append(prophetic_vision)
            # Add Nyx's Token and Forest Heart Crystal
            nyx_token = NyxToken()
            forest_crystal = ForestHeartCrystal()
            game_state.inventory.extend([nyx_token, forest_crystal])
            msg = (
                "[success]Nyx regards you with ancient eyes that hold the wisdom of millennia.\n\n"
                "\"Brave Elior, your journey through the forest and your respect for all "
                "living things has proven your worth. I have watched as you helped the "
                "healers, protected the innocent, and showed wisdom in your choices. For "
                "this, I grant you my greatest gifts.\"\n\n"

                "She raises her hands, and magical energy flows into you like gentle "
                "starlight. You feel new knowledge settling into your mind - the gift "
                "of prophetic vision, allowing you to glimpse the threads of fate. "
                "Nyx then places two precious items in your hands.\n\n"

                "[item_gained]You have learned the spell: Prophetic Vision[/item_gained]\n"
                "[item_gained]You have received: Nyx's Token[/item_gained]\n"
                "[item_gained]You have received: Forest Heart Crystal[/item_gained]\n\n"
                "\"Use these gifts wisely, young one. The prophetic vision will help you "
                "prepare for the gathering storm that approaches. May the forest's blessing "
                "guide you on your path.\""
            )
            return msg + "[/success]"
        else:
            # Subsequent meetings - just wish good luck
            followup = (
                "Nyx smiles with ethereal grace, her form shimmering like moonlight "
                "through leaves.\n\n"
                "\"Go well, Elior. The forest's blessing travels with you, and the gifts "
                "I have given will serve you in the trials ahead. Trust in your wisdom, "
                "courage, and compassion - they will light your way through the darkness "
                "that gathers. May fortune favor your quest.\""
            )
            return followup
