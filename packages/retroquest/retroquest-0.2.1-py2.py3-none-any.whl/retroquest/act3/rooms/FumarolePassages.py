"""Fumarole Passages room for Act 3."""

from ...engine.Room import Room
from ...engine.GameState import GameState
from ..Act3StoryFlags import (
    FLAG_ACT3_BREATH_OF_THE_MOUNTAIN_STARTED,
    FLAG_ACT3_BREATH_OF_THE_MOUNTAIN_COMPLETED,
)
from ..items.VentStone import VentStone
from ..items.HeatWardMix import HeatWardMix
from ..characters.PhoenixGuardian import PhoenixGuardian


class FumarolePassages(Room):
    """Narrow tunnels exhaling rhythmic heat like a great sleeping bellows."""
    def __init__(self) -> None:
        """Initialize Fumarole Passages with description and exits."""
        super().__init__(
            name="Fumarole Passages",
            description=(
                "Narrow tunnels exhale a rhythmic, breath-like heat; stone vents chuff "
                "and sigh as if the mountain itself sleeps and dreams. Curtains of "
                "steam veil the low passages, and the air tastes faintly of sulfur "
                "and warm metal. Here and there a vent hisses sparks that glass the "
                "rock into smoky, translucent streaks, while the floor bears the "
                "pale scars of old fittings—tiny holes and rubbed brass where mounts "
                "were once bolted. Each step sends a warm gust that carries a distant "
                "clink of metal and the steady, low sigh of fumaroles farther below."
            ),
            # Provide multiple vent stones here so players can perform the
            # three required calibrations during the Breath of the Mountain
            # side quest.
            items=[VentStone(), VentStone(), VentStone()],
            characters=[PhoenixGuardian()],
            exits={"south": "PhoenixCrater", "west": "MirrorTerraces"},
        )
        # Local state: how many vent stones have been installed/calibrated here
        self._vent_calibrations = 0

    def calibrate_with_stone(self, game_state, stone: VentStone) -> str:
        """Called when a VentStone is used in this room. Tracks calibrations.

        After three calibrations the vents are considered synchronized and the
        Breath of the Mountain quest can be progressed by applying the heat ward.
        """
        # Mark quest started
        game_state.set_story_flag(FLAG_ACT3_BREATH_OF_THE_MOUNTAIN_STARTED, True)

        # Remove the stone from inventory (one use per stone)
        if stone in game_state.inventory:
            game_state.inventory.remove(stone)
        else:
            # Could also be in the room; if so, remove that instance
            try:
                self.items.remove(stone)
            except ValueError:
                pass

        self._vent_calibrations += 1
        if self._vent_calibrations < 3:
            return (
                "[event]You press the vent stone into the channel. The vents click and "
                "a rhythmic hiss grows steadier—the timing seems closer to being "
                "synchronized.[/event]"
            )

        return (
            "[event]With a final fit, the vents' rhythms align into a deep, slow "
            "breath. You sense the passages will now accept a heat ward to steady "
            "the crossing intervals.[/event]"
        )

    def apply_heat_ward(self, game_state, mix: HeatWardMix) -> str:
        """Apply the heat ward mix to the calibrated vents. Requires calibration."""
        # Ensure calibration done
        if self._vent_calibrations < 3:
            return (
                "[failure]The vents are not yet synchronized; the ward would be "
                "unstable. Calibrate more vent stones first.[/failure]"
            )

        # Consume the mix from inventory if present
        game_state.inventory.remove(mix)

        # Set completion flag and open the path to Phoenix Crater
        game_state.set_story_flag(FLAG_ACT3_BREATH_OF_THE_MOUNTAIN_COMPLETED, True)

        # Return an event describing the successful application
        return (
            "[event]You daub the heat-ward mix into the vents and seams. The rock "
            "grows a touch cooler around your hands as the ward seals into place. "
            "Down the tunnel you notice the gusting heat flatten into a steady "
            "breath—passage through the fumaroles is now safe for a short interval."
            "[/event]"
        )

    def get_exits(self, game_state: GameState) -> dict[str, str]:
        """Return exits, hiding south until Breath of the Mountain completed.

        The south exit to Phoenix Crater is a hazardous crossing while the vents
        are uncalibrated and the heat ward is not applied. Hide the exit from
        the exits map until the Breath of the Mountain side quest is completed.
        """
        exits = {**self.exits}

        # Hide or block the south exit until the ward has been applied
        if not game_state.get_story_flag(FLAG_ACT3_BREATH_OF_THE_MOUNTAIN_COMPLETED):
            exits.pop('south', None)

        return exits

    def on_enter(self, game_state: GameState) -> None:
        """Set the Breath of the Mountain started flag when entering the room."""
        game_state.set_story_flag(FLAG_ACT3_BREATH_OF_THE_MOUNTAIN_STARTED, True)
