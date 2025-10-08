"""Ash Scholar NPC for Mount Ember, offers guidance and holds a mirror segment."""
from ...engine.Character import Character
from ...engine.GameState import GameState
from ..items.BrassMirrorSegment import BrassMirrorSegment


class AshScholar(Character):
    """A scholar who studies mirrorcraft and offers a mirror segment."""

    def __init__(self) -> None:
        """Initialize the Ash Scholar with a brief description."""
        super().__init__(
            name="Ash Scholar",
            description=(
                "A thoughtful figure with soot-streaked robes, carrying notes on "
                "reflective geometry and the craft of mirrors."
            ),
        )
        # Tracks whether this scholar has already given their mirror segment
        self._gave_segment = False

    def talk_to(self, game_state: GameState) -> str:
        """Speak to the scholar to receive advice and possibly a mirror segment."""
        # If the scholar hasn't yet given their segment, give one now.
        # Do NOT check the player's inventory; the scholar's gift is tracked
        # locally so the player may receive duplicates from other sources.
        if not self._gave_segment:
            segment = BrassMirrorSegment()
            game_state.add_item_to_inventory(segment)
            self._gave_segment = True
            return (
                "The scholar straightens and studies you for a long moment before "
                "speaking. "
                "[dialogue]'We are on an expedition — a small band of scholars and "
                "tinkerers tracing the terraces and cataloguing anything that "
                "glints. We comb the fissures for fragments, map the channels, "
                "and bide our time until the sun lines up with the mounts. It was "
                "while prying at a collapsed ledge that I found this brass mirror "
                "segment tucked between cooled slag and soot. It's small, but it "
                "will mend a mount. There are likely more of this sort scattered "
                "among the outcrops — search carefully and you will find them. "
                "Take this; it should help.'[/dialogue]\n"
                f"[event]You receive the [item_name]{segment.get_name()}[/item_name].[/event]"
            )
        return (
            "The scholar offers a small nod. "
            "[dialogue]'The terraces favor steady hands. We're on an expedition "
            "cataloguing glass and shards; seek the outcrops for what the mountain "
            "has shed. When you find fragments, set them carefully—alignment "
            "matters.'[/dialogue]"
        )
