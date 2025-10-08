"""Drowned courtyard with tideward sigil pillars."""
from ...engine.GameState import GameState
from ...engine.Room import Room
from ..items import WardingPillars, SeaweedTangle


class OuterWards(Room):
    """
    A flooded courtyard with three ancient pillars for tideward sigil work.

    Narrative Role:
    - Central location for the Tideward Sigils side quest
    - Demonstrates the connection between purification magic and sigil crafting
    - Gateway area that controls access to deeper sanctum areas

        Key Mechanics:
        - Search action describes the courtyard and points out the warding pillars;
            it does not itself attune the sigils.
        - Pillar purification and sigil engraving are implemented on the
            `WardingPillars` item (purify/use_with), which is responsible for
            setting the attunement flag when the player performs the correct steps.
    """
    def __init__(self) -> None:
        """Initialize Outer Wards with warding pillars and exits."""
        super().__init__(
            name="Outer Wards",
            description=(
                "The courtyard lies half-swallowed by the sea. Three ancient pillars "
                "rise from the black water, their faces scored with shallow marks. "
                "Brine beads along the carved lines and they catch the moon in small "
                "rings of light. The air here tastes of old promises and slow tides."
            ),
            items=[WardingPillars(), SeaweedTangle()],
            characters=[],
            exits={
                "south": "SubmergedAntechamber",
                "east": "CollapsedPier",
                "west": "ShorelineMarkers"
            },
        )

    def search(self, _game_state: GameState, _target: str = None) -> str:
        """Describe the courtyard and warding pillars without performing attunement.

        Note: sigil attunement is performed by interacting with the
        `WardingPillars` item (for example, casting purify on the pillars and
        using Moon Rune Shards with them). This method only returns flavor
        text describing the pillars.
        """
        return (
            "[event]You search the drowned courtyard thoroughly. Apart from the "
            "three ancient warding pillars rising from the black water, there is "
            "little of interest; the pillars alone seem keyed to the moon and tide."
            "[/event]"
        )
