"""Act I navigation aid item: Map.

Narrative Role:
    Provides an in-world justification for the player's growing spatial awareness and serves
    as the catalyst for concluding Act I when consulted at the correct location.

Key Mechanics / Interactions:
    - Basic ``use`` returns a flavorful study message (non-consumable).
    - Using the map while in the "Road to Greendale" room triggers the act completion flag
      (``FLAG_SHADOWS_OVER_WILLOWBROOK_COMPLETED``), representing Elior confidently charting the
      onward journey.

Story Flags (Sets):
    - ``FLAG_SHADOWS_OVER_WILLOWBROOK_COMPLETED`` (when used in the correct room)

Story Flags (Reads):
    (none) – the item only evaluates the current room name.

Progression Effects:
    Unlocks transition to Act II once the player has naturally reached the outward road and
    intentionally examined their map, tying exploration to narrative readiness.

Design Notes:
    - Keeps logic intentionally lightweight; expansion hooks exist for revealing dynamic exits
      or marking discovered landmarks later.
    - Room name comparison is case-insensitive via ``lower()`` to avoid brittle matching.
"""

from ...engine.Item import Item
from ...engine.GameState import GameState
from ..Act1StoryFlags import FLAG_SHADOWS_OVER_WILLOWBROOK_COMPLETED


class Map(Item):
    """Player-held world map enabling Act I completion in the correct context.

    The map is a persistent utility item. Outside the designated progression gateway room it
    simply returns a descriptive study message. When used in the "Road to Greendale" room it
    sets the act completion flag, signaling that narrative and exploratory prerequisites have
    been satisfied.

    Methods:
        use(game_state): Returns a contextual description; may set act completion flag.
    """
    def __init__(self) -> None:
        super().__init__(
            name="map",
            description=(
                "A detailed map of Willowbrook and the surrounding areas. It shows various "
                "landmarks and paths, some of which are not immediately obvious."
            ),
            can_be_carried=True,
        )

    def use(self, game_state: GameState) -> str:
        # In a real scenario, this might change game state or reveal new exits.
        # For now, it just returns a descriptive message.
        if game_state.current_room.name.lower() == "road to greendale":
            # This is the specific check for completing Act I as per RoomsAct1.md
            game_state.set_story_flag(FLAG_SHADOWS_OVER_WILLOWBROOK_COMPLETED, True)
            return (
                f"[event]You use the [item_name]{self.get_name()}[/item_name].[/event]\n"
                f"The [item_name]{self.get_name()}[/item_name] aligns with the landscape,"
                f" revealing a "
                f"hidden path that shortens the journey to Greendale. You feel a sense of "
                f"accomplishment as you set forth."
            )
        return (
            f"[event]You study the [item_name]{self.get_name()}[/item_name]. It depicts the "
            f"local area with surprising detail.[/event]"
        )
