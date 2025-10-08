"""Egg Item

Narrative Role:
Simple agricultural product reinforcing life in the village and potential cooking/crafting systems.

Key Mechanics / Interactions:
- Fully portable; no current consumption or cooking logic.
- Flavor-only until kitchen, recipe, or trade mechanics emerge.

Story Flags (Sets / Reads):
(none) – Ordinary resource without progression tie.

Progression Effects:
- Adds ambient realism; minor future barter or ingredient potential.

Design Notes:
- Could later spoil over time or combine into crafted meals.

"""

from ...engine.Item import Item

class Egg(Item):
    """
    Simple agricultural product reinforcing life in the village and
    potential cooking/crafting systems.
    """

    def __init__(self) -> None:
        """Initialize the Egg item with name, description, and carry status."""
        super().__init__(
            name="egg",
            description="A freshly laid egg, still warm. It could be cooked or used in a recipe.",
            can_be_carried=True
        )
