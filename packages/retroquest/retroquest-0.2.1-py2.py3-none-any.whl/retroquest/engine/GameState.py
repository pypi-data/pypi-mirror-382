"""Game state management for RetroQuest."""
from typing import Any, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from .Item import Item
    from .Quest import Quest

class GameState:
    """
    Holds the mutable state of the currently played game: current room, inventory,
    history, and visited rooms.
    """
    def __init__(self, starting_room: Any, all_rooms: dict, all_quests: list) -> None:
        self.current_room = starting_room
        self.all_rooms = all_rooms
        # Inventory supports carrying multiple items of the same type,
        # displayed as batched counts
        self.inventory = []
        self.history = []
        self.visited_rooms = [starting_room.name]
        self.known_spells = []
        self.story_flags = []  # Replace journal_read_prologue_entry
        self.non_activated_quests = all_quests
        self.activated_quests = []  # This will hold quests that have been activated
        self.completed_quests = []  # This will hold quests that have been completed

    def mark_visited(self, room: Any) -> None:
        """Mark a room as visited by adding it to the visited rooms list."""
        if room.name not in self.visited_rooms:
            self.visited_rooms.append(room.name)

    def set_story_flag(self, flag_name: str, value: bool) -> None:
        """Sets or updates a story flag."""
        for i, (name, _) in enumerate(self.story_flags):
            if name == flag_name:
                self.story_flags[i] = (flag_name, value)
                return
        self.story_flags.append((flag_name, value))

    def get_story_flag(self, flag_name: str) -> bool:
        """Gets the value of a story flag. Returns False if not found."""
        for name, value in self.story_flags:
            if name == flag_name:
                return value
        return False

    def get_inventory_summary(self) -> dict[str, int]:
        """Returns a dictionary with item names as keys and counts as values."""
        item_counts = {}
        for item in self.inventory:
            item_name = item.get_name()
            if item_name in item_counts:
                item_counts[item_name] += 1
            else:
                item_counts[item_name] = 1
        return item_counts

    def get_item_count(self, item_name: str) -> int:
        """
        Returns the count of items with the given name or short name in inventory
        (case-insensitive).
        """
        item_name_lower = item_name.lower()
        count = 0
        for item in self.inventory:
            if (item.get_name().lower() == item_name_lower or
                item.get_short_name().lower() == item_name_lower):
                count += 1
        return count

    def has_item(self, item_name: str) -> bool:
        """
        Checks if an item with the given name or short name is in the player's
        inventory (case-insensitive).
        """
        item_name_lower = item_name.lower()
        for item in self.inventory:
            if (item.get_name().lower() == item_name_lower or
                item.get_short_name().lower() == item_name_lower):
                return True
        return False

    def remove_item_from_inventory(self, item_name: str, count: int = 1) -> int:
        """
        Removes up to 'count' items from the player's inventory by name.
        Returns the actual number of items removed.
        """
        item_name_lower = item_name.lower()
        removed_count = 0
        items_to_remove = []
        for item in self.inventory:
            if removed_count >= count:
                break
            if item.get_name().lower() == item_name_lower:
                items_to_remove.append(item)
                removed_count += 1
        for item in items_to_remove:
            self.inventory.remove(item)
        return removed_count

    def remove_all_items_from_inventory(self, item_name: str) -> int:
        """
        Removes all items with the given name from the player's inventory.
        Returns the number of items removed.
        """
        item_name_lower = item_name.lower()
        items_to_remove = []
        for item in self.inventory:
            if item.get_name().lower() == item_name_lower:
                items_to_remove.append(item)
        for item in items_to_remove:
            self.inventory.remove(item)
        return len(items_to_remove)

    def remove_item_from_inventory_or_room(self, item_name: str, count: int = 1) -> int:
        """
        Removes up to 'count' items from the player's inventory first, then from the
        current room if more are needed. Returns the actual number of items removed.
        """
        item_name_lower = item_name.lower()
        removed_count = 0

        # First, try to remove from inventory
        items_to_remove_from_inventory = []
        for item in self.inventory:
            if removed_count >= count:
                break
            if (item.get_name().lower() == item_name_lower or
                item.get_short_name().lower() == item_name_lower):
                items_to_remove_from_inventory.append(item)
                removed_count += 1

        for item in items_to_remove_from_inventory:
            self.inventory.remove(item)

        # If we still need more items, try to remove from current room
        if removed_count < count:
            items_to_remove_from_room = []
            current_room_items = getattr(self.current_room, 'items', [])

            for item in current_room_items:
                if removed_count >= count:
                    break
                if (item.get_name().lower() == item_name_lower or
                    item.get_short_name().lower() == item_name_lower):
                    items_to_remove_from_room.append(item)
                    removed_count += 1

            for item in items_to_remove_from_room:
                self.current_room.items.remove(item)

        return removed_count

    def add_item_to_inventory(self, item_object: "Item", count: int = 1) -> None:
        """Adds an item object to the player's inventory, optionally multiple times."""
        for _ in range(count):
            self.inventory.append(item_object)

    def learn_spell(self, spell_object: Any) -> None:
        """
        Adds a spell object to the player's known spells if not already learned.
        """
        if not self.has_spell(spell_object.name):
            self.known_spells.append(spell_object)

    def has_spell(self, spell_name: str) -> bool:
        """
        Checks if a spell with the given name is in the player's known spells
        (case-insensitive).
        """
        spell_name_lower = spell_name.lower()
        for spell in self.known_spells:
            if spell.name.lower() == spell_name_lower:
                return True
        return False

    def stats(self) -> str:
        """Returns a formatted string summarizing the current game state."""
        lines = [
            f"[bold]Current Room:[/bold] [room_name]{self.current_room.name}[/room_name]",
            "",
            "[bold]Inventory:[/bold]"
        ]
        if self.inventory:
            # Batch items by name for display
            item_counts = {}
            for item in self.inventory:
                item_name = item.get_name()
                if item_name in item_counts:
                    item_counts[item_name] += 1
                else:
                    item_counts[item_name] = 1
            for item_name, count in item_counts.items():
                if count == 1:
                    lines.append(f"- [item_name]{item_name}[/item_name]")
                else:
                    lines.append(f"- [item_name]{count} {item_name}[/item_name]")
        else:
            lines.append("(empty)")
        lines.append("")
        lines.append("[bold]Known Spells:[/bold]")
        if self.known_spells:
            for spell in self.known_spells:
                lines.append(f"- [spell_name]{spell.get_name()}[/spell_name]")
        else:
            lines.append("(none)")
        lines.append("")
        lines.append("[bold]Visited Rooms:[/bold]")
        if self.visited_rooms:
            for room in self.visited_rooms:
                lines.append(f"- [room_name]{room}[/room_name]")
        else:
            lines.append("(none)")
        lines.append("")
        lines.append("[bold]Activated Quests:[/bold]")
        if self.activated_quests:
            for quest in self.activated_quests:
                quest_type = "main" if quest.is_main() else "side"
                lines.append(
                    f"- [quest_name]{quest.name} ({quest_type})[/quest_name]: {quest.description}"
                )
        else:
            lines.append("(none)")
        lines.append("")
        lines.append("[bold]Completed Quests:[/bold]")
        if self.completed_quests:
            for quest in self.completed_quests:
                quest_type = "main" if quest.is_main() else "side"
                lines.append(
                    f"- [quest_name]{quest.name} ({quest_type})[/quest_name]: {quest.completion}"
                )
        else:
            lines.append("(none)")
        return "\n".join(lines)

    def next_activated_quest(self) -> Union['Quest', None]:
        """
        Checks non_activated_quests for the first quest that should be activated (triggered).
        Moves the newly activated quest to activated_quests and returns the quest,
        or None if no new quest was activated.
        """
        for i, quest in enumerate(self.non_activated_quests):
            if quest.check_trigger(self):
                self.activated_quests.append(quest)
                del self.non_activated_quests[i]
                return quest
        return None

    def next_updated_quest(self) -> Union['Quest', None]:
        """
        Checks activated_quests for the first quest that should be updated.
        Returns the quest if found, or None if no quest needs updating.
        """
        for quest in self.activated_quests:
            if quest.check_update(self):
                return quest
        return None

    def next_completed_quest(self) -> Union['Quest', None]:
        """
        Checks activated_quests for the first quest that should be completed.
        Returns the quest if found, or None if no quest needs completing.
        """
        for i, quest in enumerate(self.activated_quests):
            if quest.check_completion(self):
                self.completed_quests.append(quest)
                del self.activated_quests[i]
                return quest
        return None

    def get_room(self, room_name: str) -> Union[Any, None]:
        """
        Returns the room object matching the given room_name (case-insensitive,
        matches against all room names). Returns None if not found.
        """
        for room in self.all_rooms.values():
            if room.name.lower() == room_name.lower():
                return room
        return None

    def get_item(self, item_name: str) -> Union["Item", None]:
        """
        Returns the item object matching the given item_name (case-insensitive),
        searching first in the player's inventory, then in all rooms.
        Returns None if not found.
        """
        # Search inventory
        item_name_lower = item_name.lower()
        for item in self.inventory:
            if ((item.get_name().lower() == item_name_lower) or
                (item.get_short_name().lower() == item_name_lower)):
                return item
        # Search all rooms
        for room in self.all_rooms.values():
            for room_item in getattr(room, 'items', []):
                if (room_item.get_name().lower() == item_name_lower or
                    (room_item.get_short_name().lower() == item_name_lower)):
                    return room_item
        return None

    def get_quest(self, quest_name: str) -> Union[Any, None]:
        """
        Returns the quest object matching the given quest_name (case-insensitive),
        searching in non_activated_quests, activated_quests, and completed_quests.
        Returns None if not found.
        """
        quest_name_lower = quest_name.lower()
        quest_lists = [self.non_activated_quests, self.activated_quests, self.completed_quests]
        for quest_list in quest_lists:
            for quest in quest_list:
                if quest.name.lower() == quest_name_lower:
                    return quest
        return None

    def update_quest(self) -> Union[str, None]:
        """
        Checks activated_quests for the first quest that should update its quest log
        (dynamic quest log updates). Returns a string describing the updated quest,
        or None if no quest log was updated.
        """
        for quest in self.activated_quests:
            if quest.check_update(self):
                quest_type = "main" if quest.is_main() else "side"
                return (
                    f"[quest_name]{quest.name} ({quest_type} quest)[/quest_name]\n\n"
                    f"{quest.description}"
                )
        return None

    def complete_quest(self) -> Union[str, None]:
        """
        Checks activated_quests for the first quest that is now completed.
        Moves the newly completed quest to completed_quests and returns a string
        describing it, or None if no new quest was completed.
        """
        for i, quest in enumerate(self.activated_quests):
            if quest.check_completion(self):
                self.completed_quests.append(quest)
                del self.activated_quests[i]
                quest_type = "main" if quest.is_main() else "side"
                return (
                    f"[quest_name]{quest.name} ({quest_type} quest)[/quest_name]\n\n"
                    f"[dim]{quest.completion}[/dim]"
                )
        return None

    def is_quest_activated(self, quest_name: str) -> bool:
        """Check if a quest with the given name is currently activated"""
        return any(quest.name == quest_name for quest in self.activated_quests)

    def is_quest_completed(self, quest_name: str) -> bool:
        """Check if a quest with the given name is completed"""
        return any(quest.name == quest_name for quest in self.completed_quests)
