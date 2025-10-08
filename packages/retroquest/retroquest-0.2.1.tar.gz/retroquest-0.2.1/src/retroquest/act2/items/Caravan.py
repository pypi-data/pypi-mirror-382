"""Caravan item created after rescuing merchants from a ravine."""

from ...engine.Item import Item

class Caravan(Item):
    """A large rescued merchant caravan object; non-carriable but interactive."""
    def __init__(self) -> None:
        super().__init__(
            name="caravan",
            short_name="caravan",
            description=(
                "The rescued merchant caravan, battered but intact. Several merchants "
                "huddle around their damaged wagon, grateful to be alive. Their "
                "faces show relief mixed with exhaustion from their ordeal in the "
                "ravine. Crates of goods are scattered around, some damaged but "
                "most salvageable."
            ),
            can_be_carried=False,  # A caravan is too large to carry
        )

    def examine(self, _game_state) -> str:  # type: ignore[override]
        return (
            "The merchant caravan is in rough shape but the people are safe. The wagon's "
            "wheels are cracked and the canvas cover is torn, but the structure is "
            "sound. Several merchants tend to minor injuries while sorting through "
            "their goods. You see spice containers, bolts of fine cloth, and various "
            "trade items. The merchants look at you with deep gratitude—you clearly "
            "saved their lives."
        )
