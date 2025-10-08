"""Mural item for Tidal Causeway (Act III)."""

from ...engine.GameState import GameState
from ...engine.Item import Item
from .SeaSealedLetter import SeaSealedLetter


class Mural(Item):
    """A weathered mural along a half-drowned arch showing a guardian."""

    def __init__(self) -> None:
        """Initialize the mural with its description."""
        super().__init__(
            name="mural",
            short_name="mural",
            description=(
                "A faded mural paints a guardian bending over a small child. "
                "Salt has softened the colors, but the sigils around them still "
                "glow faintly when the moon hits the stone. The scene feels like "
                "a promise kept against the sea."
            ),
            can_be_carried=False,
        )
        self._letter_found = False

    def examine(self, game_state: GameState) -> str:
        """Examine the mural to reveal hidden secrets or the letter."""
        if self._letter_found:
            return (
                "[event]The mural's quiet scene is whole again: the guardian's "
                "shape holds the child as if the image itself was a tide shield. "
                "Where once a small box was sealed into the paint, empty stone now "
                "shows its place.[/event]"
            )
        # Mark the story flag the first time the letter is revealed
        self._letter_found = True
        game_state.current_room.add_item(SeaSealedLetter())
        return (
            "[event]Fine salt lines run along the mural's base. Pressing the stone, "
            "your hand finds a hollow and a dry scrap falls into your palm. A "
            "[item_name]Sea-Sealed Letter[/item_name] peels free, its ink half-hidden "
            "by varnish made of salt and tide.[/event]"
        )
