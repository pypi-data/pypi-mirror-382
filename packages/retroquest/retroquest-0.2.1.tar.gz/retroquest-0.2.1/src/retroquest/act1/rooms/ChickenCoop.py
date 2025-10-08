"""Chicken Coop room: light agricultural ambience with small resource items."""

from ...engine.Room import Room
from ..items.Egg import Egg
from ..items.Feather import Feather
from ..items.Chicken import Chicken

class ChickenCoop(Room):
    """Light agricultural micro-location with passive collectible signals.

    Narrative Role:
        Introduces harmless creature presence and gentle resource flavor early.

    Key Mechanics:
        Static now; description seeds a hidden glint hook for future search or mini
        quest expansion.

    Story Flags:
        None currently.

    Contents:
        - Items: ``Chicken`` (ambient creature styled as item), ``Egg``, ``Feather``.
        - Characters: None.

    Design Notes:
        ``Chicken`` could migrate to a Character if behavior/emotion systems appear.
        Hidden hint supplies expandable narrative path (golden egg, lost trinket).
    """
    def __init__(self) -> None:
        super().__init__(
            name="Chicken Coop",
            description=(
                "A small wooden coop stands here, its planks patched and weathered. Nervous "
                "chickens cluck and flutter, their feathers ruffled as they dart between "
                "straw nests. The air is thick with the scent of hay and the occasional "
                "squawk. Sunbeams slip through the slats, casting striped shadows on the "
                "dirt floor. Something glints beneath the straw, hinting at a hidden secret."
            ),
            items=[Chicken(), Egg(), Feather()],
            characters=[],
            exits={"north": "VegetableField"}
        )
