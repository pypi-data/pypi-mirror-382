"""EchoStones item for the Stillness Vestibule in Act 3."""
from ...engine.Item import Item
from ...engine.GameState import GameState
from ..Act3StoryFlags import FLAG_ACT3_OATH_OF_STILLNESS_STARTED


class EchoStones(Item):
    """Sacred stones that amplify the resonant chant when blessed."""

    def __init__(self) -> None:
        """Initialize EchoStones as an immovable feature."""
        super().__init__(
            name="echo stones",
            description=(
                "Three weathered stones arranged in a triangle, each one carved "
                "with spiraling channels that catch and hold whispered words."
            ),
            can_be_carried=False,
            short_name="stones",
        )
        self._blessed = False

    def examine(self, game_state: GameState) -> str:
        """Examine the echo stones and start the Oath of Stillness quest."""
        game_state.set_story_flag(FLAG_ACT3_OATH_OF_STILLNESS_STARTED, True)
        return super().examine(game_state)

    def receive_spell(self, spell_name: str, _game_state: GameState) -> str:
        """Handle bless spell cast on the echo stones."""
        if spell_name == "bless" and not self._blessed:
            self._blessed = True
            _game_state.set_story_flag(FLAG_ACT3_OATH_OF_STILLNESS_STARTED, True)
            return (
                "[event]As the blessing flows from your lips, the echo stones awaken "
                "with a resonance that vibrates through your very bones. Tendrils of "
                "silver-white radiance spiral up from their carved channels, each groove "
                "igniting like liquid starlight flowing through ancient runes. The air "
                "itself seems to crystallize around the stones, forming prismatic veils "
                "that shimmer with otherworldly harmonics. A low, ethereal hum fills "
                "the chamber as the stones synchronize their energies, their surfaces "
                "now pulsing with a gentle, sacred luminescence that casts dancing "
                "shadows on the obsidian pools. The mystical conduits glow with "
                "patient anticipation, ready to weave spoken words into the very "
                "fabric of reality. [/event]\n"
                "[success]You sense that these hallowed stones now await "
                "the ancient chant that will complete the ritual and banish the "
                "restless spirits from this sacred place.[/success]"
            )
        elif spell_name == "bless" and self._blessed:
            return "[info]The echo stones are already blessed.[/info]"
        else:
            return f"[failure]The {spell_name} spell has no effect on the echo stones.[/failure]"

    def are_blessed(self) -> bool:
        """Check if the echo stones have been blessed."""
        return self._blessed

    def use_with(self, game_state: GameState, other_item: Item) -> str:
        """Handle using other items with the echo stones."""
        from .ResonantChantRubbings import ResonantChantRubbings

        if isinstance(other_item, ResonantChantRubbings):
            # Delegate to the ResonantChantRubbings' use_with method
            return other_item.use_with(game_state, self)
        else:
            return super().use_with(game_state, other_item)
