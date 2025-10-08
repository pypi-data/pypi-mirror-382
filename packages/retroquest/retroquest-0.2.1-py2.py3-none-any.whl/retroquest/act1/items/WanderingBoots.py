"""Wandering boots item that aids in travel."""
from ...engine.Item import Item

class WanderingBoots(Item):
    """Wandering boots item that aids in travel."""
    def __init__(self) -> None:
        super().__init__(
            name="wandering boots",
            description="Sturdy leather boots, well-worn and comfortable. They seem to "
            + "hum with a faint energy, eager for the road.",
            short_name="boots",
            can_be_carried=True
        )
