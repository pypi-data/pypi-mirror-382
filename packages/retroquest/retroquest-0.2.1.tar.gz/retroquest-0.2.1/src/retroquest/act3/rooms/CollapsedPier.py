"""Module defining the CollapsedPier room in Act 3."""
from ...engine.Room import Room
from ..items import Locker, WeatheredCoin
from ..characters.PierWarden import PierWarden


class CollapsedPier(Room):
    """A broken jetty where the sea keeps its older promises in shadow."""
    def __init__(self) -> None:
        """Initialize Collapsed Pier with locker and exits."""
        super().__init__(
            name="Collapsed Pier",
            description=(
                "The pier surrenders to the tide. Warped planks gape and blackened "
                "vaults yawn where light forgets to go. Barnacled timbers rise like "
                "buried ribs, and the water sings a low, patient counting of losses."
            ),
            items=[Locker(), WeatheredCoin()],
            characters=[PierWarden()],
            exits={"west": "OuterWards"},
        )
