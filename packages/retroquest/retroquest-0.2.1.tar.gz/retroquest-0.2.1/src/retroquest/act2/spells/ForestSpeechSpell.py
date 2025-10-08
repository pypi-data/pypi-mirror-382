"""ForestSpeechSpell: druidic spell to communicate with forest life and discover hooks."""

from typing import Any
from ...engine.Spell import Spell
from ..Act2StoryFlags import FLAG_FOUND_RAVINE
from ..items.Ravine import Ravine
from ...engine.GameState import GameState

class ForestSpeechSpell(Spell):
    """Druidic communication spell enabling dialogue with forest life and discovery hooks.

    Purpose:
        Facilitates environmental intelligence gathering and enables discovery of the
        Ravine (caravan hook) on first contextual use in the Forest Entrance.
    """

    def __init__(self) -> None:
        super().__init__(
            name="forest_speech",
            description=(
                "An ancient druidic spell that grants the ability to communicate with "
                "trees, plants, and forest creatures. This magic opens your mind to the "
                "slow, deep thoughts of ancient trees and the quick, bright chatter of "
                "woodland animals. Through this spell, you can seek guidance, learn "
                "forest secrets, and understand the hidden wisdom of the natural world."
            )
        )

    def cast_spell(self, game_state) -> str:
        """Cast the spell in the current room; handle ravine discovery and flavor text."""
        current_room = game_state.current_room
        # Special caravan search logic for Forest Entrance
        from ..rooms.ForestEntrance import ForestEntrance
        name = self.get_name()
        if isinstance(current_room, ForestEntrance) and not game_state.get_story_flag(
            FLAG_FOUND_RAVINE
        ):
            game_state.set_story_flag(FLAG_FOUND_RAVINE, True)
            # Add the Ravine item to the Forest Entrance room
            ravine = Ravine()
            current_room.items.append(ravine)
            return (
                f"[success]You cast [spell_name]{name}[/spell_name] and the woodland creatures "
                "gather around you excitedly. A family of squirrels chatters frantically about "
                "strange noises from the deep ravine to the northeast. An old owl hoots solemnly "
                "about 'metal beasts trapped in the earth-scar where the stone walls weep.' "
                "The animals describe a steep ravine hidden beyond the thickest part of the "
                "forest, where something seems to be moving. You should try to get down there."
                "[/success]"
            )
        # Check if caravan has already been found in Forest Entrance
        if isinstance(current_room, ForestEntrance) and game_state.get_story_flag(
            FLAG_FOUND_RAVINE
        ):
            return (
                f"[info]You cast [spell_name]{name}[/spell_name], but the woodland creatures "
                "have no new information about the ravine - you've already located it."
                "[/info]"
            )
        # Normal forest speech behavior for other locations
        room_name = current_room.name.lower()
        if "forest" in room_name or "grove" in room_name:
            return (
                f"[success]You cast [spell_name]{name}[/spell_name] and suddenly "
                "the forest comes alive with conversation. The trees whisper their ancient "
                "wisdom, sharing memories of seasons past and warnings of dangers ahead. "
                "Small woodland creatures emerge to share news of hidden paths and secret "
                "places. You feel deeply connected to the living tapestry of the forest."
                "[/success]"
            )
        elif "enchanted" in room_name:
            return (
                f"[success]You cast [spell_name]{name}[/spell_name] in this magical "
                "realm and the response is overwhelming. Every plant, from the mightiest "
                "tree to the smallest moss, has something to say. The magical nature of "
                "this place amplifies your connection, allowing you to understand even "
                "the most subtle communications from the natural world."
                "[/success]"
            )
        else:
            return (
                f"[info]You cast [spell_name]{name}[/spell_name], but there are "
                "few natural beings here to communicate with. You sense the faint whispers "
                "of any plants nearby, but the spell would be much more powerful in a "
                "forest or natural environment."
                "[/info]"
            )

    def cast_on_character(self, _game_state: GameState, target_character: Any) -> str:
        """Allow communication with forest creatures."""
        from ..characters.AncientTreeSpirit import AncientTreeSpirit
        from ..characters.ForestSprites import ForestSprites
        from ..characters.WaterNymphs import WaterNymphs
        tname = target_character.get_name()
        if isinstance(target_character, (AncientTreeSpirit, ForestSprites, WaterNymphs)):
            return (
                f"[success]You cast [spell_name]{self.get_name()}[/spell_name] on "
                f"[character_name]{tname}[/character_name], opening a channel of deep, "
                "mystical communication. Through the spell's magic, you can understand "
                "their ancient wisdom and forest secrets." "[/success]"
            )
        else:
            return (
                f"[info]You cast [spell_name]{self.get_name()}[/spell_name] on "
                f"[character_name]{tname}[/character_name], but this spell is designed for "
                "communication with forest beings and natural spirits. It has no effect "
                "on this character.[/info]"
            )
