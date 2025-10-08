"""Base class for all spells in RetroQuest."""
from .Item import Item
from .Character import Character
from .GameState import GameState

class Spell:
    """
    Base class for all spells in RetroQuest.
    Inherit from this class to define specific spells.
    """
    def __init__(self, name: str, description: str) -> None:
        """Initialize the spell with a name and a short description."""
        self.name = name
        self.description = description

    def get_name(self) -> str:
        """Return the spell's programmatic name."""
        return self.name

    def get_description(self) -> str:
        """Return the spell's in-world description used for help and UI."""
        return self.description

    def cast_spell(self, _game_state: GameState) -> str:
        """Casts the spell without a target. This method should be overridden by subclasses."""
        return (
            f"[failure]You cast [spell_name]{self.name}[/spell_name], but nothing "
            "happens.[/failure]"
        )

    def cast_on_item(self, _game_state: GameState, target_item: Item) -> str:
        """Casts the spell on an item. This method should be overridden by subclasses."""
        return (
            f"[failure]You attempt to cast [spell_name]{self.name}[/spell_name] on "
            f"[item_name]{target_item.get_name()}[/item_name], but the spell fizzles and "
            "does not seem to work on this item.[/failure]"
        )

    def cast_on_character(self, _game_state: GameState, target_character: Character) -> str:
        """Casts the spell on a character. This method should be overridden by subclasses."""
        return (
            f"[failure]You attempt to cast [spell_name]{self.name}[/spell_name] on "
            f"[character_name]{target_character.get_name()}[/character_name], but the spell "
            "fizzles and does not seem to work on this character.[/failure]"
        )
