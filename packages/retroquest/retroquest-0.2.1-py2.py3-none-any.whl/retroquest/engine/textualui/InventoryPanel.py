"""Inventory panel listing carried items with focusable entries for detail popups."""

from textual.containers import VerticalScroll
from textual.widgets import Static

from .Popup import PopupType
from ..theme import apply_theme

class InventoryPanel(VerticalScroll):
    """Scrollable inventory list with keyboard navigation and detail popups."""
    def __init__(self) -> None:
        super().__init__(id="inventory", classes="selectable-list")
        self.tooltip = "Inventory"
        self.can_focus = False

    def update_inventory(self, text: list[tuple[str, str]]) -> None:
        """
        Update the inventory list with new items. Each item is a tuple of
        (item name, description).
        """
        # Remove all existing children
        for child in list(self.children):
            child.remove()

        # Add Inventory header
        header = Static(apply_theme("[bold]Inventory[/bold]"))
        self.mount(header)

        # Create a new Static widget for each element
        if text:
            for item in text:
                # Expect tuple of (itemname, description)
                itemname, description = item
                static_widget = Static(apply_theme(itemname), classes='selectable-item')
                static_widget.can_focus = True
                static_widget.description = description  # Store the description

                self.mount(static_widget)
        else:
            no_items = Static(apply_theme("[dim](none)[/dim]"))
            self.mount(no_items)

    async def on_key(self, event) -> None:  # type: ignore[override]
        """Handle up/down arrow keys for navigation and Enter for popups."""
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
            focusable_items = [child for child in self.children if child.can_focus]
            for item in focusable_items:
                if item.has_focus:
                    item_text = str(item.renderable)
                    self.app.open_popup(item_text, item.description, PopupType.INFO)
                    break
