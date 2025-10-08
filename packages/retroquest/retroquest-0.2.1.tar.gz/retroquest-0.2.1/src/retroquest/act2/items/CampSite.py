"""CampSite: Abandoned rest node offering a single hidden item discovery."""

from ...engine.GameState import GameState
from ...engine.Item import Item

class CampSite(Item):  # pylint: disable=too-few-public-methods
    """Abandoned rest node offering single hidden item discovery (entry pass)."""

    def __init__(self) -> None:
        super().__init__(
            name="camp site",
            short_name="camp",
            description=(
                "A small clearing off the main path where travelers often rest. Signs "
                "of recent use remain—a fire pit with cold ashes and scattered "
                "belongings suggesting a hurried departure."
            ),
            can_be_carried=False,
        )
        self.examined = False

    def examine(self, game_state: GameState) -> str:  # type: ignore[override]
        if self.examined:
            return (
                "You've already thoroughly examined the camp site. There's nothing "
                "more to find here."
            )
        self.examined = True
        from .EntryPass import EntryPass
        entry_pass = EntryPass()
        game_state.current_room.add_item(entry_pass)
        return (
            "You carefully examine the abandoned camp site. Hidden under leaves near the "
            "fire pit you discover an [item_name]entry pass[/item_name] to Greendale — likely "
            "dropped by a prior traveler in haste.\n\n[event]You found an "
            "[item_name]entry pass[/item_name]![/event]"
        )

    def use(self, game_state: GameState) -> str:  # type: ignore[override]
        if not self.examined:
            return self.examine(game_state)
        return (
            "The camp site has been thoroughly examined. You could rest here if needed, "
            "but there's nothing more to discover."
        )
