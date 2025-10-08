"""Light spell for Act I — dispatches a lighting request to the current room."""

from ...engine.Spell import Spell
from ...engine.GameState import GameState

class LightSpell(Spell):
    """Spell that produces a small sphere of light to illuminate dark places."""

    def __init__(self) -> None:
        description = (
            "A simple spell that conjures a sphere of light to illuminate dark areas."
        )
        super().__init__("light", description)

    def cast_spell(self, game_state: GameState) -> str:
        """Delegate the effect to the current room's light method.

        Rooms implement contextual effects; this method simply forwards
        the call and returns the room's narrative.
        """

        current_room = game_state.current_room
        return current_room.light(game_state)
