"""Warding Pillars item for Act III."""

from ...engine.GameState import GameState
from ...engine.Item import Item
from ..Act3StoryFlags import (
    FLAG_ACT3_TIDEWARD_SIGILS_COMPLETED,
    FLAG_ACT3_WARDING_PILLARS_PURIFIED,
)

class WardingPillars(Item):
    """Tideward ritual pillars requiring purification (Act III).

    Narrative Role:
        Environmental anchor for sigil completion; demonstrates interaction between spell
        effects and quest progression.

    Key Mechanics:
        `purify()` method transitions state, affecting examine text and enabling downstream
        interactions.
    """
    def __init__(self) -> None:
        """Initialize Warding Pillars with description and purified state."""
        super().__init__(
            name="Warding Pillars",
            description=(
                "Three weathered pillars ring a drowned courtyard; glyph-lines are "
                "clogged with brine and coral crust that must be cleared to restore "
                "their ward function."
            ),
            short_name="Pillars",
            can_be_carried=False,
        )
        self.purified: bool = False

    def prevent_pickup(self) -> str:
        """Prevent pickup of the immovable warding pillars."""
        return (
            f"[failure]You can't take the [item_name]{self.get_name()}[/item_name]. "
            "They are fixed stone, older than the pier.[/failure]"
        )

    def examine(self, _game_state: GameState) -> str:
        """Examine the warding pillars showing their current purification state."""
        # Return completely different strings depending on purification state.
        if self.purified:
            # Pulsating, radiant description when purified.
            return (
                "[event]The pillars pulse with a quiet, radiant rhythm. Light seems to "
                "gather in the carved channels, a steady heartbeat that draws the tide "
                "toward the stone. The air tastes of moonwater; the ward answers, ready "
                "to pull the sea back when the sigil is set.[/event]"
            )

        # Dark, faint-hum description when not purified.
        return (
            "[event]The pillars stand mute in the dim, their faces ringed with crust and "
            "shadow. A faint, weary hum hides under the stone, a thread of old magic "
            "barely holding. They watch the water but do not command it.[/event]"
        )

    def purify(self, game_state: GameState) -> str:
        """Purify the pillars, enabling their use in the Tideward Sigil quest."""
        if self.purified:
            return "[info]The pillars are already cleansed of brine and coral.[/info]"
        self.purified = True
        # Update the item's displayed name to reflect purified state.
        self.name = "Warding Pillars (purified)"
        # Mark purification story flag so other systems can react to the change.
        game_state.set_story_flag(FLAG_ACT3_WARDING_PILLARS_PURIFIED, True)
        return (
            "[event]You rinse salt and scrape coral from the carved channels. Glyph-lines "
            "breathe again, ready to take the Tideward Sigil.[/event]"
        )

    def use_with(self, game_state: GameState, other_item: 'Item') -> str:
        """Handle being used together with another item.

        If `other_item` is Moon Rune Shards (by name/short name), attempt to engrave
        the pillars. This follows the same rules as the previous `engrave()` helper:
        pillars must be purified and the player must have shards in inventory. The
        shards are consumed and the attuned flag is set.
        """
        # Use isinstance to check for MoonRuneShards without circular import.
        from .MoonRuneShards import MoonRuneShards
        if not isinstance(other_item, MoonRuneShards):
            return super().use_with(game_state, other_item)

        # Now handle engraving flow
        if not self.purified:
            return (
                "[failure]The carved channels are still clogged with crust. The shards "
                "will not take until the pillars are cleansed.[/failure]"
            )

        # Consume shards (remove all matching entries) and set story flag
        game_state.remove_item_from_inventory(other_item.name)
        game_state.set_story_flag(FLAG_ACT3_TIDEWARD_SIGILS_COMPLETED, True)
        return (
            "[event]You press the pale shards into the cleansed grooves. Pale runes "
            "flare and sink into the stone like stored moonlight. The air leans in; "
            "a subtle pull runs through the courtyard as the tide answers the sigils, "
            "drawing the sea closer to the pillars.[/event]"
        )
