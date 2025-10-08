"""Merchant's Warehouse room for Act II."""

from ...engine.Room import Room

class MerchantsWarehouse(Room):
    """Storage adjunct supporting market scale (Act II).

    Narrative Role:
        Conveys logistical backbone behind the bustling market. Provides potential staging area for
        future supply chain, theft, or inventory audit quests.

    Key Mechanics:
        Currently static with no custom interactions.

    Story Flags:
        None yet; location is a candidate for smuggling or stock discrepancy flags later.

    Contents:
        Starts empty so quests can inject crates, ledgers, or guarded artifacts as needed.

    Design Notes:
        Kept intentionally lean to avoid refactors when narrative expansion arrives.
    """
    def __init__(self) -> None:
        super().__init__(
            name="Merchant's Warehouse",
            description=(
                "A large stone building packed with goods from distant lands. Crates and "
                "barrels form narrow corridors between tall shelving. Exotic spice and "
                "lacquer aromas mingle in the cool still air. This is where the most valuable "
                "inventory rests under quiet watch."
            ),
            items=[],
            characters=[],
            exits={"north": "MarketDistrict"}
        )
