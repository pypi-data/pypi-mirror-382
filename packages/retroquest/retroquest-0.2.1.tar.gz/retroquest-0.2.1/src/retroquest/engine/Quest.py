"""Base class for all quests in RetroQuest."""
from .GameState import GameState

class Quest:
    """
    Base class for all quests in RetroQuest.
    """
    def __init__(self, name: str, description: str, completion: str = None) -> None:
        self.name = name
        self.description = description
        self.completion = completion or f"You have completed the quest '{name}'."
        self.is_completed_flag = False

    def check_trigger(self, game_state: GameState) -> bool:
        """Override in subclasses to check if the quest should be triggered."""
        return False

    def check_completion(self, game_state: GameState) -> bool:
        """Override in subclasses to check if the quest is completed."""
        return self.is_completed_flag

    def complete(self, game_state: GameState) -> str:
        """Mark the quest as completed and return completion message."""
        self.is_completed_flag = True
        return self.completion

    def check_update(self, game_state: GameState) -> bool:
        """
        Override in subclasses to update quest state dynamically. Return True if quest log
        should update.
        """
        return False

    def is_main(self) -> bool:
        """Return True if this is a main quest. Override in subclasses for main quests."""
        return False
