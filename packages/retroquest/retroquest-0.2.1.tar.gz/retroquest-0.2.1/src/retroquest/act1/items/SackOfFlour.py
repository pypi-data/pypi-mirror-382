"""SackOfFlour Item

Narrative Role:
Everyday provisioning good emphasizing agrarian economy and baking culture.
Potential quest delivery or ingredient.

Key Mechanics / Interactions:
- Heavy thematic item; currently portable without penalty (no encumbrance system yet).

Story Flags (Sets / Reads):
(none)

Progression Effects:
- Could support future baking/cooking mini-quest or trade barter.

Design Notes:
- Might later become non-portable until player acquires a cart or similar aid.

"""

from ...engine.Item import Item

class SackOfFlour(Item):
    """
    Everyday provisioning good emphasizing agrarian economy and baking culture.
    Potential quest delivery or ingredient.
    """

    def __init__(self) -> None:
        """Initialize the Sack of Flour item with name, description, and short name."""
        super().__init__(
            name="sack of flour",
            description=(
                "A heavy burlap sack filled with fine white flour. Essential for baking, but a "
                "bit unwieldy to carry."
            ),
            short_name="flour"
        )
