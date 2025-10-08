"""Panel rendering current room description with adaptive width formatting."""

from textual.widgets import Static
from textual.containers import ScrollableContainer
from ..theme import apply_theme

class RoomPanel(ScrollableContainer):
    """Scrollable container for current room narrative text."""
    def __init__(self) -> None:
        super().__init__(classes="room", can_focus=False)
        self.tooltip = "Current Room Description"
        self.content_widget = Static("", classes='room-text', markup=True)
        self.content_widget.can_focus = True

    def on_mount(self) -> None:  # type: ignore[override]
        """Mount the inner static when the panel is added to the DOM."""
        self.mount(self.content_widget)

    def update_room(self, text: str, wide: bool = False) -> None:
        """Update with new themed room description.

        wide: When True apply alternate style class for logo / center formatting.
        """
        self.content_widget.classes = 'room-text room-text-wide' if wide else 'room-text'
        self.content_widget.update(apply_theme(text))
