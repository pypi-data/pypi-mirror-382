"""Bridge between core game logic and Textual UI panels/state queries."""

from typing import Optional, List, Tuple
from ..Game import Game
from ..theme import apply_theme

class GameController:
    """Controller adapting engine operations for presentation in the Textual UI.

    Responsibilities:
        * Provide formatted / themed text for panels (room, result, quests, inventory).
        * Surface quest activation / update / completion events as popup payloads.
        * Delegate raw command strings to the command parser and retain last output.

    Design Notes:
        Kept intentionally thin; avoids UI dependencies so it can be reused by other
        front ends in future (e.g., web or curses). Popup generation returns optional
        strings instead of side‑effects, enabling the UI layer to decide sequencing.
    """

    def __init__(self, game: Game) -> None:
        self.game = game
        self.last_output = ""

    def start(self) -> str:
        """Return initial game / act intro text for first render."""
        return self.game.get_result_text()

    def handle_command(self, command: str) -> str:
        """Parse and execute a player command returning formatted result text."""
        output = self.game.command_parser.parse(command)
        self.last_output = output
        return output

    def get_output(self) -> str:
        """Return last command result (already themed when fetched via look/room)."""
        return self.last_output

    def get_active_quests(self) -> List[Tuple[str, str]]:
        """Return themed tuples: (quest_name_with_type, quest_description)."""
        quest_tuples: List[Tuple[str, str]] = []
        for quest in self.game.state.activated_quests:
            quest_type = "main" if quest.is_main() else "side"
            quest_name = f"[quest_name]{quest.name} ({quest_type})[/quest_name]"
            quest_tuples.append((quest_name, quest.description))
        return quest_tuples

    def get_completed_quests(self) -> List[Tuple[str, str]]:
        """Return themed tuples: (quest_name_with_type, completion_text)."""
        quest_tuples: List[Tuple[str, str]] = []
        for quest in self.game.state.completed_quests:
            quest_type = "main" if quest.is_main() else "side"
            quest_name = f"[quest_name]{quest.name} ({quest_type})[/quest_name]"
            completion_text = f"[dim]{quest.completion}[/dim]"
            quest_tuples.append((quest_name, completion_text))
        return quest_tuples

    def get_inventory(self) -> List[Tuple[str, str]]:
        """Return themed tuples: (possibly counted_item_name, item_description)."""
        item_tuples: List[Tuple[str, str]] = []
        inventory_summary = self.game.state.get_inventory_summary()

        # Create a set to track which items we've already processed
        processed_items = set()

        for item in self.game.state.inventory:
            item_name = item.get_name()
            if item_name in processed_items:
                continue  # Skip duplicates, we already processed this item type

            count = inventory_summary[item_name]
            if count > 1:
                styled_item_name = f"[item_name]{count} {item_name}[/item_name]"
            else:
                styled_item_name = f"[item_name]{item_name}[/item_name]"
            item_description = item.description
            item_tuples.append((styled_item_name, item_description))
            processed_items.add(item_name)

        return item_tuples

    def get_room(self) -> str:
        """Return themed current room description (includes exits/items/characters)."""
        return apply_theme(self.game.state.current_room.describe(self.game.state))

    def get_spells(self) -> List[Tuple[str, str]]:
        """Return themed tuples: (spell_name, description) for known spells."""
        spell_tuples: List[Tuple[str, str]] = []
        for spell in self.game.state.known_spells:
            spell_name = f"[spell_name]{spell.get_name()}[/spell_name]"
            spell_description = spell.description
            spell_tuples.append((spell_name, spell_description))
        return spell_tuples

    def save_game(self) -> None:
        """Save the game state."""
        self.game.save()

    def get_act_intro(self) -> str:
        """Get the act introduction text."""
        return self.game.get_act_intro()

    def look(self) -> str:
        """Execute the look command and return result."""
        return self.game.look()

    def complete_quest(self) -> Optional[str]:
        """Return completion popup payload if a quest just completed else None."""
        if (quest := self.game.state.next_completed_quest()) is not None:
            quest_type = "main" if quest.is_main() else "side"
            return (
                f"[quest_name]{quest.name} ({quest_type} quest)"\
                f"[/quest_name]\n\n{quest.completion}"
            )
        return None

    def update_quest(self) -> Optional[str]:
        """Return update popup payload if a quest just updated else None."""
        if (quest := self.game.state.next_updated_quest()) is not None:
            quest_type = "main" if quest.is_main() else "side"
            return (
                f"[quest_name]{quest.name} ({quest_type} quest)"\
                f"[/quest_name]\n\n{quest.description}"
            )
        return None

    def activate_quest(self) -> Optional[str]:
        """Return activation popup payload if a quest just activated else None."""
        if not self.game.is_act_running():
            return None
        if (quest := self.game.state.next_activated_quest()) is not None:
            quest_type = "main" if quest.is_main() else "side"
            return (
                f"[quest_name]{quest.name} ({quest_type} quest)"\
                f"[/quest_name]\n\n{quest.description}"
            )
        return None

    def play_soundeffect(self, filename: str) -> None:
        """Play a sound effect using the underlying Game's play_soundeffect method."""
        self.game.play_soundeffect(filename)
