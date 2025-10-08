"""Bush Item

Narrative Role:
Environment vegetation that can be magically stimulated to generate forage (wild berries),
demonstrating renewable resource mechanics gated by spell use.

Key Mechanics / Interactions:
- `grow` (triggered via spell externally) adds `WildBerries` if not already present in room.
- Idempotent production prevents duplication spam in single cycle.

Story Flags (Sets / Reads):
(none) – Room inventory presence provides implicit state.

Progression Effects:
- Introduces transformation of static environment into resource node via magic.

Design Notes:
- Could track depletion/regrowth timers if resource economy expands.

"""

from ...engine.Item import Item
from .WildBerries import WildBerries # Import WildBerries
from ...engine.GameState import GameState # Import GameState

class Bush(Item):
    """
    Environment vegetation that can be magically stimulated to generate forage (wild berries).
    """

    def __init__(self) -> None:
        """Initialize the Bush item with name, description, and carry status."""
        super().__init__(
            name="bush",
            description=(
                "A dense, leafy bush. It looks like it might be hiding something,"
                + " or just be a bush."
            ),
            short_name="bush",
            can_be_carried=False
        )

    def grow(self, game_state: GameState) -> str:
        """Cast grow spell to generate wild berries if not present."""
        current_room = game_state.current_room
        if not current_room.get_item_by_name("wild berries"):
            current_room.add_item(WildBerries())
            return (
                "[event]You cast the [spell_name]grow[/spell_name] spell on the "
                "[item_name]bush[/item_name]. It flourishes, and clusters of "
                "[item_name]wild berries[/item_name] appear among its leaves![/event]"
            )
        else:
            return (
                "[failure]The [item_name]bush[/item_name] is already full of "
                "[item_name]wild berries[/item_name].[/failure]"
            )
