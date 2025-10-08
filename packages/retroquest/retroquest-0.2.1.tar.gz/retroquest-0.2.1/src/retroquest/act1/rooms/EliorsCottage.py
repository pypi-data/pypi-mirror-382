"""Elior's Cottage room: tutorial sanctuary with gated exits and first search reward."""

from ...engine.Room import Room
from ...engine.GameState import GameState
from ..items.Lantern import Lantern
from ..characters.Grandmother import Grandmother
from ..items.FadedPhotograph import FadedPhotograph
from ..Act1StoryFlags import FLAG_FOUND_PHOTO

class EliorsCottage(Room):
    """Introductory sanctuary space with staged exits and first flag-based discovery.

    Narrative Role:
        Establishes emotional baseline (Grandmother) and safe exploratory cadence.

    Key Mechanics:
        - Exits hidden until ``can_leave()`` invoked (soft tutorial pacing).
        - ``search()`` spawns ``FadedPhotograph`` once and sets ``FLAG_FOUND_PHOTO``.

    Story Flags:
        - Sets: ``FLAG_FOUND_PHOTO`` when photograph discovered.
        - Reads same to prevent duplication.

    Contents:
        - Items: ``Lantern``; conditional ``FadedPhotograph``.
        - NPC: ``Grandmother``.

    Design Notes:
        Exit reveal pattern could migrate to a ``TutorialRoom`` abstraction if reused.
    """
    def __init__(self) -> None:
        """Initialize the cottage room with base items and no exits initially.

        Exits are intentionally empty to delay outward movement until
        ``can_leave`` is invoked (tutorial pacing). Adds the starting
        ``Lantern`` item and the ``Grandmother`` character.
        """
        super().__init__(
            name="Elior's Cottage",
            description=(
                "A modest cottage with a straw roof and a cozy hearth. "
                "The scent of fresh bread and old books fills the air. "
                "Sunlight filters through lace curtains, illuminating "
                "shelves lined with trinkets and memories. A sturdy wooden "
                "table sits in the center, and a gentle fire crackles in the "
                "hearth. Grandmother hums softly in her rocking chair, her "
                "eyes twinkling with wisdom and warmth."
            ),
            items=[Lantern()],
            characters=[Grandmother()],
            exits={}  # Start with empty exits
        )

    def can_leave(self) -> None:
        """Populate exits if they have not yet been revealed.

        This lazy population models a soft gating tutorial step so the
        player engages with the room (dialogue / search) before leaving.
        """
        if not self.exits:
            self.exits = {"south": "VegetableField", "east": "VillageSquare"}

    def search(self, game_state: GameState, _target: str = None) -> str:
        """Search the cottage for hidden items.

        On first successful search spawns a ``FadedPhotograph`` and sets the
        ``FLAG_FOUND_PHOTO`` story flag. Subsequent searches yield no new
        results.

        Parameters:
            game_state: Global game progression state for flag checks.
            _target: Ignored (reserved for future targeted search verbs).

        Returns:
            A narrative string describing the outcome of the search.
        """
        if not game_state.get_story_flag(FLAG_FOUND_PHOTO):
            photo = FadedPhotograph()
            self.items.append(photo)
            game_state.set_story_flag(FLAG_FOUND_PHOTO, True)
            return (
                "You search the cottage thoroughly and discover a "
                f"[item_name]{photo.get_name()}[/item_name] hidden in a drawer."
            )
        return "You search the cottage but find nothing new."
