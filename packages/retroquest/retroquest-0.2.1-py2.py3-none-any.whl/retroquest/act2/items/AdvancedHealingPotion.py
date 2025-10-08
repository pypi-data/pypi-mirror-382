"""Advanced healing potion item: potent restorative future combat balancing hook."""

from ...engine.Item import Item


class AdvancedHealingPotion(Item):  # pylint: disable=too-few-public-methods
    """High-tier curative consumable placeholder."""

    def __init__(self) -> None:
        super().__init__(
            name="advanced healing potion",
            short_name="adv heal",
            description=(
                "A sealed crystal vial swirling with layered iridescent strata that pulse "
                "faintly when held. Even unopened it radiates clean restorative potential—"
                "clearly beyond a common herbal tincture."
            ),
            can_be_carried=True,
        )
