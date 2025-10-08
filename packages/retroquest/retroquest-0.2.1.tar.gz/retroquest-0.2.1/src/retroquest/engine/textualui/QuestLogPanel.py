"""Quest log panel showing active and completed quests using collapsible entries."""

from typing import Union
from textual.widgets import Collapsible, Static
from textual.containers import VerticalScroll
from ..theme import apply_theme

class QuestLogPanel(VerticalScroll):
    """Scrollable quest log with collapsible sections for details."""
    def __init__(self) -> None:
        super().__init__(id="questlog")
        self.tooltip = "Quest Log"
        self.can_focus = False

    def update_questlog(self, active_quests: list,
                        completed_quests: Union[list, None] = None) -> None:
        """Update the quest log with active and completed quests.

        Args:
            active_quests (list): List of active quests.
            completed_quests (Union[list, None], optional): List of completed quests.
                Defaults to None.
        """
        # Remove all existing children
        for child in list(self.children):
            child.remove()

        # Add Active Quests header
        active_header = Static(apply_theme("[bold]Active Quests[/bold]"))
        self.mount(active_header)

        # Add new Collapsible widgets for each active quest
        if active_quests:
            for quest_name, quest_description in active_quests:
                quest_content = Static(
                    apply_theme(quest_description), classes='quest-description'
                )
                collapsible = Collapsible(
                    quest_content, title=apply_theme(quest_name), classes='quest'
                )
                self.mount(collapsible)
        else:
            no_active = Static(apply_theme("[dim](none)[/dim]"))
            self.mount(no_active)

        # Add Completed Quests header and list
        if completed_quests is not None:
            completed_header = Static(apply_theme("[bold]Completed Quests[/bold]"))
            self.mount(completed_header)

            if completed_quests:
                for quest_name, quest_completion in completed_quests:
                    quest_content = Static(apply_theme(quest_completion))
                    collapsible = Collapsible(
                        quest_content, title=apply_theme(quest_name),
                        classes='quest completed-quest'
                    )
                    self.mount(collapsible)
            else:
                no_completed = Static(apply_theme("[dim](none)[/dim]"))
                self.mount(no_completed)

    async def on_key(self, event) -> None:  # type: ignore[override]
        """
        Handle key events for quest log navigation.
        """
        if event.key in ("down", "up"):
            # Get all Collapsible widgets
            collapsibles = [child for child in self.children if isinstance(child, Collapsible)]

            if not collapsibles:
                return

            # Find currently focused collapsible
            current_focused = None
            for i, collapsible in enumerate(collapsibles):
                if collapsible.has_focus_within:
                    current_focused = i
                    break

            # Move to next/previous collapsible or first/last one if none focused
            if current_focused is not None:
                if event.key == "down":
                    next_index = (current_focused + 1) % len(collapsibles)
                else:  # up key
                    next_index = (current_focused - 1) % len(collapsibles)
            else:
                next_index = 0 if event.key == "down" else len(collapsibles) - 1

            collapsibles[next_index].children[0].focus()
            event.prevent_default()
