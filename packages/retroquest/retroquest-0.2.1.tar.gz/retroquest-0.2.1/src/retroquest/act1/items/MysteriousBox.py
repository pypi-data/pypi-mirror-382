"""Small locked mysterious box that may contain a map for Act I."""

from ...engine.Item import Item
from ..items.Map import Map as GameMap
from ...engine.GameState import GameState


class MysteriousBox(Item):
    """Small locked container introducing multi-step acquisition and
    object state transitions.
    """

    def __init__(self) -> None:
        """Initialize the Mysterious Box item with name and description."""
        super().__init__(
            name="mysterious box",
            description=(
                "A small, ornate wooden box covered in strange runes. The lid is "
                "tightly shut, and it feels oddly heavy for its size. You sense "
                "something important is hidden inside."
            ),
            short_name="box",
        )
        self.locked = True
        self.contains_map = True

    def unlock(self, _game_state: 'GameState') -> str:
        """Unlock the box if locked, otherwise report already unlocked."""
        name_html = f"[item_name]{self.get_name()}[/item_name]"
        if self.locked:
            self.locked = False
            self.description = (
                f"A small, ornate wooden {name_html} covered in "
                "strange runes. The lock has clicked open."
            )
            event_msg = f"[event]You try to unlock the {name_html}.[/event]\n"
            return (
                event_msg
                + f"A soft click is heard from the {name_html} as the lock springs open!"
            )

        return f"[failure]The {name_html} is already unlocked.[/failure]"

    def open(self, game_state: 'GameState') -> str:
        """Open the box if unlocked and dispense the map, otherwise report locked or
        empty.
        """
        name_html = f"[item_name]{self.get_name()}[/item_name]"
        if self.locked:
            return (
                f"[failure]The {name_html} is locked. You need to find a way to open it."
                "[/failure]"
            )

        if self.contains_map:
            game_state.add_item_to_inventory(GameMap())
            self.contains_map = False
            self.description = "An open, ornate wooden box. It is now empty."
            return (
                f"[event]You open the {name_html}.[/event]\n"
                "Inside, you find a [item_name]map[/item_name]! You take the "
                "[item_name]map[/item_name] and place it in your inventory."
            )

        return f"[event]The {name_html} is now empty.[/event]"

    # The use_with method might be more complex depending on how spells are targeted.
    # For now, the UnlockSpell will call the .unlock() method directly if cast on this box.
