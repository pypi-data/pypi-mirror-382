"""Module defining the SanctumOfTheTide room and its characters in Act 3."""
from ...engine.Room import Room
from ..items import CrystalOfLight
from ..characters.TideBornGuardian import TideBornGuardian

class SanctumOfTheTide(Room):
    """A domed chamber where water stands glass-still with rippling sigils."""

    def __init__(self) -> None:
        """Initialize Sanctum of the Tide with crystal, guardian, and exits."""
        super().__init__(
            name="Sanctum of the Tide",
            description=(
                "A vaulted chamber where water hangs like a dark mirror, its surface "
                "etched with sigils that breathe and shift. Pale motes of light drift "
                "along the ripples, arranging themselves into slow, impatient runes. "
                "At the room's heart a shallow basin holds a cold, humming brightness; "
                "the air tastes of brine and vows left unsaid."
            ),
            items=[CrystalOfLight()],
            characters=[TideBornGuardian()],
            exits={"west": "SubmergedAntechamber"},
        )
