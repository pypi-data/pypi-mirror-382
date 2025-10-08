"""Inn Rooms room: private upstairs chambers with hidden journal and coin stash."""

from ...engine.Room import Room
from ...engine.GameState import GameState
from ..items.TravelersJournal import TravelersJournal
from ..items.Coins import Coins

class InnRooms(Room):
    """Quiet lodging floor offering hidden lore item and currency cache.

    Narrative Role:
        Provides a calm interlude location while rewarding exploratory search
        with a lore-bearing journal. Acts as an economy booster via coin group.

    Key Mechanics:
        - ``search()`` spawns ``TravelersJournal`` once (``journal_found`` flag).
        - Pre-populated coin list using comprehension for concise mass items.

    Story Flags:
        - None (local boolean only for discovery state).

    Contents:
        - Items: Multiple ``Coins``; conditional ``TravelersJournal``.
        - Characters: None (maintains solitude atmosphere).

    Design Notes:
        Mirrors other idempotent search patterns; future rest mechanics could
        add recovery bonuses here.
    """

    def __init__(self) -> None:
        """Initialize inn rooms with coin cache and no journal yet discovered."""
        super().__init__(
            name="Inn Rooms",
            description=(
                "Comfortable guest rooms on the upper floor of The Silver Stag Inn. Each room "
                "has a cozy bed, a writing desk, and a window overlooking the Market District. "
                "The rooms are clean and well-maintained, offering a peaceful retreat for "
                "travelers. Faint conversation drifts up from the common room below."
            ),
            items=[Coins() for _ in range(20)],
            characters=[],
            exits={"west": "SilverStagInn"}
        )
        self.journal_found = False

    def search(self, _game_state: GameState, _target: str = None) -> str:
        """Search for the hidden traveler's journal (idempotent).

        Parameters:
            game_state: Unused currently; accepted for interface parity.
            _target: Ignored placeholder for potential targeted search.

        Returns:
            Narrative result describing discovery or repeat search feedback.
        """
        if not self.journal_found:
            # Add the journal to the room when first searched
            journal = TravelersJournal()
            self.add_item(journal)
            self.journal_found = True
            return (
                "[event]You search the inn rooms thoroughly.[/event]\n\nAs you examine the room "
                "carefully, you notice a wooden floorboard near the bed is slightly raised. "
                "Pressing it shifts the board with a soft creak. Lifting it reveals a hidden "
                "space containing a "
                "leather-bound journal deliberately concealed by a previous guest. The pages hold "
                "detailed notes and observations that may aid your journey."
            )
        else:
            return (
                "[event]You search the inn rooms again.[/event]\n\nYou've already searched "
                "this room and found everything of interest."
            )
