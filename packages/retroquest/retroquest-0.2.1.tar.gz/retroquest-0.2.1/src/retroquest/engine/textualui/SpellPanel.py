"""Spell panel listing known spells with keyboard navigation and detail popups."""

from textual.containers import VerticalScroll
from textual.widgets import Static

from .Popup import PopupType
from ..theme import apply_theme

class SpellPanel(VerticalScroll):
    """Scrollable list of spells with popup detail on selection."""
    def __init__(self) -> None:
        super().__init__(id="spells", classes="selectable-list")
        self.tooltip = "Spell List"
        self.can_focus = False

    def update_spells(self, text: list[tuple[str, str]]) -> None:
        """Update the spell list with new spells."""
        # Remove all existing children
        for child in list(self.children):
            child.remove()

        # Add Spells header
        header = Static(apply_theme("[bold]Spells[/bold]"))
        self.mount(header)

        # Create a new Static widget for each element
        if text:
            for spell in text:
                static_widget = Static(apply_theme(spell[0]), classes='selectable-item')
                static_widget.can_focus = True
                static_widget.description = spell[1]  # Store the description

                self.mount(static_widget)
        else:
            no_spells = Static(apply_theme("[dim](none)[/dim]"))
            self.mount(no_spells)

    async def on_key(self, event) -> None:  # type: ignore[override]
        """Handle up/down arrow keys for navigation and Enter for popup details."""
        if event.key in ("down", "up"):
            # Get all focusable Static widgets (selectable items)
            focusable_items = [child for child in self.children if child.can_focus]

            if not focusable_items:
                return

            # Find currently focused item
            current_focused = None
            for i, item in enumerate(focusable_items):
                if item.has_focus:
                    current_focused = i
                    break

            # Move to next/previous item or first/last one if none focused
            if current_focused is not None:
                if event.key == "down":
                    next_index = (current_focused + 1) % len(focusable_items)
                else:  # up key
                    next_index = (current_focused - 1) % len(focusable_items)
            else:
                next_index = 0 if event.key == "down" else len(focusable_items) - 1

            focusable_items[next_index].focus()
            event.prevent_default()
        elif event.key == "enter":
            # Get all focusable Static widgets (selectable items)
            focusable_items = [child for child in self.children if child.can_focus]

            # Find currently focused item
            for item in focusable_items:
                if item.has_focus:
                    # Extract spell name from the rendered text
                    spell_text = str(item.renderable)
                    # Use the spell's stored description
                    self.app.open_popup(spell_text, item.description, PopupType.INFO)
                    break
