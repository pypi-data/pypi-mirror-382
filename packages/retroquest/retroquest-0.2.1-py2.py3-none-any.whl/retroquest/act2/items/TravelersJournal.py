"""Traveler's Journal item for Act II; sets FLAG_READ_TRAVELERS_JOURNAL and
provides lineage lore.
"""

from ...engine.GameState import GameState
from ...engine.Item import Item
from ..Act2StoryFlags import FLAG_READ_TRAVELERS_JOURNAL

class TravelersJournal(Item):
    """A family journal containing genealogies and lore about Willowbrook and ley sites."""
    def __init__(self) -> None:
        super().__init__(
            name="traveler's journal",
            short_name="journal",
            description=(
                "A well-worn leather journal containing historical notes, family genealogies, "
                "and references to ancient bloodlines. Several passages mention Willowbrook "
                "and its significance in regional history."
            ),
            can_be_carried=True,
        )

    def use(self, game_state: GameState) -> str:
        # Set flag to indicate the journal has been read
        game_state.set_story_flag(FLAG_READ_TRAVELERS_JOURNAL, True)
        return (
            "[event]You carefully open the weathered traveler's journal and begin reading "
            "the faded entries...[/event]\n\n"

            "The journal belongs to [character_name]Lysander Ravencrest[/character_name], a "
            "distant ancestor who traveled these lands centuries ago. His elegant script "
            "reveals fascinating details about your family's ancient heritage:\n\n"

            "*'The bloodline of Ravencrest has long been tied to the mystical energies that "
            "flow through Willowbrook and its surrounding lands. We are not mere wanderers, "
            "but guardians of an ancient pact - keepers of balance between the mortal realm "
            "and the forces beyond. The village of Willowbrook sits upon a convergence of "
            "ley lines, making it a focal point for both protective and destructive magics.'*\n\n"

            "*'I have documented the locations of several hidden sanctuaries and the bloodline "
            "connections to various noble houses throughout the region. The Ravencrest family "
            "crest - a silver tree beneath twin moons - can be found carved into stone markers "
            "at sites of power. These markers serve as keys to accessing restricted archives in "
            "the great libraries.'*\n\n"

            "*'Should any of my descendants find themselves in need of answers about our "
            "heritage, this journal contains references and genealogical charts that will grant "
            "them access to the deepest historical records. The knowledge within could prove "
            "vital when darkness stirs again, as the ancient prophecies foretell it inevitably "
            "will.'*\n\n"

            "[event]The journal is filled with detailed maps, family trees, and scholarly "
            "references that would serve as excellent credentials when researching historical "
            "documents in libraries, archives, or when speaking with historians and scholars. "
            "The information clearly establishes your noble ancestry and legitimate claim to "
            "accessing restricted historical records.[/event]"
        )
