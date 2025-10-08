"""EnchantedAcorn: Forest-offering item used in Act II rituals and interactions."""

from ...engine.Item import Item
from ...engine.GameState import GameState

class EnchantedAcorn(Item):
    """A forest-blessed acorn intended as an offering to sacred spirits."""
    def __init__(self) -> None:
        super().__init__(
            name="enchanted acorn",
            short_name="acorn",
            description=(
                "A perfectly shaped acorn that glows with soft, natural magic. The shell "
                "appears to be made of polished wood with intricate spiral patterns that "
                "seem to move when observed closely. It radiates a sense of ancient wisdom "
                "and connection to the deepest mysteries of the forest. This is clearly a "
                "gift meant for the most sacred forest spirits."
            ),
            can_be_carried=True,
        )

    def use(self, game_state: GameState) -> str:
        current_room = game_state.current_room.name
        if "ancient grove" in current_room.lower():
            # This should be handled by the room or character interaction
            return (
                f"The [item_name]{self.get_name()}[/item_name] pulses with magical energy in "
                "response to the sacred grove. You should offer it to the ancient tree spirit "
                "that dwells here."
            )
        elif "forest" in current_room.lower():
            return (
                f"The [item_name]{self.get_name()}[/item_name] glows softly in the forest, "
                "but it seems to be calling you toward something more ancient and sacred."
            )
        else:
            return (
                f"The [item_name]{self.get_name()}[/item_name] feels dormant here. It likely "
                "has special significance in a more magical location."
            )

    def picked_up(self, game_state: GameState) -> str:
        """Called when the item is picked up by the player."""
        from ..rooms.ForestEntrance import ForestEntrance  # Import here to avoid circular imports
        if isinstance(game_state.current_room, ForestEntrance):
            return ("The moment you touch it, you feel a surge of natural magic - this is no "
                    "ordinary acorn, but a sacred offering imbued with the forest's blessing. "
                    "The forest sprites whisper approvingly as you claim this gift.")
        return ""

    def examine(self, _game_state: GameState) -> str:
        name = self.get_name()
        desc = self.description
        return (
            f"[event]You examine the [item_name]{name}[/item_name]. {desc} "
            "When you hold it up to the light, you can see tiny veins of silver running "
            "through the shell like tree roots. The acorn seems to whisper in a language "
            "older than words, speaking of growth, wisdom, and the eternal cycle of the "
            "forest.[/event]"
        )
