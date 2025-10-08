"""City Notice Board (Act II environmental/economy item)."""

from ...engine.GameState import GameState
from ...engine.Item import Item

class CityNoticeBoard(Item):
    """Public notice board with postings that provide in-game leads and quests."""
    def __init__(self) -> None:
        super().__init__(
            name="city notice board",
            short_name="board",
            description=(
                "A large wooden board posted with official notices, job postings, and "
                "announcements. The most prominent posting seeks brave souls for 'The "
                "Gathering Storm' — a call for heroes to help defend against rising dark "
                "forces."
            ),
            can_be_carried=False,
        )

    def examine(self, _game_state: GameState) -> str:
        return (
            "You read through the various postings on the notice board. Most are mundane "
            "announcements about trade regulations and festival dates, but one catches "
            "your eye: a formal call for heroes to aid in 'The Gathering Storm.' The "
            "notice bears the seal of Sir Cedric and promises great rewards for those "
            "brave enough to answer the call."
        )
