"""Mine Overseer character for Cavern Mouth."""
from ...engine import GameState, Character
from ..items.MinersKey import MinersKey
from ..Act3StoryFlags import FLAG_ACT3_MINERS_RESCUE_STARTED

class MineOverseer(Character):
    """Overseer who triggers Miners' Rescue and gives the miner's key."""
    def __init__(self) -> None:
        super().__init__(
            name="Mine Overseer",
            description="A grizzled foreman with a ring of keys and a worried look.",
        )

    def talk_to(self, game_state: GameState) -> str:
        if not game_state.get_story_flag(FLAG_ACT3_MINERS_RESCUE_STARTED):
            game_state.set_story_flag(FLAG_ACT3_MINERS_RESCUE_STARTED, True)
            # Give the miner's key if not already in inventory
            if not any(isinstance(i, MinersKey) for i in game_state.inventory):
                game_state.inventory.append(MinersKey())
            return (
                "The overseer grips your arm, voice hoarse: 'You don't hear them now, but the rock "
                "shifted at dawn. Half a dozen men are trapped behind tons of stone—no air, no "
                "light. We tried to dig, but the walls groan with every blow. Some of the younger "
                "lads... they screamed until their voices gave out. The rest are silent now. Gods, "
                "let them still be alive.'\n"
                "He points north, jaw clenched: 'Collapsed Galleries are blocked, but the Tool "
                "Cache has what you need—braces, straps, blocks. If you can reach them, you might "
                "hold the roof long enough to pull the miners free.'\n"
                "He presses a heavy iron key into your palm, his hand trembling: "
                "[dialogue]'Here—take my key. "
                "It opens the supply crate. Get those miners out.[/dialogue]\n"
                "[event]You receive the [item_name]Miner's Key[/item_name].[/event]'"
            )
        return (
            "The overseer nods grimly. 'The miners are still waiting. The Tool Cache is north.'"
        )
