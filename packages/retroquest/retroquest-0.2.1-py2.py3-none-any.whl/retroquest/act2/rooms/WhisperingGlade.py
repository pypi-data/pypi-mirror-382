"""Whispering Glade room for Act II."""

from ...engine.Room import Room

class WhisperingGlade(Room):
    """Tranquil forest clearing with latent lore potential (Act II).

    Narrative Role:
        Provides a quiet tonal contrast to denser forest areas and a future anchor
        for nature, riddle, or restorative interactions.

    Current Mechanics:
        Pass-through location reached after prerequisite flags at Forest Entrance; presently no
        interactive items or characters.

    Planned Features:
        Potential water nymph riddle system, restorative buffs, or nature-aligned spell unlocks.

    Design Notes:
        Minimal implementation keeps the space flexible. When adding riddles, standardize an
        'answer <text>' verb across puzzle rooms.
    """
    def __init__(self) -> None:
        super().__init__(
            name="Whispering Glade",
            description=(
                "A peaceful meadow opens around a small stream that babbles over smooth stones. "
                "Wildflowers blanket the ground and butterflies drift through warm sunlight. The "
                "water's murmur soothes, yet faint voices ride the breeze — whispers hinting at "
                "ancient secrets. Near the crystal stream you sense watchful, unseen guardians."
            ),
            items=[],
            characters=[],
            exits={"west": "ForestEntrance"}
        )
        # Future expansion: riddle handling / water nymph interaction placeholder.
