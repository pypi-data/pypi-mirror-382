"""Phoenix: the ancient riddle-giving guardian of Mount Ember's crater."""

from ...engine import GameState, Character
from ..Act3StoryFlags import FLAG_ACT3_PHOENIX_FEATHER_ACQUIRED

class Phoenix(Character):
    """A majestic, telepathic phoenix who poses a riddle to the worthy."""

    def __init__(self) -> None:
        super().__init__(
            name="Phoenix",
            description=(
                "A vast, ember-wrought phoenix reclines amid the crater's molten glass. Its "
                "feathers glow with shifting gold and crimson, and its eyes burn with patient, "
                "ancient wisdom. It radiates a presence that is both fierce and serene, as if it "
                "has seen the rise and fall of ages."
            ),
        )
        self._riddle_posed = False

    def talk_to(self, _game_state=None) -> str:
        """Telepathic riddle from the Phoenix."""
        self._riddle_posed = True
        return (
            "The phoenix's voice does not come from its beak, but resounds within your mind: "
            "[dialogue]'What is wisdom when time is short?'[/dialogue] The question lingers, "
            "bright and weightless, as if the answer might shape the very air around you."
        )

    def say_to(self, words: str, game_state: GameState) -> str:
        """Accepts correct answers and gives the Phoenix Feather if appropriate."""
        # Only accept answer if riddle was posed and feather not yet given
        if not self._riddle_posed:
            return super().say_to(words, game_state)
        if game_state.get_story_flag(FLAG_ACT3_PHOENIX_FEATHER_ACQUIRED):
            return (
                "The phoenix inclines its head, a knowing warmth in its eyes. "
                "[dialogue]'You already hold what you have earned.'[/dialogue]"
            )
        answer = words.strip().lower()
        if any(key in answer for key in ("patience", "calm", "ease")):
            from ..items.PhoenixFeather import PhoenixFeather
            game_state.add_item_to_inventory(PhoenixFeather())
            game_state.set_story_flag(FLAG_ACT3_PHOENIX_FEATHER_ACQUIRED, True)
            return (
                "The phoenix's eyes flare with approval. It plucks a single glowing feather and "
                "offers it to you. [dialogue]'Wisdom is patience, even when the world burns. Take "
                "this, and remember.'[/dialogue]"
            )
        return (
            "The phoenix studies you in silence. [dialogue]'Is that truly wisdom, when time is "
            "short?'[/dialogue]"
        )
