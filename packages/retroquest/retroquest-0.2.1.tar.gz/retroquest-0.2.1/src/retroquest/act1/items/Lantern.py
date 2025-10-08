"""Lantern Item

Narrative Role:
    Primary early-game light source revealing hidden items and reinforcing the concept that
    using an item can alter the environment (spawning new items).

Key Mechanics / Interactions:
    - First use transforms the item (renames to ``lantern (lit)``) and reveals ``Bread`` and
      ``EliorsJournal`` in the current room.
    - Subsequent uses report that it is already lit (idempotent state change).
    - Light emission abstracted; no ongoing fuel tracking.

Story Flags (Sets / Reads):
    (none) – environmental reveal handled directly; no global progression flags.

Progression Effects:
    - Teaches players that some items modify the room inventory, encouraging revisiting
      spaces with newly acquired tools.

Design Notes:
    - Uses name mutation plus ``short_name`` alignment to maintain consistent command targeting.
    - Future abstraction possible for broader light-producing item hierarchy.
"""

from ...engine.GameState import GameState
from ...engine.Item import Item

class Lantern(Item):
    """Primary early-game light source that reveals hidden items on first use.

    Behavior:
        - First activation renames the item to ``lantern (lit)`` while keeping ``short_name``
          stable for command resolution.
        - Spawns ``Bread`` and ``EliorsJournal`` into the current room (environment reveal
          pattern) and becomes idempotent afterward.
        - Subsequent uses simply report that it is already lit.

    Design Notes:
        Lightweight state tracking via name mutation avoids an extra boolean attribute.
        Future refactors could extract a shared ``LightSource`` mixin if more luminous items
        appear.
    """

    def __init__(self) -> None:
        super().__init__(
            name="lantern",
            description=(
                "A well-used brass lantern. Its glass is clean and the wick is fresh, ready to "
                "light up the darkest corners."
            ),
        )

    def use(self, game_state: GameState) -> str:
        """Light the lantern and reveal hidden items the first time it is used.

        On first activation:
            - Renames itself to ``lantern (lit)`` while keeping ``short_name`` stable.
            - Spawns ``Bread`` and ``EliorsJournal`` into the current room inventory.
        Subsequent uses simply report it is already lit.
        """
        action_taken_message = ""

        if self.name == "lantern":  # If it's not lit yet
            self.name = "lantern (lit)"
            self.short_name = "lantern"  # Update short_name as well
            from .Bread import Bread
            from .EliorsJournal import EliorsJournal
            game_state.current_room.add_item(Bread())
            game_state.current_room.add_item(EliorsJournal())
            action_taken_message = (
                f"[event]You light the [item_name]{self.get_name()}[/item_name]. The flickering "
                "light reveals more of the room. A small loaf of [item_name]bread[/item_name] "
                "and a [item_name]journal[/item_name] appear in the light.[/event]"
            )
        else:  # Already lit
            action_taken_message = (
                f"[failure]The [item_name]{self.get_name()}[/item_name] is already lit.[/failure]"
            )

        return action_taken_message
