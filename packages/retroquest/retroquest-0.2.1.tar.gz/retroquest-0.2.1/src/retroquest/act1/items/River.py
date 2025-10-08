"""River item: a fishing location with simple availability gating."""

from ...engine.Item import Item
from .Fish import Fish
from ...engine.GameState import GameState

class River(Item):
    """Natural fishing location with a one-time catch until reset."""

    def __init__(self) -> None:
        """Initialize the River item with name, description, and fish availability."""
        super().__init__(
            name="river",
            description=(
                "A gentle river, its waters flowing steadily. It looks like a good spot "
                "for fishing."
            ),
            short_name="river",
        )
        self.fish_available = True

    def use_with(self, game_state: 'GameState', other_item: Item) -> str:
        """Use with FishingRod to catch fish if basics are learned, otherwise fail."""
        from .FishingRod import FishingRod
        if isinstance(other_item, FishingRod):
            if not game_state.get_story_flag("learned_fishing_basics"):
                rod_name = other_item.get_name()
                return (
                    "[failure]You have the [item_name]"
                    + rod_name
                    + (
                        "[/item_name], but you're not quite sure how to fish effectively yet. "
                        "Perhaps someone could teach you.[/failure]"
                    )
                )
            if self.fish_available:
                game_state.add_item_to_inventory(Fish())
                self.fish_available = False
                self.description = (
                    "A gentle river, its waters flowing steadily. You've already fished "
                    "here recently."
                )
                river_name = self.get_name()
                rod_name = other_item.get_name()
                return (
                    "[event]You cast your line into the [item_name]"
                    + river_name
                    + "[/item_name] using the [item_name]"
                    + rod_name
                    + (
                        "[/item_name]. After a moment, you feel a tug and reel in a "
                        "plump [item_name]fish[/item_name]![/event]\n"
                        "You add the fish to your inventory."
                    )
                )
            else:
                return (
                    "[failure]You cast your line again, but the fish aren't biting "
                    "right now.[/failure]"
                )
        else:
            return super().use_with(game_state, other_item)
