"""Silver Stag Inn room for Act II."""

from ...engine.Room import Room
from ..characters.InnkeeperMarcus import InnkeeperMarcus
from ..characters.BarmaidElena import BarmaidElena
from ..items.RoomKey import RoomKey
from ..items.Door import Door

class SilverStagInn(Room):
    """Social nexus and information hub (Act II).

    Narrative Role:
        Central meeting place for gathering information, provisioning, and unlocking private inn
        rooms for rest or narrative beats.

    Key Mechanics:
        `use_key()` adds an east exit to the inn rooms exactly once.

    Story Flags:
        None currently; gating is via possessing and using the `RoomKey` item.

    Contents:
        Items: Room Key, Door (flavor). NPCs: Innkeeper Marcus, Barmaid Elena for service and lore.

    Design Notes:
        Exit mutation is isolated in a single method. If lockable exits spread, abstract to a mixin.
    """
    def __init__(self) -> None:
        super().__init__(
            name="The Silver Stag Inn",
            description=(
                "A three-story inn glows with warm yellow light. Conversations from travelers "
                "and locals merge into a comforting din while tales are traded over bread and "
                "ale. Stag mounts and adventuring trophies line the walls. The place feels "
                "welcoming; information flows here as freely as the drink."
            ),
            items=[RoomKey(), Door()],
            characters=[InnkeeperMarcus(), BarmaidElena()],
            exits={"south": "MarketDistrict"}
        )

    def use_key(self) -> str:
        """Handle use of the room key, unlocking the inn rooms if not already open."""
        if "east" not in self.exits:
            self.exits["east"] = "InnRooms"
            return (
                "[success]The key turns with a soft click, unlocking access to the private "
                "inn rooms upstairs. You can now 'go east' to enter them.[/success]"
            )
        else:
            return "[info]The inn rooms are already unlocked.[/info]"
