"""Panel presenting latest command result text with theming and scrolling."""

from textual.widgets import Static
from textual.containers import ScrollableContainer
from ..theme import apply_theme

class ResultPanel(ScrollableContainer):
    """Scrollable container for the most recent command output."""
    def __init__(self) -> None:
        super().__init__(classes="result", can_focus=False)
        self.tooltip = "Command Result"
        self.content_widget = Static("", classes='room-text', markup=True)
        self.content_widget.can_focus = True

    def on_mount(self) -> None:  # type: ignore[override]
        """Mount the inner static when the panel is added to the DOM."""
        self.mount(self.content_widget)

    def update_result(self, text: str) -> None:
        """Update with new themed result text."""
        self.content_widget.update(apply_theme(text))
