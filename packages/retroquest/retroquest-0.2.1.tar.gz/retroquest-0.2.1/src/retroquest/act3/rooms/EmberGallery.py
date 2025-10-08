"""Ember Gallery room for Act 3."""

from ...engine.Room import Room
from ..items.AshFern import AshFern
from ..items.CooledSlag import CooledSlag


class EmberGallery(Room):
    """A vaulted cavern veined with cooling flows smelling of charcoal and iron."""
    def __init__(self) -> None:
        """Initialize Ember Gallery with description and exits."""
        super().__init__(
            name="Ember Gallery",
            description=(
                "A vaulted cavern veined with cooling flows; the air smells of "
                "charcoal and iron. Streaks of glassed lava lace the walls, "
                "catching stray cinders that glow like embers in the gloom. "
                "Steam sighs from fissures and pools of blackened water mirror "
                "faint, dancing light. Worktables gather scattered fragments of "
                "fireglass and ash‑tumbled tools where attendants hammer and "
                "sort cooled slag for wards. The heat here is a steady, low "
                "thrum — a reminder that the mountain breathes beneath your "
                "feet."
            ),
            items=[],
            characters=[],
            exits={
                "north": "MirrorTerraces",
                "west": "LowerSwitchbacks"
            },
        )

        # Track whether deposits have been discovered by searching
        self._deposits_revealed = False

    def search(self, _game_state, _target: str = None) -> str:
        """Reveal ash-fern and cooled slag deposits when searched the first time."""
        if not self._deposits_revealed:
            self._deposits_revealed = True
            # Add items to the room so they can be taken
            self.items.append(AshFern())
            self.items.append(CooledSlag())
            return (
                "[event]You sift through the sorted fragments on the worktable and "
                "find a brittle frond of ash-fern tucked in a tool roll, and a pile "
                "of cooled slag fragments sifted into a shallow basin. They look "
                "suitable for warding mixtures.[/event]"
            )

        return (
            "You search the Ember Gallery again but find nothing new beyond the "
            "worktables and sorted fragments.")
