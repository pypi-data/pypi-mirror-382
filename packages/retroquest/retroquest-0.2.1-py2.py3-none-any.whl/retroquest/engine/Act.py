"""Engine Act base class and helpers."""

from .GameState import GameState

class Act:
    """Container for rooms, quests, music and act-level helpers."""

    def __init__(self, name: str, rooms: dict, quests: list, music_file: str,
                 music_info: str) -> None:
        """Initialize the Act with content and metadata."""
        self.name = name
        self.rooms = rooms
        self.quests = quests
        self.music_file = music_file
        self.music_info = music_info

    def get_act_intro(self) -> str:
        """Return an introduction string for the act (override in acts)."""
        return ""

    def setup_gamestate(self, _game_state: GameState) -> None:
        """Hook for act-specific GameState initialization. Default is no-op."""

    def is_completed(self, _game_state: GameState) -> bool:
        """Return True when the act's completion conditions are met."""
        return False
