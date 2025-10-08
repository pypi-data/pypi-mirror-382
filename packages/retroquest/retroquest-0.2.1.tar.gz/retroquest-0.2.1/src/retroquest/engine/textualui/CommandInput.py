"""Command input widget with nested suggestion expansion on Tab."""

from typing import Any
from textual.widgets import Input
from textual.events import Key
from .NestedSuggester import NestedSuggester

class CommandInput(Input):
    """Input widget that supports auto-completion via nested command suggester."""
    def __init__(self, controller: Any) -> None:
        super().__init__(placeholder="Invalid", id="command_input")
        self.controller = controller
        self.tooltip = "Command Input"
        self.suggester = NestedSuggester(self, controller)

    async def on_key(self, event: Key) -> None:  # type: ignore[override]
        """Handle Tab for nested command auto-completion."""
        if event.key == "tab":
            # Check if there's a suggestion available
            suggestion = await self.suggester.get_suggestion(self.value)
            if suggestion is not None:
                # Apply the suggestion and prevent normal submission
                self.value = suggestion
                self.cursor_position = len(suggestion)
                event.prevent_default(True)
                event.stop()
