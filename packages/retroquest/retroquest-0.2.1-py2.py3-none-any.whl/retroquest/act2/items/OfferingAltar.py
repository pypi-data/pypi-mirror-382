"""Offering Altar (Act II ritual object): used to summon Nyx with three sacred charms."""

from ...engine.Item import Item
from ..items.DruidicCharm import DruidicCharm
from ..items.ProtectiveCharm import ProtectiveCharm
from ..items.NaturesCharm import NaturesCharm
from ..characters.Nyx import Nyx
from ...engine.GameState import GameState

class OfferingAltar(Item):
    """An ancient starstone altar where the three sacred charms can be placed to summon Nyx."""

    def __init__(self) -> None:
        super().__init__(
            name="offering altar",
            description=(
                "An ancient altar carved from a single piece of starstone, its surface "
                "adorned with mystical runes that pulse with otherworldly light. Three "
                "circular indentations suggest that specific items are meant to be "
                "placed here in a sacred ritual. The altar radiates "
                "powerful magic and seems to be waiting for the proper offerings to activate its "
                "full potential."
            ),
        )

    def use_with(self, game_state: GameState, other_item) -> str:
        """Use the offering altar with one of the three sacred charms to summon Nyx."""
        # Check if the other item is one of the three sacred charms
        if not isinstance(other_item, (DruidicCharm, ProtectiveCharm, NaturesCharm)):
            return (
                f"The altar's runes remain dim. The {other_item.name} does not seem to be one of "
                "the sacred charms needed for this ancient ritual. You need the three blessed "
                "charms: Druidic Charm, Protective Charm, and Nature's Charm."
            )
        # Check if player has all three sacred charms
        has_druidic = any(isinstance(item, DruidicCharm) for item in game_state.inventory)
        has_protective = any(isinstance(item, ProtectiveCharm) for item in game_state.inventory)
        has_natures = any(isinstance(item, NaturesCharm) for item in game_state.inventory)
        if not (has_druidic and has_protective and has_natures):
            missing_charms = []
            if not has_druidic:
                missing_charms.append("Druidic Charm")
            if not has_protective:
                missing_charms.append("Protective Charm")
            if not has_natures:
                missing_charms.append("Nature's Charm")
            return (
                f"The altar's runes flicker weakly as you place the {other_item.name} upon it. "
                f"You sense that you need all three sacred charms to activate the full ritual: "
                f"{', '.join(missing_charms)}. The ancient magic requires all three offerings to "
                "complete the summoning."
            )
        # Player has all three charms - complete the ritual!
        # Remove all three charms from inventory
        items_to_remove = []
        for item in game_state.inventory:
            if isinstance(item, (DruidicCharm, ProtectiveCharm, NaturesCharm)):
                items_to_remove.append(item)
        for item in items_to_remove:
            game_state.inventory.remove(item)
        # Create and add Nyx to the current room if not already present
        nyx = Nyx()
        game_state.current_room.characters.append(nyx)
        summon_message = (
            "As the three sacred charms are placed upon the altar, the starstone erupts in "
            "brilliant light! The mystical runes blaze with ancient power, and the very air "
            "shimmers with magic. From the swirling energies, a figure of ethereal beauty "
            "materializes - Nyx, the ancient forest sprite, has answered the ritual's call!"
        )
        return f"[success]{summon_message}[/success]"
