"""FallenRock item for the Collapsed Galleries rescue sequence."""
from ..Act3StoryFlags import FLAG_ACT3_MINERS_RESCUE_STARTED
from ...engine.Item import Item
from ...engine.GameState import GameState


class FallenRock(Item):
    """A mass of collapsed stone blocking the galleries."""

    def __init__(self) -> None:
        """Initialize FallenRock as an unmovable obstacle."""
        self._collapse_stabilized = False
        self._straps_secured = False
        self._passage_freed = False
        super().__init__(
            name="fallen rock",
            description=(
                "A massive pile of stone and debris blocks the passage, sealing off "
                "any further venturing to the east. Muffled voices echo from beyond "
                "the collapse—panicked calls for help and the desperate scraping of "
                "hands against stone. The sounds confirm your worst fears: people are "
                "trapped behind this barrier, their fate hanging in the balance of "
                "whether you can find a way to safely clear the obstruction."
            ),
            short_name='rock',
            can_be_carried=False
        )

    def examine(self, game_state: GameState) -> str:
        """Examine the fallen rock to understand the situation."""
        game_state.set_story_flag(FLAG_ACT3_MINERS_RESCUE_STARTED, True)
        return (
            "[event]You examine the massive pile of fallen rock.[/event] The collapse "
            "appears unstable, with loose stones precariously balanced above. You can "
            "hear desperate voices calling from beyond the barrier—miners are definitely "
            "trapped on the other side. The ceiling sags dangerously, but with the right "
            "reinforcement, you might be able to stabilize the collapse and then clear "
            "a safe passage through."
        )

    def use_with(self, game_state: GameState, other_item: "Item") -> str:
        """Handle rescue item usage on the fallen rock."""
        from .ReinforcedBraces import ReinforcedBraces
        from .SupportStraps import SupportStraps
        from .WedgeBlocks import WedgeBlocks

        if isinstance(other_item, ReinforcedBraces):
            if not game_state.get_story_flag(FLAG_ACT3_MINERS_RESCUE_STARTED):
                return (
                    "[info]You should examine the fallen rock first to understand "
                    "the situation before attempting anything.[/info]"
                )
            if not self._collapse_stabilized:
                self._collapse_stabilized = True
                game_state.remove_item_from_inventory(other_item.name)
                return (
                    "[event]You wedge the reinforced braces under the sagging "
                    "ceiling, stabilizing the collapse. The immediate danger of "
                    "further cave-in is reduced, but the braces need to be secured "
                    "before you can safely clear the passage.[/event]"
                )
            return (
                "[info]The braces are already in place, holding the ceiling "
                "steady.[/info]"
            )
        
        if isinstance(other_item, SupportStraps):
            if not self._collapse_stabilized:
                return (
                    "[info]You need to stabilize the collapse with braces before "
                    "securing them with straps.[/info]"
                )
            if not self._straps_secured:
                self._straps_secured = True
                game_state.remove_item_from_inventory(other_item.name)
                return (
                    "[event]You bind the reinforced braces securely with the "
                    "support straps, ensuring they can withstand the pressure "
                    "when the debris is cleared. The structure is now stable "
                    "enough for the final excavation.[/event]"
                )
            return (
                "[info]The straps are already securing the braces.[/info]"
            )
            
        if isinstance(other_item, WedgeBlocks):
            if not self._straps_secured:
                return (
                    "[info]The braces need to be secured with support straps "
                    "before you can safely clear the passage.[/info]"
                )
            if not self._passage_freed:
                self._passage_freed = True
                game_state.remove_item_from_inventory(other_item.name)
                # Remove the fallen rock from the current room since passage is cleared
                game_state.current_room.remove_item("fallen rock")
                # Add the miners to the room now that they can be reached
                from ..characters.Miners import Miners
                miners = Miners()
                game_state.current_room.add_character(miners)
                return (
                    "[event]You hammer the wedge blocks into the cracks, freeing "
                    "the blocked passage. The fallen rock crumbles away, clearing "
                    "the path forward. Through the newly opened gap, you see the "
                    "trapped miners emerging from the depths![/event]"
                )
            return (
                "[info]The wedge blocks are already securing the passage.[/info]"
            )
        return "[info]That won't help with the fallen rock.[/info]"
