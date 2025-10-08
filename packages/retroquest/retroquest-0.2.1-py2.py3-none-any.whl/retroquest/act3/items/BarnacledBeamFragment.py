"""A jutting fragment of beam encrusted with barnacles; decorative, cannot be taken."""
from ...engine.Item import Item


class BarnacledBeamFragment(Item):
    """A splintered beam piece encrusted with barnacles; not carriable."""

    def __init__(self) -> None:
        """Initialize a Barnacled Beam Fragment decorative item."""
        super().__init__(
            name="Barnacled Beam Fragment",
            description=(
                "A jagged remnant of timber studded with barnacles. It juts from the "
                "pier, more anchor than object."
            ),
            short_name="beam",
            can_be_carried=False,
        )

    def prevent_pickup(self) -> str:
        """Explain why the fragment cannot be taken."""
        return (
            "[failure]The beam is fused into the pier's wreckage; you cannot pry it free."
            "[/failure]"
        )
