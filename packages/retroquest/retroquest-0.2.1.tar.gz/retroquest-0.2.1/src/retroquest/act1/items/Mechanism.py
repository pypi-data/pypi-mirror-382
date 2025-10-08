"""Mechanism item for the mill repair puzzle."""

from ...engine.GameState import GameState
from ...engine.Item import Item
from .MillstoneFragment import MillstoneFragment
from .Rope import Rope

class Mechanism(Item):
    """
    Central repair puzzle object in the mill context.
    """

    def __init__(self) -> None:
        """Initialize the Mechanism item with name, description, and repaired state."""
        super().__init__(
            name="strange mechanism",
            short_name="mechanism",
            description=(
                "A strange mechanism with levers and gears that doesn't quite seem to "
                "belong to the old mill's original design. It looks like something could be "
                "used with it."
            ),
            can_be_carried=False,
        )
        self.repaired = False

    def examine(self, game_state: 'GameState') -> str:
        """Return description based on repaired state."""
        name_html = f"[item_name]{self.get_name()}[/item_name]"
        if self.repaired:
            self.description = (
                f"The {name_html} has been repaired using a "
                "[item_name]rope[/item_name]. A compartment is open."
            )
        else:
            self.description = (
                "A strange mechanism with levers and gears that doesn't quite seem to "
                "belong to the old mill's original design. It looks like something could be "
                "used with it."
            )
        return super().examine(game_state)

    def use(self, _game_state: 'GameState') -> str:
        """Operate the mechanism if repaired, otherwise prompt for repair."""
        name_html = f"[item_name]{self.get_name()}[/item_name]"
        if self.repaired:
            return (
                "[failure]The "
                + name_html
                + " has already been operated.[/failure]"
            )
        return (
            "[failure]It looks like you need to use something with the "
            + name_html
            + "[/item_name].[/failure]"
        )

    def use_with(self, game_state: 'GameState', other_item: Item) -> str:
        """Repair with Rope, spawn MillstoneFragment, or fallback."""
        if isinstance(other_item, Rope):
            if self.repaired:
                return (
                    f"[failure]The [item_name]{self.get_name()}[/item_name] has already been "
                    "operated.[/failure]"
                )
            self.repaired = True
            if other_item in game_state.inventory:
                game_state.inventory.remove(other_item)
            millstone_fragment = MillstoneFragment()
            game_state.current_room.add_item(millstone_fragment)
            self.description = (
                "The mechanism has been repaired using a rope. A compartment is open."
            )
            name_html = f"[item_name]{self.get_name()}[/item_name]"
            event_msg = (
                "[event]You try to use the [item_name]rope[/item_name] with the "
                + name_html
                + "[/event]\n"
            )
            part1 = (
                "You manage to thread the [item_name]rope[/item_name] through the "
                + name_html
                + ". "
            )
            part2 = (
                "With a clunk, a hidden compartment slides open, "
                "revealing a fragment of the old millstone!"
            )
            return event_msg + part1 + part2
        else:
            return super().use_with(game_state, other_item)

    def listen(self, _game_state: 'GameState') -> str:
        """Return sound feedback based on repaired state."""
        name_html = f"[item_name]{self.get_name()}[/item_name]"
        event_msg = "[event]You listen to the " + name_html + "[/event]\n"
        if self.repaired:
            return event_msg + ("The " + name_html + " is silent now, its purpose served.")
        return (
            event_msg
            + (
                "You hear a faint whirring and clicking from within the "
                + name_html
                + ", as if it's waiting for something."
            )
        )
