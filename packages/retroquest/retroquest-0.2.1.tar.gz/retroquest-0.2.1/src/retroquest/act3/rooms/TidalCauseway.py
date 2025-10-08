"""Tidal Causeway room and related items for Act 3."""

from ...engine.Room import Room
from ..items import Mural
from ..items import RustedLockerKey, BarnacledBeamFragment

class TidalCauseway(Room):
    """Moon-washed causeways linking broken arches to half-drowned plazas."""

    def __init__(self) -> None:
        """Initialize Tidal Causeway with mural and exits."""
        super().__init__(
            name="Tidal Causeway",
            description=(
                "Thin causeways of old stone lift from the black water like ribs. "
                "Moonlight skims the wet stones; salt and wind carry half‑heard "
                "songs. Broken arches stand like quiet mouths, guarding what the "
                "sea keeps."
            ),
            items=[Mural(), BarnacledBeamFragment()],
            characters=[],
            exits={"north": "ShorelineMarkers", "east": "SubmergedAntechamber"},
        )
        self.light_cast = False

    def cast_light_here(self, _game_state):
        """Cast light in the causeway to reveal things hidden in mural-shadow.

        This reveals a rusted locker key tucked into a shadowed niche the first
        time light is focused here. Subsequent casts report nothing new.
        """
        # If we've already focused light here, nothing new will be found.
        if self.light_cast:
            return (
                "[info]Your light washes over the stones; the mural's shadows are "
                "familiar now and nothing new comes free.[/info]"
            )

        # Reveal the rusted key into the room and mark we've cast light.
        self.add_item(RustedLockerKey())
        self.light_cast = True
        return (
            "[event]Your light catches a patch of pigment and a small hollow. In the "
            "shadowed cranny, something metallic flakes free — a corroded key rests "
            "in the rock.[/event]"
        )
