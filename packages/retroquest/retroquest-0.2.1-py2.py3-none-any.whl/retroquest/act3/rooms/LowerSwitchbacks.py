"""Lower Switchbacks room for Act 3."""

from ...engine.Room import Room
from ..characters.AshScholar import AshScholar
from ..items import EmberwaterCanteen


class LowerSwitchbacks(Room):
    """Wind-carved paths zig-zagging across black rock with canvas shelters."""
    def __init__(self) -> None:
        """Initialize Lower Switchbacks with description and exits."""
        super().__init__(
            name="Lower Switchbacks",
            description=(
                "Wind‑carved paths snake across black, glassy rock; ash skims the "
                "air and the scent of iron hangs on the wind. A small scholars' "
                "camp clings to a lee: canvas shelters patched with soot, low "
                "braziers for warmth, and drying racks where scorched notes and "
                "map fragments flutter. Workbenches hold polishing stones and "
                "brass fittings—evidence of a diligent, makeshift atelier repairing "
                "mirror segments found among the outcrops. Beyond the camp, the "
                "slope falls into jagged obsidian ribs and steaming vents where "
                "fumaroles hiss; sparks drift like trapped fireflies when the wind "
                "turns."
            ),
            items=[EmberwaterCanteen()],
            characters=[AshScholar()],
            exits={"north": "ObsidianOutcrops", "east": "EmberGallery"},
        )
