"""Locker item for Act III (corroded storage revealing prism lanterns)."""

from ...engine.GameState import GameState
from ...engine.Item import Item


class Locker(Item):
    """Corroded pier locker containing prism lanterns (Act III).

    Narrative Role:
        Environmental container gating access to multiple prism lanterns used in ritual
        lighting.

    Key Mechanics:
        Requires external unlocking (spell or effect). Once unlocked, opening spawns
        lantern items.
    """

    def __init__(self) -> None:
        """Initialize Locker with description and locked state."""
        super().__init__(
            name="Locker",
            description=(
                "A corroded locker wedged under the pier. Salt and time have fused "
                "its lock, resisting ordinary keys and brute effort."
            ),
            short_name="locker",
            can_be_carried=False,
        )
        self.locked: bool = True
        self.opened: bool = False
        # Track whether a rusted key has been forced into the lock and stuck.
        self.rusted_key_stuck = False

    def examine(self, _game_state: GameState) -> str:  # noqa: ARG002
        """Return state-dependent description of the locker."""
        if self.opened:
            return (
                "The door hangs open and the interior is still and cold, silt motes "
                "drifting inside."
            )
        if self.locked:
            return (
                "Barnacles crust the seam; the fused lock will not yield to a "
                "mundane key."
            )
        return "The mechanism is freed; the door can be opened."

    def open(self, game_state: GameState) -> str:
        """Open the locker, spawning prism lanterns if newly opened."""
        from .PrismLantern import PrismLantern  # Local import to avoid circular dependency
        if self.opened:
            return "[info]The locker is already open.[/info]"
        if self.locked:
            return (
                "[failure]You pull at the handle, but the fused lock holds tight. "
                "It cannot open while it remains locked.[/failure]"
            )
        self.opened = True
        for _ in range(3):
            game_state.current_room.items.append(PrismLantern())
        return (
            "[success]With a brittle crack the door gives, revealing three prism lanterns "
            "gleaming behind veils of silt.[/success]"
        )

    def unlock(self, _game_state: GameState) -> str:
        """Free the fused mechanism, allowing the locker to be opened."""
        if not self.locked:
            return "[info]The mechanism is already free.[/info]"

        # Unlocking the fused mechanism requires that a rusted key has been
        # forced into the lock first (it provides purchase on the corroded
        # pins). If the rusted key is not stuck, the mechanism cannot be freed
        # by ordinary means.
        if not self.rusted_key_stuck:
            return (
                "[failure]The lock is fused tight; without something lodged in the "
                "mechanism you cannot free the pins.[/failure]"
            )

        # Proceed to free the mechanism when the rusted key is present.
        self.locked = False
        return (
            "[event]A subtle click echoes under the pier as fused pins release. "
            "The locker can now be opened.[/event]"
        )

    def use_with(self, game_state: GameState, other_item: Item) -> str:
        """Handle being used together with another item.

        Special-case the RustedLockerKey: it cannot open the fused lock, but it
        may get stuck if forced, altering the locker state slightly.
        """
        from .RustedLockerKey import RustedLockerKey
        if isinstance(other_item, RustedLockerKey):
            # The rusted key gets stuck and does not unlock the mechanism.
            self.rusted_key_stuck = True
            game_state.remove_item_from_inventory(other_item.get_name())
            return (
                "[failure]The lock is too corroded for the key to turn. As you tug, "
                "the corroded key jams in the mechanism and will not come free.[/failure]"
            )
        return super().use_with(game_state, other_item)
