"""Module defining the CavernMouth room in Act 3."""

from ...engine.Room import Room
from ..characters.MineOverseer import MineOverseer


class CavernMouth(Room):
    """The misty entrance to the ancient cavern system."""
    def __init__(self) -> None:
        """Initialize Cavern Mouth with description, Mine Overseer, and exits."""
        super().__init__(
            name="Cavern Mouth",
            description=(
                "A broad entry arch yawns before you, curtained by tendrils of cold mist "
                "that coil and writhe like spectral fingers. Lantern light wavers and dims "
                "at the threshold, as if the darkness within hungers to devour illumination. "
                "Ancient symbols are carved into the weathered stone archway, their meanings "
                "lost to time but somehow still resonating with a faint, otherworldly power. "
                "The air carries whispers of forgotten secrets and the weight of ages past."
            ),
            items=[],
            characters=[MineOverseer()],
            exits={"north": "ToolCache", "east": "StillnessVestibule"},
        )
