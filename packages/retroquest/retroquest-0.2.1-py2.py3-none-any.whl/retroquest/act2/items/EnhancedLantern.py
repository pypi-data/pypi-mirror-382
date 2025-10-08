"""Enhanced Lantern (Act II Item): gating item for ForestEntrance."""

from ...engine.GameState import GameState
from ...engine.Item import Item
from ..Act2StoryFlags import (
    FLAG_ENHANCED_LANTERN_USED_FOREST_ENTRANCE,
    FLAG_PROTECTIVE_CHARM_USED_FOREST_ENTRANCE,
)

class EnhancedLantern(Item):
    """Magical lantern that reveals hidden paths and magical auras when used."""
    def __init__(self) -> None:
        """Initialize the Enhanced Lantern item with its descriptive text."""
        super().__init__(
            name="enhanced lantern",
            short_name="lantern",
            description=(
                "A magically enhanced lantern that burns with bright, steady light. "
                "The enchantment allows it to illuminate hidden paths and reveal magical "
                "auras that would otherwise remain invisible."
            ),
            can_be_carried=True,
        )

    def use(self, game_state: GameState) -> str:
        from ..rooms.ForestEntrance import ForestEntrance  # Import here to avoid circular imports

        if isinstance(game_state.current_room, ForestEntrance):
            if not game_state.get_story_flag(FLAG_ENHANCED_LANTERN_USED_FOREST_ENTRANCE):
                game_state.set_story_flag(
                    FLAG_ENHANCED_LANTERN_USED_FOREST_ENTRANCE, True
                )
                self.name = 'enhanced lantern (lit)'
                result = (
                    "[item_effect]The Enhanced Lantern's crystal core pulses with magical "
                    "energy, casting ethereal blue light that reveals hidden paths through "
                    "the dense undergrowth. The light seems to resonate with the forest's "
                    "natural magic, illuminating safe routes and warning you away from "
                    "dangerous areas. With this enhanced vision, you can navigate the "
                    "forest with confidence.[/item_effect]"
                )

                # Check if both protective charm and enhanced lantern have been used
                if game_state.get_story_flag(FLAG_PROTECTIVE_CHARM_USED_FOREST_ENTRANCE):
                    result += (
                        "\n\n[success]With both the protective charm's spiritual barrier and "
                        "the enhanced lantern's magical illumination active, the forest's "
                        "deeper paths are now revealed and safe to travel. You can now "
                        "venture deeper into the enchanted woods.[/success]"
                    )

                return result
            else:
                return (
                    "[info]The Enhanced Lantern continues to provide magical illumination, "
                    "keeping the forest paths clearly visible.[/info]"
                )
        else:
            return (
                "You activate the enhanced lantern. Its magical light pierces through "
                "darkness and can reveal hidden passages, magical traces, and secret "
                "paths that ordinary light cannot illuminate."
            )
