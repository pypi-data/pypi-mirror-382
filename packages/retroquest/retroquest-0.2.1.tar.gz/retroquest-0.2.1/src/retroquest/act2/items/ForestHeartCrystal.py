"""ForestHeartCrystal: High-tier natural magic artifact from the Enchanted Forest."""

from ...engine.Item import Item

class ForestHeartCrystal(Item):
    """A powerful crystal embodying the living essence of the enchanted forest."""
    def __init__(self) -> None:
        super().__init__(
            name="forest heart crystal",
            description=(
                "A magnificent crystal that seems to contain an entire living forest within its "
                "translucent depths. Tiny lights dance inside like fireflies, and you can almost "
                "hear the whisper of wind through leaves when you hold it close. This crystal "
                "radiates immense magical power and represents the concentrated essence of all "
                "natural magic."
            ),
        )
