"""Phoenix Feather: a relic of wisdom, warm as a heartbeat."""
from ...engine.Item import Item

class PhoenixFeather(Item):
    """A single feather from the Phoenix, glowing with inner warmth."""
    def __init__(self) -> None:
        super().__init__(
            name="Phoenix Feather",
            description=(
                "A single feather shed by the Phoenix, warm as a heartbeat and shimmering with "
                "crimson and gold. It hums faintly in your hand, as if containing a spark of "
                "ancient wisdom."
            ),
        )
