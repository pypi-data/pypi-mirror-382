"""SilverTree: Environmental item anchoring the Ancient Grove encounters."""

from ...engine.Item import Item
from ..characters.AncientTreeSpirit import AncientTreeSpirit
from ...engine.GameState import GameState

class SilverTree(Item):
    """Ancient silver-barked tree that anchors the Ancient Grove and related encounters."""
    def __init__(self) -> None:
        super().__init__(
            name="silver-barked tree",
            short_name="tree",
            description=(
                "A magnificent ancient tree that towers above all others, its silver bark "
                "shimmering with an inner light that seems to pulse in rhythm with your "
                "heartbeat. The bark is smooth as polished metal yet warm to the touch, "
                "and intricate spiraling patterns flow across its surface like living "
                "veins of starlight. This is the dwelling place of the Ancient Tree Spirit."
            ),
            can_be_carried=False,
        )
        self.examined = False

    def examine(self, game_state: GameState) -> str:
        """Examine the magnificent silver-barked tree."""
        from ..rooms.AncientGrove import AncientGrove  # Import here to avoid circular imports

        if not self.examined:
            self.examined = True
            # Add the Ancient Tree Spirit to the room only if we're in the Ancient Grove
            if isinstance(game_state.current_room, AncientGrove):
                ancient_spirit = AncientTreeSpirit()
                game_state.current_room.characters.append(ancient_spirit)
                return (
                    "[environment_description]The ancient tree towers above you, its silver bark "
                    "shimmering with an inner light that seems to pulse in rhythm with your "
                    "heartbeat. The bark is smooth as polished metal yet warm to the touch, and "
                    "intricate spiraling patterns flow across its surface like living veins of "
                    "starlight. Its massive canopy spreads wide, with leaves that catch and "
                    "reflect light in impossible ways. You sense an ancient presence within - "
                    "older than memory, wise beyond measure, and deeply connected to the very "
                    "essence of the forest. As you study the tree more closely, the silver bark "
                    "begins to glow more brightly, and suddenly you feel a powerful presence "
                    "emerge from within. The Ancient Tree Spirit has awakened to your reverent "
                    "attention.[/environment_description]"
                )
            else:
                return (
                    "[environment_description]The ancient tree towers above you, its silver bark "
                    "shimmering with an inner light that seems to pulse in rhythm with your "
                    "heartbeat. The bark is smooth as polished metal yet warm to the touch, and "
                    "intricate spiraling patterns flow across its surface like living veins of "
                    "starlight. Its massive canopy spreads wide, with leaves that catch and "
                    "reflect light in impossible ways. You sense an ancient presence within - "
                    "older than memory, wise beyond measure, and deeply connected to the very "
                    "essence of the forest. This is no mere tree, but the dwelling place of the "
                    "Ancient Tree Spirit.[/environment_description]"
                )
        else:
            return (
                "[environment_description]The magnificent silver-barked tree continues to "
                "radiate ancient power and wisdom. Its presence fills you with a sense of "
                "reverence and connection to the natural world.[/environment_description]"
            )
