"""RunicWalls item for the Echo Chambers chant sequence."""
from ...engine.Item import Item
from ...engine.GameState import GameState


class RunicWalls(Item):
    """Runic walls containing the Resonant Chant."""

    def __init__(self) -> None:
        """Initialize RunicWalls as an immovable feature."""
        super().__init__(
            name="runic walls",
            description=(
                "Ancient walls carved with mystical runes that describe a chant "
                "to quiet phantoms and wandering spirits."
            ),
            can_be_carried=False,
            short_name="walls",
        )
        self._rubbings_discovered = False

    def examine(self, game_state: GameState) -> str:
        """Reveal the Resonant Chant instructions and add rubbings to room."""
        from .ResonantChantRubbings import ResonantChantRubbings
        # Add ResonantChantRubbings to the current room if not already discovered
        current_room = game_state.current_room
        if current_room and not self._rubbings_discovered:
            current_room.add_item(ResonantChantRubbings())
            self._rubbings_discovered = True
        return (
            "[info]The runes describe a chant to quiet the phantoms: "
            "'Let stillness echo, let silence bind.' You notice you could make "
            "rubbings of these ancient symbols.[/info]"
        )
