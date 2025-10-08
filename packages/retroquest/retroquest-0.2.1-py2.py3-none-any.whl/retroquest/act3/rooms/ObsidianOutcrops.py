"""Module defining the ObsidianOutcrops room in Act 3."""
from ...engine.Room import Room
from ...engine.GameState import GameState
from ..items import BrassMirrorSegment, BindingResin


class ObsidianOutcrops(Room):
    """The Obsidian Outcrops: sharp volcanic glass formations."""
    def __init__(self) -> None:
        """Initialize Obsidian Outcrops with description and exits."""
        super().__init__(
            name="Obsidian Outcrops",
            description=(
                "Needle-sharp obsidian towers rise like black teeth from the ash, "
                "their surfaces catching and fracturing the light into jagged, "
                "glassy facets. Between the towers, thin seams and crevices hide "
                "weathered mirror fragments and the faint scars of old mounts—"
                "brass filings, dull polish, and tiny holes that speak of a long-"
                "vanished craft. A dry, metallic tang rides the hot wind, and "
                "every step sets off a tiny cascade of glass flakes into echoing "
                "gullies below."
            ),
            items=[],
            characters=[],
            exits={"south": "LowerSwitchbacks", "east": "MirrorTerraces"},
        )
        self._revealed = False

    def search(self, _game_state: GameState, _target: str = None) -> str:
        """Search the outcrops; reveal mirror segments and resin once."""
        if self._revealed:
            return (
                "[info]You pick through the crevices again; the scattered fragments are "
                "the same as before—nothing new comes loose.[/info]"
            )
        # Reveal a mirror segment and some resin
        self.items.append(BrassMirrorSegment())
        self.items.append(BindingResin())
        self._revealed = True
        return (
            "[event]You pry at a narrow seam and a brass segment flakes free, along with "
            "a hardened pot of binding resin—useful for securing the mirror mounts.[/event]"
        )
