"""Crystal-clear water purification item (Act II)."""

from ...engine.Item import Item
from ...engine.GameState import GameState

class CrystalClearWater(Item):
    """Purifying water item that can cleanse curses and dark enchantments."""
    def __init__(self) -> None:
        super().__init__(
            name="crystal-clear water",
            short_name="water",
            description=(
                "Water from the sacred spring in the Whispering Glade, this liquid is so "
                "pure it seems to glow with its own inner light. The water has been "
                "blessed by the water nymphs and carries powerful purification magic "
                "that can break curses and cleanse dark enchantments. Each drop sparkles "
                "like liquid starlight, and the container feels cool to the touch."
            ),
            can_be_carried=True,
        )

    def use_on_character(self, game_state: GameState, target_character) -> str:
        """Use crystal-clear water on a character to purify them."""
        from ..characters.BarmaidElena import BarmaidElena  # Import here to avoid circular imports
        # Special handling for Elena's curse purification
        if isinstance(target_character, BarmaidElena):
            return target_character.receive_crystal_water_purification(game_state)
        else:
            name = target_character.get_name()
            return (
                "The [item_name]crystal-clear water[/item_name] glows faintly when near "
                f"[character_name]{name}[/character_name], but it seems this blessed water is "
                "meant for someone specifically afflicted by dark magic."
            )

    def examine(self, _game_state: GameState) -> str:
        description = self.description
        return (
            "[event]You examine the [item_name]crystal-clear water[/item_name]. "
            f"{description} The liquid moves with an otherworldly fluidity, and you can "
            "sense the powerful purification magic contained within. This water could break "
            "even the strongest curses.[/event]"
        )
