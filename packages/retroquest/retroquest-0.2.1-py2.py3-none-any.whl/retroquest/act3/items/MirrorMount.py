"""Mirror mount object representing an empty socket on the terraces.

This module provides the MirrorMount item used in Act 3. The mount can be
examined to reveal a hidden Brass Mirror Segment once, can accept segments
via use_with, and supports a mend operation to finalize repairs.
"""
from ...engine.Item import Item, GameState

class MirrorMount(Item):
    """A simple mount for holding a brass mirror segment."""

    def __init__(self) -> None:
        """Initialize an empty mirror mount."""
        super().__init__(
            name="Mirror Mount",
            description=(
                "A brass-and-stone mount fixed into the terrace socket. It needs a "
                "brass segment and binding resin to secure and repair the mirror face."
            ),
            short_name="mirror mount",
            can_be_carried=False,
        )
        self._installed = False
        # Track whether this mount has already revealed its hidden segment
        self._segment_revealed = False
        # Track whether binding resin has been applied after installation
        self._resin_applied = False

    def use_with(self, game_state: GameState, other_item: Item) -> str:
        """Allow use with a BrassMirrorSegment to install it into the mount.

        Requires the player to have four Brass Mirror Segments in inventory;
        consumes four and marks this mount as prepared.
        """
        from ..items.BrassMirrorSegment import BrassMirrorSegment
        from ..items.BindingResin import BindingResin

        # If the player uses binding resin on the mount, handle it here
        if isinstance(other_item, BindingResin):
            if not self._installed:
                return (
                    "[failure]There is nothing to bind yet — prepare the mount with "
                    "the mirror segments first.[/failure]"
                )
            if self._resin_applied:
                return "[info]Binding resin has already been applied to this mount.[/info]"
            # Remove one resin from inventory
            resin_name = BindingResin().get_name()
            game_state.remove_item_from_inventory(resin_name, 1)
            self._resin_applied = True
            return (
                "[success]You apply the binding resin carefully around the seams; "
                "the brass segments sit firmer and the joints set.[/success]"
            )

        if not isinstance(other_item, BrassMirrorSegment):
            return (
                f"[failure]You can't use the [item_name]{self.get_name()}[/item_name] with "
                f"the [item_name]{other_item.get_name()}[/item_name].[/failure]"
            )

        # Requirement: player must have at least 4 brass mirror segments total
        seg_name = BrassMirrorSegment().get_name()
        if game_state.get_item_count(seg_name) < 4:
            return (
                "[failure]You need more brass mirror segments in your pack before "
                "you can install them into the terrace mounts.[/failure]"
            )

        # Remove four segments from the player's inventory
        game_state.remove_item_from_inventory(seg_name, 4)

        # Mark this mount as installed; resin still needs to be applied before mend
        self._installed = True

        return (
            "[success]With a careful, ringing press you seat the brass segments and "
            "secure their alignment. The terrace mount accepts the fittings.[/success]"
        )

    def mend(self, game_state: GameState) -> str:
        """Finalize mirror repairs across the terraces and set completion flag.

        When called on a mount that is already installed, this will set the
        Mirrors of Emberlight completion flag so other systems can react.
        """
        from ..Act3StoryFlags import FLAG_ACT3_MIRRORS_OF_EMBER_LIGHT_COMPLETED

        if not self._installed:
            return (
                "[info]This mount has not yet been prepared with the brass segments; "
                "there is nothing to mend.[/info]"
            )

        # Require binding resin to have been applied before final mending
        if not self._resin_applied:
            return (
                "[info]The mirror segments are seated but still loose. You should "
                "apply Binding Resin to the mount before attempting the final mend.[/info]"
            )

        # Set the completion flag; idempotent
        game_state.set_story_flag(FLAG_ACT3_MIRRORS_OF_EMBER_LIGHT_COMPLETED, True)
        return (
            "[success]A whispered mend gathers in your hands and the mirrors "
            "answer — seams knit, polish brightens, and the whole face hums. "
            "When the sun's beams strike the great mirror they are coaxed and "
            "folded together until they pour from the terraces as a single, "
            "piercing ray. The light lances into the mountainside, strikes a "
            "hidden trigger, and a narrow passage grinds open to the east.[/success]"
        )

    def examine(self, game_state: GameState) -> str:
        """Examine the mount and reveal a brass segment hidden in the sand.

        The hidden segment is revealed once per mount and added to the current
        room's items so the player can retrieve it.
        """
        from ..items.BrassMirrorSegment import BrassMirrorSegment

        if self._segment_revealed:
            return super().examine(game_state)
        segment = BrassMirrorSegment()
        game_state.current_room.add_item(segment)
        self._segment_revealed = True
        return (
            "[event]You sift the ash and grit beneath the mount and find a "
            f"[item_name]{segment.get_name()}[/item_name]. It lies half-buried "
            "in the sand and has been added to the terrace.[/event]"
        )
