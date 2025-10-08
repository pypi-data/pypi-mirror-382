"""Tool Cache room for Act 3."""


from ...engine.Room import Room
from ..items.SupplyCrate import SupplyCrate



class ToolCache(Room):
    """A reinforced alcove with a locked supply crate for the miners' rescue."""
    def __init__(self) -> None:
        """Initialize Tool Cache with supply crate and exits."""
        self.crate_discovered = False
        super().__init__(
            name="Tool Cache",
            description=(
                "A reinforced alcove carved from living stone, where shadows pool between "
                "weathered crates of timbers, iron braces, and coils of hemp rope. The air "
                "tastes of old metal and earth, heavy with the weight of countless mining "
                "expeditions. Ancient tool marks score the walls, and you sense the "
                "presence of those who labored here in ages past. The flickering torchlight "
                "reveals corners shrouded in darkness."
            ),
            items=[],
            characters=[],
            exits={"south": "CavernMouth", "east": "CollapsedGalleries"},
        )

    def search(self, _game_state, _target: str = None) -> str:
        """Describe the supply crate and hint at its importance."""
        # Check if the supply crate has already been discovered
        if self.crate_discovered:
            return (
                "You've already found the heavy supply crate, locked with its large iron "
                "padlock. The label still reads: 'Rescue Supplies — For Emergency Use Only.'"
            )
        # First time searching - reveal the supply crate
        self.crate_discovered = True
        supply_crate = SupplyCrate()
        self.add_item(supply_crate)
        return (
            "You search deeper into the shadowed alcove and discover a heavy supply crate "
            "hidden behind stacked timbers, locked with a large iron padlock that glints "
            "with an almost malevolent gleam. The label reads: 'Rescue Supplies — For "
            "Emergency Use Only.' If you had the right key, you could unlock it and retrieve "
            "the tools needed to help the trapped miners."
        )
