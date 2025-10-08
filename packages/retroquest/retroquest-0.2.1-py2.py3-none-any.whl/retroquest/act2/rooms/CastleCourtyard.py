"""Castle Courtyard room: martial training hub with dialogue-gated hidden diary."""

from ...engine.Room import Room
from ...engine.GameState import GameState
from ..characters.SirCedric import SirCedric
from ..characters.TrainingMaster import TrainingMaster
from ..characters.Squires import Squires
from ..items.SquiresDiary import SquiresDiary
from ..Act2StoryFlags import FLAG_SQUIRES_TALKED_TO

class CastleCourtyard(Room):
    """Training yard blending character interaction with gated item discovery.

    Narrative Role:
        Combines martial culture ambience with social progression—players must
        speak to the squires before discovering the hidden diary.

    Key Mechanics:
    - ``search()`` grants ``Squire's Diary`` only after ``FLAG_SQUIRES_TALKED_TO``.
        - Lazy item injection via ``add_item`` with ``diary_found`` boolean for
          idempotence.

    Story Flags:
        - Reads: ``FLAG_SQUIRES_TALKED_TO``.
        - Sets: None (follow‑up logic delegated to diary usage elsewhere).

    Contents:
        - NPCs: ``SirCedric``, ``TrainingMaster``, ``Squires``.
        - Conditional Item: ``Squire's Diary``.

    Design Notes:
        Illustrates conversation-before-loot gating; pattern could migrate to a
    reusable mixin (e.g., ``ConversationGateSearch``) if repeated.
    """

    def __init__(self) -> None:
        """Initialize courtyard with training NPCs and no pre-placed items."""
        super().__init__(
            name="Castle Courtyard",
            description=(
                "An expansive courtyard within the castle walls, featuring training grounds "
                "where knights practice their swordwork. Ancient oak trees provide shade for "
                "stone benches, and a stable houses magnificent warhorses. The castle's main "
                "hall rises before you, its great doors carved with the symbols of Greendale's "
                "noble houses."
            ),
            items=[],
            characters=[SirCedric(), TrainingMaster(), Squires()],
            exits={"east": "CastleApproach", "north": "ResidentialQuarter", "west": "GreatHall"}
        )
        self.diary_found = False

    def search(self, game_state: GameState, _target: str = None) -> str:
        """Search for the hidden diary after prerequisite dialogue.

        Parameters:
            game_state: Global game state used to query story flags.
            _target: Ignored placeholder for future targeted search verbs.

        Returns:
            Narrative result string reflecting discovery or gating feedback.
        """
        if not self.diary_found:
            # Check if squires have been talked to first
            if not game_state.get_story_flag(FLAG_SQUIRES_TALKED_TO):
                return (
                    "[event]You search around the stone benches and training equipment, "
                    "but you don't find anything of particular interest. The squires are "
                    "watching you curiously — perhaps you should talk to them first to learn "
                    "more about this place.[/event]"
                )

            # Add the squire's diary when searching under stone benches (after talking to squires)
            diary = SquiresDiary()
            self.add_item(diary)
            self.diary_found = True
            return (
                "[event]You search around the stone benches and training equipment. "
                "Remembering what the squires told you, you look more carefully under "
                "one of the ancient stone benches and discover a worn leather diary "
                "that appears to have been left by a former squire.[/event]\n\n"
                "[success]You found a [item_name]squire's diary[/item_name]![/success]"
            )
        return "[info]You've already searched this area thoroughly.[/info]"
