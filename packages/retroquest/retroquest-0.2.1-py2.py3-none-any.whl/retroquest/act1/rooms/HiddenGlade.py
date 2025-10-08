"""Hidden Glade room: enchanted clearing with conditional fauna and spell gain."""

from ...engine.Room import Room
from ...engine.GameState import GameState
from ..items.RareFlower import RareFlower
from ..items.ShinyPebble import ShinyPebble
from ..characters.Deer import Deer
from ..spells.GrowSpell import GrowSpell

class HiddenGlade(Room):
    """Stateful enchanted clearing featuring conditional spawn and spell teaching.

    Narrative Role:
        Optional discovery zone blending environment ambience with first nature-aligned
        spell acquisition (``Grow``) and conditional wildlife appearance.

    Key Mechanics:
        - ``rest()``: If story flag ``'deer_can_be_observed'`` set and deer absent,
          spawns ``Deer`` + ``RareFlower``.
        - ``light()``: Grants ``Grow`` if not known; toggles internal illumination
          state altering description tone.
        - ``describe()`` rebuilds description from dynamic segments each call.

    Story Flags:
        - Reads: ``'deer_can_be_observed'`` (string literal—candidate for constant).
        - Sets: None locally.

    Contents:
        - Items: ``ShinyPebble``; conditional ``RareFlower``.
        - NPC: Conditional ``Deer``.
        - Spell: ``Grow`` via illumination event.

    Design Notes:
        Future refactor: unify dynamic description pattern across similar rooms.
    """
    def __init__(self) -> None:
        """Initialize the Hidden Glade and its initial state for spells and fauna."""
        super().__init__(
            name="Hidden Glade",
            description=(
                "A peaceful clearing bathed in golden sunlight, hidden deep within the forest. "
                "Wildflowers carpet the ground, and a gentle breeze stirs the tall grass. In the "
                "center, a mossy stone bears a faint, magical inscription. The glade feels "
                "enchanted, a place where the world holds its breath."
            ),
            items=[ShinyPebble()],
            characters=[],
            exits={"north": "ForestPath", "south": "VillageChapel"}
        )
        self.light_spell_cast = False  # Track if the light spell has been cast

    def get_room_text_description(self) -> str:
        """Build and return the dynamic base description for the glade."""
        base_description = (
            "A peaceful clearing bathed in golden sunlight, hidden deep within the forest. "
            "Wildflowers carpet the ground, and a gentle breeze stirs the tall grass. In the "
            "center, a mossy stone bears a faint, magical inscription."
        )
        # Add darkness hint if light spell has not been cast
        if not self.light_spell_cast:
            base_description += (
                " Yet, an unnatural darkness lingers here, as if the glade itself is waiting "
                "to be enlightened."
            )
        dynamic_parts = []
        if self.get_character_by_name("Deer"):
            dynamic_parts.append(
                "A graceful [character_name]Deer[/character_name] grazes quietly, occasionally "
                "lifting its head to watch you with wise, gentle eyes."
            )
            # Check if flower is still in the room's items
            if any(isinstance(item, RareFlower) for item in self.items):
                dynamic_parts.append(
                    "A beautiful [item_name]Rare Flower[/item_name] blooms near the mossy stone."
                )
            else:
                dynamic_parts.append(
                    "You recall picking a beautiful [item_name]Rare Flower[/item_name] that once "
                    "bloomed near the mossy stone."
                )
        if not dynamic_parts and not self.get_character_by_name("Deer"):
            base_description += (
                " The glade feels quiet and expectant, as if waiting for something."
            )
        description = base_description
        if dynamic_parts:
            description += " " + " ".join(dynamic_parts)
        description += " The glade feels enchanted, a place where the world holds its breath."
        return description

    def rest(self, game_state: GameState) -> str:
        if game_state.get_story_flag("deer_can_be_observed"):
            messages = ["You take a moment to rest in the tranquil glade."]
            if not self.get_character_by_name("Deer"):
                deer = Deer()
                self.add_character(deer)
                messages.append(
                    "As you relax, a graceful [character_name]Deer[/character_name] emerges into "
                    "the glade. It gazes at you with deep, ancient eyes, and for a moment, "
                    "you feel a surge of gentle magical energy flow through your body, as if "
                    "the glade itself is welcoming you."
                )
                self.add_item(RareFlower())
                messages.append(
                    "You notice a rare, beautiful [item_name]Rare Flower[/item_name] blooming "
                    "near the mossy stone."
                )
            else:
                messages.append(
                    "The [character_name]Deer[/character_name] continues to graze "
                    "peacefully."
                )

            return " ".join(messages)
        else:
            return (
                "You rest for a while, but the glade remains quiet. Perhaps something more needs "
                "to happen for its magic to awaken."
            )

    def describe(self, game_state: GameState) -> str:
        self.description = self.get_room_text_description()
        return super().describe(game_state)

    def light(self, game_state: GameState) -> str:
        """Called when a light source is used or a light spell is cast in the room."""
        self.light_spell_cast = True
        message = (
            "[event]You cast a [spell_name]light[/spell_name] spell that illuminates the "
            "glade.[/event]\n"
            "The inscription on the mossy stone glows faintly, revealing ancient runes. "
            "They speak of a seed, a song, and the sun's embrace to awaken life."
        )
        if not game_state.has_spell("Grow"):
            grow_spell = GrowSpell()
            game_state.learn_spell(grow_spell)
            message += (
                "\nAs you read the runes, you feel a connection to the ancient magic of nature. "
                "You have learned the [spell_name]grow[/spell_name] spell!"
            )
        return message
