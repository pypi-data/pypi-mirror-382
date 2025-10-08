"""ResonantChantRubbings item for the Echo Chambers."""
from ...engine.Item import Item
from ...engine.GameState import GameState
from ..Act3StoryFlags import FLAG_ACT3_OATH_OF_STILLNESS_COMPLETED
from .EchoStones import EchoStones


class ResonantChantRubbings(Item):
    """Rubbings of the Resonant Chant from the Echo Chambers."""

    def __init__(self) -> None:
        """Initialize Resonant Chant Rubbings."""
        super().__init__(
            name="Resonant Chant Rubbings",
            description=(
                "Carefully made rubbings of ancient runes containing the "
                "Resonant Chant: 'Let stillness echo, let silence bind.'"
            ),
            can_be_carried=True,
            short_name="rubbings"
        )

    def use_with(self, game_state: GameState, other_item: Item) -> str:
        """Handle using resonant chant rubbings with blessed echo stones."""
        if isinstance(other_item, EchoStones):
            # Check if the echo stones are blessed
            if other_item.are_blessed():
                # Perform the Oath of Stillness
                game_state.set_story_flag(FLAG_ACT3_OATH_OF_STILLNESS_COMPLETED, True)

                # Remove the rubbings from inventory (consumed in the ritual)
                game_state.remove_item_from_inventory(self.get_name())

                # Remove phantoms from current room if it's StillnessVestibule
                current_room = game_state.current_room
                if current_room and current_room.__class__.__name__ == "StillnessVestibule":
                    from ..characters.WanderingPhantoms import WanderingPhantoms
                    phantoms_to_remove = [char for char in current_room.characters
                                          if isinstance(char, WanderingPhantoms)]
                    for phantom in phantoms_to_remove:
                        current_room.characters.remove(phantom)

                return (
                    "[event]You recite the resonant chant at each stone. [/event]\n"
                    "[success]The words "
                    "echo and re-echo, building into a harmonious silence that "
                    "banishes the wandering phantoms. The path to the dragon's hall "
                    "now lies open.[/success]"
                )
            else:
                return (
                    "[failure]The stones remain cold and unresponsive. They must be "
                    "sanctified before the chant can take hold.[/failure]"
                )
        else:
            return f"[failure]The {other_item.get_name()} has no effect on the rubbings.[/failure]"
