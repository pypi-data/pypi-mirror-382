"""Vegetable Field room: blighted crops establishing early restorative themes."""

from ...engine.GameState import GameState
from ...engine.Room import Room
from ..items.WitheredCarrot import WitheredCarrot
from ..items.RustyHoe import RustyHoe
from ..items.DullKnife import DullKnife
from ..Act1StoryFlags import FLAG_INVESTIGATED_WITHERED_CROPS

class VegetableField(Room):
    """Blighted agricultural scene auto-triggering passive investigation flag.

    Narrative Role:
        Conveys ecological imbalance and seeds restorative magic expectations.

    Key Mechanics:
        - ``on_enter()`` sets ``FLAG_INVESTIGATED_WITHERED_CROPS`` unprompted.
        - Provides multiple basic experimental items.

    Story Flags:
        - Sets: ``FLAG_INVESTIGATED_WITHERED_CROPS``.

    Contents:
        - Items: ``WitheredCarrot``, ``RustyHoe``, ``DullKnife``.
        - Characters: None.

    Design Notes:
        Later visual state swap possible after growth spell or quest resolution.
    """
    def __init__(self) -> None:
        """Initialize the Vegetable Field and its passive investigation flag behavior."""
        super().__init__(
            name="Vegetable Field",
            description=(
                "Rows of withered crops stretch beneath a brooding gray sky. The earth is "
                "cracked and dry, with only a few stubborn carrots and a rusty hoe hinting at "
                "better days. A faint breeze rustles the brittle leaves, carrying the scent "
                "of soil and distant rain. The field feels quiet, as if holding its breath, "
                "waiting for a touch of magic to bring it back to life."
            ),
            items=[WitheredCarrot(), RustyHoe(), DullKnife()],
            characters=[],
            exits={"north": "EliorsCottage", "east": "VillageWell", "south": "ChickenCoop"}
        )

    def on_enter(self, game_state: GameState) -> None:
        # Set the story flag when the player enters the field
        game_state.set_story_flag(FLAG_INVESTIGATED_WITHERED_CROPS, True)
        super().on_enter(game_state)
