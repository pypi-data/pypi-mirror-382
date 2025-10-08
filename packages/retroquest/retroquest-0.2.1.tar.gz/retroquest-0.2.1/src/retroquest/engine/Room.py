"""Base class for all rooms in RetroQuest."""
from typing import Union
from .Item import Item  # Added import
from .Character import Character # Added import
from .GameState import GameState  # Added for GameState type hint

class Room:
    """
    Base class for all rooms in RetroQuest.
    Inherit from this class to define specific rooms.
    """
    def __init__(self, name: str, description: str, items: Union[list[Item], None] = None,
                 characters: Union[list[Character], None] = None,
                 exits: Union[dict[str, str], None] = None) -> None:
        self.name = name
        self.description = description
        self.items = items if items is not None else []
        self.characters = characters if characters is not None else []
        self.exits = exits if exits is not None else {}

    def enter(self) -> None:
        """Called when the player enters the room."""
        print(self.description)

    def get_items(self) -> list[Item]:
        """Returns the list of items currently in the room."""
        return self.items

    def add_item(self, item: Item) -> None:
        """Adds an item to the room's list of items."""
        self.items.append(item)

    def add_character(self, character: Character) -> None:
        """Adds a character to the room's list of characters."""
        self.characters.append(character)

    def get_characters(self) -> list[Character]:
        """Returns the list of characters currently in the room."""
        return self.characters

    def get_exits(self, _game_state: GameState) -> dict[str, str]:
        """Return static exit mapping; parameter reserved for dynamic overrides."""
        return self.exits

    def get_ambient_sound(self) -> str:
        """Returns a description of the ambient sound of the room."""
        return "It is quiet here."

    def get_item_by_name(self, item_name: str) -> Union[Item, None]:
        """
        Retrieves an item from the room by its name (case-insensitive).
        Returns the item object if found, otherwise None.
        """
        item_name_lower = item_name.lower()
        for item in self.items:
            if item.get_name().lower() == item_name_lower:
                return item
        return None

    def get_character_by_name(self, character_name: str) -> Union[Character, None]:
        """
        Retrieves a character from the room by its name (case-insensitive).
        Returns the character object if found, otherwise None.
        """
        character_name_lower = character_name.lower()
        for character in self.characters:
            if character.get_name().lower() == character_name_lower:
                return character
        return None

    def remove_item(self, item_name: str) -> Union[Item, None]:
        """
        Removes an item from the room by its name (case-insensitive).
        Returns the item object if removed, otherwise None.
        """
        item_to_remove = self.get_item_by_name(item_name)
        if item_to_remove:
            self.items.remove(item_to_remove)
            return item_to_remove
        return None

    def describe(self, game_state: GameState) -> str:
        """Return a full description of the room, including items, characters, and exits."""
        desc = f"[bold]{self.name}[/bold]\n"
        desc += self.description + '\n'
        visible_items = [item for item in self.items]
        if visible_items:
            # Group items by name and count them
            item_counts = {}
            for item in visible_items:
                item_name = item.get_name()
                item_counts[item_name] = item_counts.get(item_name, 0) + 1

            # Create formatted item list with counts
            item_descriptions = []
            for item_name, count in item_counts.items():
                if count > 1:
                    item_descriptions.append(f"[item_name]{count} {item_name}[/item_name]")
                else:
                    item_descriptions.append(f"[item_name]{item_name}[/item_name]")

            item_names = ', '.join(item_descriptions)
            desc += f"\nItems you can see: {item_names}"
        if self.characters:
            # Use get_name for character instances
            character_names = ', '.join(
                f"[character_name]{c.get_name()}[/character_name]" for c in self.characters
            )
            desc += f"\nCharacters present: {character_names}"
        exits = self.get_exits(game_state)
        if exits:
            exit_names = ', '.join(
                f"[exits]{direction}[/exits] ({destination})"
                for direction, destination in exits.items()
            )
            desc += f"\nExits: {exit_names}"
        return desc

    def search(self, _game_state: GameState, _target: str = None) -> str:
        """Search the room; base implementation reveals nothing new.

        Underscore-prefixed parameters keep polymorphic signature while avoiding unused
        variable lint warnings.
        """
        return (
            "You search around the [room_name]"
            f"{self.name}[/room_name], but find nothing of interest beyond what you can "
            "already see."
        )

    def rest(self, _game_state: GameState) -> str:
        """Rest briefly; base implementation has no mechanical effect."""
        return "You rest for a moment, gathering your strength."

    def light(self, _game_state: GameState) -> str:
        """Handle lighting action; base implementation assumes sufficient light."""
        return "The room is already well lit."

    def on_enter(self, _game_state: GameState) -> None:
        """Hook when player enters; override for custom scripted behaviors."""
        return ""
