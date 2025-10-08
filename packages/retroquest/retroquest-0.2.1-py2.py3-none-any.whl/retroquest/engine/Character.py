"""Character base class and helpers for in-game NPCs and actors."""

from .GameState import GameState
from .Item import Item


class Character:
    """Base class for all characters in RetroQuest. Inherit to define actors."""

    def __init__(self, name: str, description: str) -> None:
        self.name = name
        self.description = description

    def get_name(self) -> str:
        """Return the character's name."""
        return self.name

    def examine(self, _game_state: GameState) -> str:
        """
        Base 'examine' method for characters. Subclasses should override this if they have
        specific examination details.
        """
        return (
            f"[event]You examine [character_name]{self.get_name()}[/character_name]. "
            f"{self.description}[/event]"
        )

    def talk_to(self, _game_state: GameState) -> str:
        """Default talk_to method. Subclasses should override this for specific dialog."""
        event_msg = (
            f"[event]You speak with the [character_name]{self.name}[/character_name]."
            "[/event]"
        )
        return (
            event_msg + "\n" +
            f"[character_name]{self.name}[/character_name] has nothing to say right now."
        )

    def say_to(self, words: str, _game_state: GameState) -> str:
        """
        Default say_to method for when a player says a specific word to this character.
        Subclasses should override this to handle specific word recognition and responses.
        """
        return (
            f"[dialogue]You say '{words}' to [character_name]{self.name}[/character_name], "
            "but they don't seem to understand or respond to that particular phrase."
            "[/dialogue]"
        )

    def give_item(self, _game_state: GameState, item_object: Item) -> str:
        """
        Default behavior when an item is given to this character.
        Subclasses should override this to handle specific item interactions.
        """
        event_msg = (
            f"[event]You offer the [item_name]{item_object.get_name()}[/item_name] to the "
            f"[character_name]{self.name}[/character_name].[/event]"
        )
        return (
            event_msg + "\n" +
            f"[character_name]{self.name}[/character_name] doesn't seem interested in the "
            f"[item_name]{item_object.get_name()}[/item_name]."
        )

    def buy_item(self, item_name_to_buy: str, _game_state: GameState) -> str:
        """Default buy_item method. Subclasses should override this for specific dialog."""
        event_msg = (
            f"[event]You try to buy the [item_name]{item_name_to_buy}[/item_name] from the "
            f"[character_name]{self.name}[/character_name].[/event]"
        )
        return (
            event_msg + "\n" +
            f"[character_name]{self.name}[/character_name] does not have any "
            f"[item_name]{item_name_to_buy}[/item_name] to sell right now."
        )
