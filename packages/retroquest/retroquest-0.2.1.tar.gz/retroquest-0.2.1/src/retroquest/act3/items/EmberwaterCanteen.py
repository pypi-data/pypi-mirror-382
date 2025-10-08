"""Emberwater Canteen item for Act 3."""

from typing import TYPE_CHECKING
from ...engine.Item import Item
from ...engine.GameState import GameState
if TYPE_CHECKING:
    from ...engine.Character import Character


class EmberwaterCanteen(Item):
    """A travel-worn canteen holding traces of past expeditions.

    Examining the canteen provides lore about previous climbers and may reveal
    a loose brass mirror segment tucked into its lining. The discovery is
    idempotent: once the segment is given it will not be duplicated.
    """

    def __init__(self) -> None:
        super().__init__(
            name="Emberwater Canteen",
            description=(
                "A dented canteen whose interior bears the faint smell of ash and "
                "old boiling herbs. A strip of brass peeks from a fold in the "
                "lining."
            ),
            short_name="Canteen",
            can_be_carried=True,
        )
        self._gave_segment = False

    def examine(self, game_state: GameState) -> str:
        """Examine the canteen; possibly give a Brass Mirror Segment.

        The first time the canteen is examined it yields a Brass Mirror Segment.
        This is tracked by an internal flag so the segment is only found once
        regardless of whether the player already holds a segment in inventory.
        """
        # Local import to avoid circular dependencies
        from .BrassMirrorSegment import BrassMirrorSegment
        lore = (
            "The canteen's lining is scorched and patched; someone once used it to "
            "carry boiled ash and broth between camps. A folded scrap of brass is "
            "stitched into the seam — a useful fragment for repairing a mirror."
        )
        if not self._gave_segment:
            segment = BrassMirrorSegment()
            # Place the segment into the current room so the player must take it
            # from the ground; do not add directly to inventory.
            game_state.current_room.items.append(segment)
            self._gave_segment = True
            return (
                f"[event]{lore} You pry free a [item_name]{segment.get_name()}"
                "[/item_name] from the lining; it falls to the ground nearby.[/event]"
            )

        return f"[event]{lore}[/event]"
