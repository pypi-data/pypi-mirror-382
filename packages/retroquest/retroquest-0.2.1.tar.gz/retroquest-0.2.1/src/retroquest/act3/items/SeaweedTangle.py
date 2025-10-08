"""A clump of seaweed clinging to stones; decorative, cannot be taken."""
from ...engine.Item import Item


class SeaweedTangle(Item):
    """A mat of salt-wet seaweed that clings to the shoreline; not carriable."""

    def __init__(self) -> None:
        """Initialize a Seaweed Tangle decorative item."""
        super().__init__(
            name="Seaweed Tangle",
            description=(
                "A dense mat of seaweed clings to the stones, slick and knotted. "
                "It seems rooted to the surf."
            ),
            short_name="seaweed",
            can_be_carried=False,
        )

    def prevent_pickup(self) -> str:
        """Explain why this cannot be picked up."""
        return (
            "[failure]The seaweed is wedged into crevices and heavy with salt; you "
            "can't pull it free.[/failure]"
        )
