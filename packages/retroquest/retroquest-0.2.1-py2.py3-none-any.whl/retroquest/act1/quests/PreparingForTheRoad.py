from ...engine.Quest import Quest
from ...engine.GameState import GameState
from ..Act1StoryFlags import FLAG_MAGIC_FULLY_UNLOCKED, FLAG_JOURNEY_BLESS_COMPLETED

class PreparingForTheRoadQuest(Quest):
    def __init__(self) -> None:
        super().__init__(
            name="Preparing for the road",
            description=(
                "Mira has tasked you with preparing for your journey. She says you will need: \n"
                " - Warm clothing -\n"
                " - Magical protection -\n"
                " - Food for the road (at least four different types) -\n"
                " - Sturdy footwear -\n"
                " - A map to find your way, and to have learned all the basic magic the village elders can teach you -\n"
                " - To have learned all the basic magic the village elders can teach you -\n"
            ),
            completion="You have gathered all the items needed for your journey. With your preparations complete, you are ready to face whatever lies beyond Willowbrook."
        )

    def check_trigger(self, game_state: GameState) -> bool:
        return game_state.get_story_flag(FLAG_MAGIC_FULLY_UNLOCKED)

    def check_completion(self, game_state: GameState) -> bool:
        # Items
        self.has_travel_cloak = game_state.has_item("travel cloak")
        # Food items
        has_wild_berries = game_state.has_item("wild berries")
        has_apple = game_state.has_item("apple")
        has_egg = game_state.has_item("egg")
        has_carrot = game_state.has_item("fresh carrot")
        self.all_food_collected = has_wild_berries and has_apple and has_egg and has_carrot

        self.has_wandering_boots = game_state.has_item("wandering boots")
        self.has_map = game_state.has_item("map")

        # Spells
        required_spells = ["revive", "purify", "bless", "heal", "unlock", "light", "grow"]
        self.knows_all_spells = all(game_state.has_spell(spell_name) for spell_name in required_spells)

        # Action: Bless cast for journey (assuming this flag is set elsewhere when player casts bless on self)
        self.journey_bless_completed = game_state.get_story_flag(FLAG_JOURNEY_BLESS_COMPLETED)

        self.description = ["Mira has tasked you with preparing for your journey. She says you will need: \n"]
        requirements = [
            (" * Warm clothing", self.has_travel_cloak),
            (" * Magical protection", self.journey_bless_completed),
            (" * Food for the road (at least four different types)", self.all_food_collected),
            (" * Sturdy footwear", self.has_wandering_boots),
            (" * A map to find your way", self.has_map),
            (" * All basic magic learned", self.knows_all_spells),
        ]
        for req, completed in requirements:
            if completed:
                self.description.append(f"[success]{req}[/success]")
            else:
                self.description.append(f"[failure]{req}[/failure]")
        self.description = "\n".join(self.description)

        return (self.has_travel_cloak and self.all_food_collected and self.has_wandering_boots and self.has_map and
                self.knows_all_spells and self.journey_bless_completed)
