"""Blacksmith's Forge room: sensory craftsmanship hub placeholder for forging systems."""

from ...engine.Room import Room
from ..items.Horseshoe import Horseshoe
from ..characters.Blacksmith import Blacksmith

class BlacksmithsForge(Room):
    """Static crafting ambience node foreshadowing future equipment systems.

    Narrative Role:
        Establishes industrial heat/sound contrast versus quieter pastoral spaces and
        hints at later gear enhancement mechanics.

    Key Mechanics:
        Currently inert. Potential future: repair hooks, forging mini-game, upgrade
        services, or recipe discovery.

    Story Flags:
        None; progression neutral.

    Contents:
        - Item: ``Horseshoe`` (flavor / possible luck or crafting reagent).
        - NPC: ``Blacksmith`` (future gear interface candidate).

    Design Notes:
        If forging expands, introduce a ``ForgingStation`` item (encapsulating recipe
        validation, heat states, material slotting).
    """
    def __init__(self) -> None:
        super().__init__(
            name="Blacksmith's Forge",
            description=(
                "A hot, smoky forge glows with the light of burning coals. The clang of "
                "hammer on anvil echoes through the air, mingling with the scent of molten "
                "metal and sweat. Tools and half-finished weapons hang from the walls, and "
                "the blacksmith wipes his brow, his arms corded with muscle. Sparks dance "
                "in the gloom, and the heat is almost overwhelming."
            ),
            items=[Horseshoe()],
            characters=[Blacksmith()],
            exits={"west": "VillageWell", "north": "GeneralStore"}
        )
