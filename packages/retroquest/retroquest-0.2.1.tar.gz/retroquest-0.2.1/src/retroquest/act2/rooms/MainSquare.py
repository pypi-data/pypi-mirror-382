"""Main Square room for Act II."""

from ...engine.Room import Room
from ...engine.GameState import GameState
from ..items.CityNoticeBoard import CityNoticeBoard
from ..items.MerchantsFlyer import MerchantsFlyer
from ..characters.TownCrier import TownCrier

class MainSquare(Room):
    """Central urban hub in Greendale (Act II).

    Narrative Role:
        Establishes the scale of the city and provides the first impression of urban life.

    Key Mechanics:
        - Exits are gated until the player "uses" or otherwise activates the city map.
        - `enable_city_navigation()` flips an internal boolean allowing full movement.

    Story Flags:
        No global flag yet; uses local `city_map_used` (could later map to a story flag for saves).

    Contents:
        Items: notice board (lore hooks), merchant flyer (economy hint).
        NPC: Town Crier who can broadcast future quest beats.

    Design Notes:
        Gating encourages the player to orient themselves before free roaming. If additional
        settlements appear, consider abstracting map unlock logic to a reusable mixin.
    """
    def __init__(self) -> None:
        super().__init__(
            name="Main Square",
            description=(
                "The heart of Greendale pulses with activity. A grand fountain shows ancient "
                "heroes locked in battle with mythical beasts. Merchants hawk wares from "
                "bright stalls while townsfolk bustle about, exchanging news and gossip. Stone "
                "buildings with red roofs frame the space. Castle towers rise to the north, and "
                "the energetic flow of people makes it clear important things happen here."
            ),
            items=[CityNoticeBoard(), MerchantsFlyer()],
            characters=[TownCrier()],
            exits={"south": "GreendaleGates", "north": "CastleApproach", "east": "MarketDistrict"}
        )
        self.city_map_used = False

    def get_exits(self, _game_state: GameState) -> dict[str, str]:
        """Return exits, limiting movement until the city map has been used.

        Before the map is used only the south exit (back to the gates) is revealed. After map
        activation all declared exits become available.
        """
        if self.city_map_used:
            return self.exits
        else:
            return {"south": "GreendaleGates"}

    def enable_city_navigation(self) -> None:
        """Enable full exit set once the player has oriented using the city map."""
        self.city_map_used = True
