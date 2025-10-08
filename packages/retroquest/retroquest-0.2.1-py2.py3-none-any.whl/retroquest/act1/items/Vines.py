"""Vines Item

Narrative Role:
Destructible environmental obstacle that converts into a resource (`Stick`)
when overcome, illustrating clearance + yield pattern.

Key Mechanics / Interactions:
- `use_with` + `SharpKnife` removes vines from room, consumes the knife, spawns a `Stick` item.
- Delegates fallback behavior to base for non-supported tools.

Story Flags (Sets / Reads):
(none) – Persistence handled by removing item from room.

Progression Effects:
- Teaches that environmental barriers can produce salvage materials.

Design Notes:
- Knife destruction adds cost weight to clearing; encourages timing choice.
- Could later variabilize outputs (multiple sticks, fiber) if crafting deepens.

"""

from ...engine.Item import Item
from .Stick import Stick

class Vines(Item):
    """
    Destructible environmental obstacle that converts into a resource (Stick) when overcome.
    """

    def __init__(self) -> None:
        """Initialize the Vines item with name and description."""
        super().__init__(
            name="vines",
            description="Thick, thorny vines block a small alcove.",
        )

    def use_with(self, game_state, other_item: Item) -> str:
        """Cut vines with SharpKnife, remove from room, spawn Stick, destroy knife."""
        from .SharpKnife import SharpKnife
        if isinstance(other_item, SharpKnife):
            game_state.current_room.remove_item(self.name)
            game_state.remove_item_from_inventory(other_item.get_name())
            game_state.current_room.add_item(Stick())
            return (
                f"[event]You use the [item_name]{other_item.get_name()}[/item_name] "
                f"to cut through the "
                f"thick [item_name]{self.get_name()}[/item_name], clearing the way "
                f"to a small alcove. "
                f"The [item_name]{other_item.get_name()}[/item_name] shatters from the "
                f"effort! You can see "
                f"a sturdy [item_name]stick[/item_name] in the revealed alcove.[/event]"
            )
        return super().use_with(game_state, other_item)
