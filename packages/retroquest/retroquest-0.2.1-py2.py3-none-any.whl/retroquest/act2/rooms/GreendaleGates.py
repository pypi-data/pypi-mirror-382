"""Greendale Gates room: formal entry gate with etiquette-based search unlock."""

from ...engine.Room import Room
from ...engine.GameState import GameState
from ..characters.GateCaptain import GateCaptain
from ..items.CityMap import CityMap

class GreendaleGates(Room):
    """Urban threshold enforcing protocol and staged discovery.

    Narrative Role:
        Shifts player from wilderness traversal to a structured civic space. It also
        introduces formal access control and etiquette required to progress.

    Key Mechanics:
        - ``get_exits()`` withholds ``north`` until the gate captain grants entry.
        - ``search()`` is blocked while the captain remains; the first permissive
          search spawns a ``CityMap`` (idempotent via a local boolean).

    Story Flags:
        - None; this room currently relies on the NPC attribute
          ``entry_pass_given`` rather than global story flags.

    Contents:
        - NPC: ``GateCaptain``.
        - Conditional Item: ``CityMap``.

    Design Notes:
        Local state keeps transient discovery scoped. Elevate to a story flag if
        later cross-room logic requires explicit map ownership checks.
    """

    def __init__(self) -> None:
        """Initialize gates with gate captain and gated northern exit."""
        gate_captain = GateCaptain()
        super().__init__(
            name="Greendale Gates",
            description=(
                "A magnificent stone archway marks the entrance to Greendale, the largest "
                "settlement you have encountered. Guards in polished mail stand watch, banners "
                "fluttering in the mountain breeze. Beyond, cobblestone streets wind between "
                "stone houses and bustling shops. The air carries the sounds of commerce—a "
                "stark contrast to Willowbrook's quiet charm."
            ),
            items=[],
            characters=[gate_captain],
            exits={"south": "MountainPath", "north": "MainSquare"},
            # Include north exit in the static definition above
        )
        self.gate_captain = gate_captain
        self.city_map_found = False

    def get_exits(self, game_state: GameState) -> dict:
        """Return exits; hide north until entry granted by gate captain.

        Parameters:
            game_state: Unused; maintained for interface consistency.

        Returns:
            Mapping of exits including ``south`` and conditionally ``north``.
        """
        exits = super().get_exits(game_state).copy()
        # Remove north exit until the entry pass has been given
        if not self.gate_captain.entry_pass_given and "north" in exits:
            del exits["north"]
        return exits

    def search(self, _game_state: GameState, _target: str = None) -> str:
        """Search area; map appears only after protocol and first search.

        Parameters:
            game_state: Unused here beyond interface uniformity.
            _target: Ignored placeholder for future targeted search.

        Returns:
            Narrative feedback string reflecting etiquette gating or discovery.
        """
        if self.gate_captain in self.characters:
            return (
                "The Gate Captain stands vigilant, watching all who approach. It would be "
                "improper to search while he observes you so closely. Perhaps speak with him "
                "first."
            )
        if self.city_map_found:
            return "You've already searched thoroughly. Nothing more of value stands out here."
        self.city_map_found = True
        city_map = CityMap()
        self.add_item(city_map)
        name = city_map.get_name()
        return (
            "With the Gate Captain gone, you're free to look around. A small information post "
            "nearby holds items left by travelers. Among them you discover a detailed "
            f"[item_name]{name}[/item_name] of Greendale—exactly what you need to navigate the "
            "city's winding streets!"
        )
