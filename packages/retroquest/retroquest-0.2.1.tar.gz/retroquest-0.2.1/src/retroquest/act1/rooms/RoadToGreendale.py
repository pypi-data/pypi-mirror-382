"""Road to Greendale room: outbound transition toward broader world scope."""

from ...engine.Room import Room
from ..items.RustySaw import RustySaw
from ..characters.Merchant import Merchant

class RoadToGreendale(Room):
    """Transitional route signaling expansion beyond village confines.

    Narrative Role:
        Frames departure tone and allows light provisioning via ambient merchant.

    Key Mechanics:
        Simple exit topology; staging for future encounter gating or travel events.

    Story Flags:
        None currently.

    Contents:
        - Item: ``RustySaw``.
        - NPC: ``Merchant``.

    Design Notes:
        Could introduce conditional unlocking tied to core village quest completion.
    """
    def __init__(self) -> None:
        """Initialize the Road to Greendale with its item and traveling merchant NPC."""
        super().__init__(
            name="Road to Greendale",
            description=(
                "The main road leaving Willowbrook stretches beneath ancient oaks, their "
                "branches arching overhead like a living tunnel. The path is well-trodden, "
                "lined with wildflowers and scattered leaves. A merchant's cart creaks nearby, "
                "and the air is filled with the promise of adventure and the unknown. The road "
                "beckons, leading onward to new lands and new stories."
            ),
            items=[RustySaw()],
            characters=[Merchant()],
            exits={"west": "VillageChapel"}
        )
