"""Well item: a multi-step environmental puzzle object in Act I."""

from ...engine.GameState import GameState
from ...engine.Item import Item
from ..Act1StoryFlags import FLAG_WELL_EXAMINED

class Well(Item):
    """Central multi-phase environmental puzzle object used for layered interactions."""

    def __init__(self) -> None:
        """Initialize the Well item with name, description, and state flags."""
        super().__init__(
            name="well",
            description=(
                "An old stone well, its surface worn smooth. A frayed rope hangs nearby, "
                "disappearing into the depths."
            ),
        )
        self.contains_ring = True
        self.is_purified = False

    def examine(self, game_state: GameState) -> str:
        """Examine the well, update flags, and adjust description based on state."""
        game_state.set_story_flag(FLAG_WELL_EXAMINED, True)
        base_desc = (
            "An old stone well, its surface worn smooth. A frayed rope hangs nearby, "
            "disappearing into the depths."
        )
        if self.is_purified:
            if self.contains_ring:
                self.description = (
                    base_desc
                    + (
                        " The water within is crystal clear. You can see something shiny "
                        "at the bottom, but it's still too deep to reach by hand."
                    )
                )
            else:
                self.description = (
                    base_desc
                    + (" The water within is crystal clear. The bottom is visible and "
                       "appears empty.")
                )
        else:
            desc = (
                base_desc
                + (
                    " The water below is dark and still. A foul stench rises from the "
                    "depths, making your stomach churn. Something is very wrong here."
                )
            )
            if self.contains_ring:
                desc += (
                    " You think you see something shiny deep within the murky water, but "
                    "it's impossible to tell for sure or reach."
                )
            self.description = desc
        return super().examine(game_state)

    def use_with(self, game_state: GameState, other_item: Item) -> str:
        """Delegate to bucket/fishing rod variants for retrieval attempts."""
        from .Bucket import Bucket
        from .FishingRod import FishingRod
        from .MagneticFishingRod import MagneticFishingRod
        from .ExtendedMagneticFishingRod import ExtendedMagneticFishingRod
        if isinstance(
            other_item,
            (Bucket, FishingRod, MagneticFishingRod, ExtendedMagneticFishingRod),
        ):
            return other_item.use_with(game_state, self)
        return super().use_with(game_state, other_item)

    def search(self, _game_state: GameState) -> str:
        """Search the well for visible items based on purity and ring presence."""
        if self.is_purified:
            if self.contains_ring:
                return (
                    "[event]You peer into the crystal clear water. A [item_name]shiny "
                    "ring[/item_name] glints at the bottom, tantalizingly out of "
                    "reach by hand.[/event]"
                )
            return (
                "[event]You peer into the crystal clear water. The bottom is visible and "
                "empty.[/event]"
            )
        if self.contains_ring:
            return (
                "[failure]You peer into the murky depths. It's hard to see clearly, "
                "but you think you catch a glimpse of something shiny. It's far too "
                "deep to reach.[/failure]"
            )
        return (
            "[failure]You peer into the murky depths. It's too dark and unclear to see "
            "anything of interest.[/failure]"
        )

    def purify(self, game_state: GameState) -> str:
        """Purify the well if examined, update state, and reveal ring if present."""
        if not game_state.get_story_flag(FLAG_WELL_EXAMINED):
            name = self.get_name()
            return (
                "[failure]You hesitate. Why would you cast [spell_name]purify[/spell_name] on the "
                + name
                + "[item_name][/item_name]? Perhaps you should examine it first.[/failure]"
            )
        if self.is_purified:
            name = self.get_name()
            return (
                "[failure]The [item_name]" + name + "[/item_name] is already pure. The water is "
                "crystal clear.[/failure]"
            )
        self.is_purified = True
        if self.contains_ring:
            name = self.get_name()
            return (
                "[event]You cast [spell_name]purify[/spell_name] on the [item_name]"
                + name
                + (
                    "[/item_name]. The murky water shimmers and clears! You can now "
                    "see a [item_name]shiny ring[/item_name] at the bottom, but it's "
                    "still too deep to reach by hand.[/event]"
                )
            )
        name = self.get_name()
        return (
            "[event]You cast [spell_name]purify[/spell_name] on the [item_name]"
            + name
            + (
                "[/item_name]. The murky water shimmers and clears! The bottom is "
                "visible, but there's nothing of interest.[/event]"
            )
        )
