"""AncientDragon character for the Dragon's Hall in Act 3."""
from ...engine.Character import Character
from ...engine.GameState import GameState
from ..Act3StoryFlags import (
    FLAG_ACT3_DRAGONS_MEMORY_RECEIVED,
    FLAG_ACT3_DRAGON_OATH_SPOKEN,
    FLAG_ACT3_OATH_SCROLLS_EXAMINED
)


class AncientDragon(Character):
    """The ancient dragon who guards the Dragon's Scale and holds memories."""

    def __init__(self) -> None:
        """Initialize AncientDragon with majestic and wise appearance."""
        super().__init__(
            name="ancient dragon",
            description=(
                "A magnificent dragon of immense age, scales gleaming like polished "
                "obsidian in the ember-light. Ancient wisdom burns in golden eyes "
                "that have witnessed countless ages. Slow breaths stir the air like "
                "distant thunder."
            )
        )

    def talk_to(self, game_state: GameState) -> str:
        """Provide the Dragon's Memory for the storytelling quest."""
        # Check if this is the first conversation
        dialogue = ''
        if not game_state.get_story_flag(FLAG_ACT3_DRAGONS_MEMORY_RECEIVED):
            game_state.set_story_flag(FLAG_ACT3_DRAGONS_MEMORY_RECEIVED, True)
            dialogue = (
                "The dragon's voice resonates through your mind like "
                "distant thunder: [dialogue]'Young one, I remember your parents well. Lyra "
                "and Theron came to me when shadows first stirred. They spoke of "
                "a child who must be hidden from Malakar's sight, protected until "
                "the time of choosing arrived. They forged a ward—not of stone or "
                "steel, but of love itself. This ward yet shields you, woven into "
                "your very being. They did not perish, child. They walk paths "
                "beyond sight, guardians still, waiting for the moment when all "
                "debts are paid and all bonds may be renewed.'[/dialogue]\n\n"
            )
        dialogue = dialogue + (
            "[dialogue]'The memory has been shared,'[/dialogue] the dragon rumbles softly. "
            "[dialogue]'Your path leads forward now, not back. The scale awaits when you "
            "are ready to prove your selflessness.'[/dialogue]"
        )
        return dialogue

    def say_to(self, words: str, game_state: GameState) -> str:
        """Handle saying something to the dragon, particularly oaths."""
        if game_state.get_story_flag(FLAG_ACT3_DRAGONS_MEMORY_RECEIVED) is not True:
            return (
                "The dragon's eyes glint with ancient wisdom. You should probably "
                "listen to what it has to say first."
            )
        if words.lower() == "oath":
            if game_state.get_story_flag(FLAG_ACT3_OATH_SCROLLS_EXAMINED) is not True:
                return (
                    "The dragon's golden eyes narrow slightly. [dialogue]'You "
                    "must first understand the weight of the oath you wish to "
                    "speak. You can not just speak any oath. You must speak one "
                    "that proves your selflessness.'[/dialogue]"
                )
            # Check if the oath has already been spoken
            if game_state.get_story_flag(FLAG_ACT3_DRAGON_OATH_SPOKEN):
                return (
                    "[dialogue]'The oath has been given and accepted,' the dragon "
                    "rumbles. 'The scale is yours to claim.'[/dialogue]"
                )
            else:
                # Accept the oath and make the scale available
                game_state.set_story_flag(FLAG_ACT3_DRAGON_OATH_SPOKEN, True)
                # Import and add the dragon's scale to the current room
                from ..items.DragonsScale import DragonsScale
                dragons_scale = DragonsScale()
                game_state.current_room.add_item(dragons_scale)
                return (
                    "[event]You speak your oath to the ancient dragon, pledging "
                    "your commitment to selflessness and the protection of others. [/event]"
                    "[success]The dragon's golden eyes regard you with ancient wisdom. "
                    "'Your words ring true, young one. The scale is yours to bear. "
                    "May you carry its burden with honor.'[/success]"
                )
        else:
            return (
                "[dialogue]The dragon listens but does not respond to those words. "
                "Perhaps you need to speak a more meaningful pledge.[/dialogue]"
            )
