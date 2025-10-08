"""Mira character for Act 3."""

from ...engine.Character import Character
from ...engine.GameState import GameState
from ..Act3StoryFlags import (
    FLAG_ACT3_MAIN_STARTED,
    FLAG_ACT3_CRYSTAL_OF_LIGHT_ACQUIRED,
    FLAG_ACT3_PHOENIX_FEATHER_ACQUIRED,
    FLAG_ACT3_DRAGONS_SCALE_ACQUIRED,
    FLAG_ACT3_LIFELIGHT_ELIXIR_CREATED,
    FLAG_ACT3_SEA_SEALED_LETTER_READ,
    FLAG_ACT3_CHARRED_INSCRIPTION_READ,
)


class Mira(Character):
    """Act III version of Mira: starts the main quest and handles teleportation between
    sites."""

    def __init__(self) -> None:
        """Initialize Mira with description."""
        super().__init__(
            name="Mira",
            description=(
                "The village healer returns with renewed purpose. Her eyes shine "
                "with resolve as she speaks of the three relics needed to confront "
                "Malakar."
            ),
        )

    def talk_to(self, game_state: GameState) -> str:
        """Handle conversation with Mira, including quest start and teleportation."""
        event_msg = (
            f"[event]You speak with [character_name]{self.name}[/character_name]."
            "[/event]"
        )

        # First conversation in Act III: start the main quest
        if not game_state.get_story_flag(FLAG_ACT3_MAIN_STARTED):
            game_state.set_story_flag(FLAG_ACT3_MAIN_STARTED, True)

            # Give Elior the Keepsake Note
            from ..items.KeepsakeNote import KeepsakeNote
            keepsake_note = KeepsakeNote()
            game_state.inventory.append(keepsake_note)

            return (
                event_msg
                + "\n"
                + (
                    "[dialogue]'Elior, the weave bends and the hourglass shivers. "
                    "Threads of fate tighten about us.'[/dialogue]\n"
                    "[dialogue]'Malakar drains King Alden to unbind Eldoria's wards. "
                    "We will not reach him unscathed without protection.'[/dialogue]\n"
                    "[dialogue]'To walk the last road, you must embody three virtues—"
                    "Courage, Wisdom, and Selflessness—and three relics must be won to "
                    "counter his working and shield you from his influence: the Crystal "
                    "of Light from the Sunken Ruins, the Phoenix Feather from Mount "
                    "Ember, and the Dragon's Scale from the Caverns of "
                    "Shadow.'[/dialogue]\n"
                    "[dialogue]'Listen to what the tide whispers, what embers teach, "
                    "and what the deep stone remembers.'[/dialogue]\n"
                    "[dialogue]'The Crystal will part veils and steady your spirit; "
                    "the Feather will awaken guiding fire and clarity; the Scale will "
                    "turn aside shadow and bind your oath.'[/dialogue]\n"
                    "[dialogue]'We will travel by my focus. I will anchor circles at "
                    "the edges of each site: first the Tidal Causeway of the Sunken "
                    "Ruins, then the Lower Switchbacks on Mount Ember, and finally the "
                    "Cavern Mouth of the shadowed halls.'[/dialogue]\n"
                    "[dialogue]'Before we depart, take this note. It contains guidance "
                    "about traces of the past you may find on your journey.'[/dialogue]\n"
                    "[event]Mira hands you a small, worn piece of parchment.[/event]\n"
                    "[dialogue]'When all three are gathered, I will set our last "
                    "circle at the fortress gate. Say the word, and I will draw the "
                    "first circle—where moonlight marries the sea.'[/dialogue]"
                )
            )

        destination_key = ""
        flavor = ""
        # Subsequent conversation: teleport onward based on current location.
        # Special-case: if we're at the Tidal Causeway, hint about the relic
        # unless the Crystal of Light has been acquired. If acquired, Mira can
        # draw the circle onward to Mount Ember.
        # If we're already at Lower Switchbacks, do not teleport; instead
        # provide lore about the second virtue and the phoenix legend.
        # Special dialogue for Cavern Mouth
        if game_state.current_room.name == "Entrance to Malakar's Fortress":
            return (
                event_msg
                + "\n"
                + (
                    "[dialogue]'The journey has taken its toll on me, Elior. The magic "
                    "required to transport us here has drained much of my strength.'[/dialogue]\n"
                    "[dialogue]'I must rest and recover while you and Sir Cedric press "
                    "forward into the fortress. The fate of the kingdom now rests in "
                    "your capable hands.'[/dialogue]\n"
                    "[dialogue]'Go with courage, wisdom, and selflessness—the three "
                    "virtues you have proven. The Lifelight Elixir will guide you to "
                    "victory. I will await your return.'[/dialogue]"
                )
            )
        elif game_state.current_room.name == "Cavern Mouth":
            # Check if dragon's scale has been acquired
            if not game_state.get_story_flag(FLAG_ACT3_DRAGONS_SCALE_ACQUIRED):
                return (
                    event_msg
                    + "\n"
                    + (
                        "[dialogue]'The shadows here run deep, Elior. The miners' plight is a "
                        "test of selflessness—lend your strength, and the path to the dragon "
                        "will open. "
                        "When you are ready, I can draw the next circle, but the caverns will "
                        "not yield their heart until all are safe.'[/dialogue]"
                    )
                )
            destination_key = "MirasHut"
            flavor = (
                "[dialogue]'The three relics are yours, Elior. The dragon's "
                "wisdom runs deep—its scale will turn aside shadow and bind "
                "your oath. Let us return to my hut where we can combine their "
                "power into something that can save the king.'[/dialogue]"
            )
        elif game_state.current_room.name == "Lower Switchbacks":
            if not game_state.get_story_flag(
                FLAG_ACT3_PHOENIX_FEATHER_ACQUIRED
            ):
                return (
                    event_msg
                    + "\n"
                    + (
                        "[dialogue]'There the second virtue, Wisdom, is taught in "
                        "embers. Old guides here tell of a phoenix that nested where "
                        "the rock blooms with heat — a bird of returning flame. From "
                        "its ash a single feather rises renewed, and such a feather "
                        "is said to clear the eyes and steady a wavering hand. "
                        "Listen for songs on the wind, and tend any sparks you find; "
                        "they may be more than mere kindle.'[/dialogue]"
                    )
                )

            # Check if Charred Inscription has been read before proceeding to Cavern Mouth
            if not game_state.get_story_flag(FLAG_ACT3_CHARRED_INSCRIPTION_READ):
                return (
                    event_msg
                    + "\n"
                    + (
                        "[dialogue]'Before we descend into shadow, Elior, you must "
                        "discover the words your parents left burned into stone upon "
                        "these ember heights. Their message will guide you through "
                        "the darkness ahead.'[/dialogue]"
                    )
                )

            destination_key = "CavernMouth"
            flavor = (
                "[dialogue]'You have done well, Elior. The Phoenix Feather is a "
                "token of wisdom; it will guide you through darkness and flame. "
                "Ahead lies the Cavern Mouth—gaping stone jaws that breathe cold "
                "and shadow. Steel your heart and hold your light high.'[/dialogue]"
            )
        elif game_state.current_room.name == "Tidal Causeway":
            if not game_state.get_story_flag(
                FLAG_ACT3_CRYSTAL_OF_LIGHT_ACQUIRED
            ):
                return (
                    event_msg
                    + "\n"
                    + (
                        "[dialogue]'This place keeps its secrets in salt and song. "
                        "Within the Sunken Ruins lies the Crystal of Light—an old "
                        "relic that answers to courage. When you stand before the "
                        "tide-born guardian, speak your vow and let it steady you.'"
                        "[/dialogue]"
                    )
                )

            # Check if Sea-Sealed Letter has been read before proceeding to Lower Switchback
            if not game_state.get_story_flag(FLAG_ACT3_SEA_SEALED_LETTER_READ):
                return (
                    event_msg
                    + "\n"
                    + (
                        "[dialogue]'Before we venture into the shadowed depths, Elior, "
                        "you should seek the traces your parents left behind in the "
                        "sunken ruins. Their story will give you strength for what "
                        "lies ahead in the caverns.'[/dialogue]"
                    )
                )

            destination_key = "LowerSwitchbacks"
            flavor = (
                "[dialogue]'Well done, Elior. The Crystal answers to courage; you "
                "have steadied the tide. Ahead lies the Lower Switchbacks—ridges "
                "of ember and knife-rolled stone where ash chokes the air and the "
                "path winds like a fever dream. Keep your footing and watch the "
                "skies for falling cinders.'[/dialogue]"
            )
        elif game_state.current_room.name == "Mira's Hut":
            # Check if Elior has read the Keepsake Note first
            from ..Act3StoryFlags import FLAG_ACT3_ECHOES_QUEST_STARTED
            if not game_state.get_story_flag(FLAG_ACT3_ECHOES_QUEST_STARTED):
                return (
                    event_msg
                    + "\n"
                    + (
                        "[dialogue]'Before we proceed, Elior, you should read the note "
                        "I gave you. It contains important guidance about your journey "
                        "that you may find... enlightening.'[/dialogue]"
                    )
                )

            # Check if all three relics have been gathered
            all_relics_gathered = (
                game_state.get_story_flag(FLAG_ACT3_CRYSTAL_OF_LIGHT_ACQUIRED) and
                game_state.get_story_flag(FLAG_ACT3_PHOENIX_FEATHER_ACQUIRED) and
                game_state.get_story_flag(FLAG_ACT3_DRAGONS_SCALE_ACQUIRED)
            )
            if all_relics_gathered and not game_state.get_story_flag(
                FLAG_ACT3_LIFELIGHT_ELIXIR_CREATED
            ):
                # Step 28: Perform the Warding Rite to create Lifelight Elixir
                game_state.set_story_flag(FLAG_ACT3_LIFELIGHT_ELIXIR_CREATED, True)

                # Remove the three virtue relics from inventory/room
                game_state.remove_item_from_inventory_or_room("Crystal of Light", 1)
                game_state.remove_item_from_inventory_or_room("Phoenix Feather", 1)
                game_state.remove_item_from_inventory_or_room("Dragon's Scale", 1)

                # Add Lifelight Elixir to the room for pickup
                from ..items.LifelightElixir import LifelightElixir
                lifelight_elixir = LifelightElixir()
                game_state.current_room.add_item(lifelight_elixir)
                return (
                    event_msg
                    + "\n"
                    + (
                        "[dialogue]'The three relics resonate with ancient power, "
                        "Elior. The Crystal of Light, the Phoenix Feather, and the "
                        "Dragon's Scale—courage, wisdom, and selflessness made "
                        "manifest.'[/dialogue]\n"
                        "[event]Mira carefully arranges the three relics in a precise "
                        "triangle. She begins an intricate ritual, weaving threads of "
                        "starlight around each relic. The Crystal flares with brilliant "
                        "light, the Feather ignites with phoenix fire, and the Scale "
                        "hums with draconic power.[/event]\n"
                        "[dialogue]'By light and flame and ancient oath, let these "
                        "virtues merge into one vessel of protection!'[/dialogue]\n"
                        "[event]The three relics dissolve into streams of pure essence "
                        "that spiral together into a crystalline vial. The resulting "
                        "elixir shimmers with liquid starlight—the Lifelight Elixir, "
                        "born from the union of three virtues.[/event]\n"
                        "[dialogue]'It is done. This elixir can counter Malakar's "
                        "life-draining ritual and save King Alden. Take it, and we "
                        "shall proceed to the fortress.'[/dialogue]"
                    )
                )
            elif game_state.get_story_flag(FLAG_ACT3_LIFELIGHT_ELIXIR_CREATED):
                # Step 28 continued: Check if elixir is in inventory before teleporting to fortress
                if not game_state.has_item("Lifelight Elixir"):
                    return (
                        event_msg
                        + "\n"
                        + (
                            "[dialogue]'Elior, you must take the Lifelight Elixir before we "
                            "depart for the fortress. We cannot face Malakar without it—the "
                            "elixir is our only hope of countering his life-draining ritual "
                            "and saving King Alden.'[/dialogue]"
                        )
                    )
                # Step 28 continued: Teleport to fortress
                destination_key = "FortressEntrance"
                flavor = (
                    "[dialogue]'The Lifelight Elixir pulses with the power of three "
                    "virtues. Now we make our final journey—to Malakar's fortress, "
                    "where the kingdom's fate awaits.'[/dialogue]\n"
                    "[dialogue]'Steel yourself, Elior. Beyond this circle lies the "
                    "heart of shadow itself. But you carry the light that can pierce "
                    "even Malakar's darkness.'[/dialogue]"
                )
            else:
                # Initial teleport to start the quest
                destination_key = "TidalCauseway"
                flavor = (
                    "[dialogue]'The hour is upon us, Elior. We will draw the first "
                    "circle at the Tidal Causeway, where moonlight marries the "
                    "sea.'[/dialogue]\n"
                    "[dialogue]'When the air folds and the mist closes, breathe. It "
                    "will pass in a heartbeat.'[/dialogue]"
                )

        if destination_key in game_state.all_rooms:
            # Capture origin and destination rooms
            origin_room = game_state.current_room
            destination_room = game_state.all_rooms[destination_key]

            # Move Mira and Sir Cedric to the new room to accompany the player
            origin_room.characters.remove(self)
            destination_room.characters.append(self)
            sir_cedric = origin_room.get_character_by_name("Sir Cedric")
            if sir_cedric:
                origin_room.characters.remove(sir_cedric)
                destination_room.characters.append(sir_cedric)

            # Perform the teleport by switching the current room
            game_state.current_room = destination_room
            # Call room hook and mark visited for consistency
            game_state.current_room.on_enter(game_state)
            game_state.mark_visited(game_state.current_room)
            arrival_fx = (
                "[event]Mira traces a prism with her finger; the air folds and the "
                "world blurs. When it clears, you arrive at your next "
                "destination.[/event]\n"
            )
            return (
                event_msg + "\n" + flavor + "\n" + arrival_fx +
                f"[event]You arrive at "
                f"[room_name]{game_state.current_room.name}[/room_name].[/event]"
            )
        else:
            return (
                event_msg + "\n" +
                "[failure]Mira hesitates—she cannot find the proper anchor to send "
                "you there yet.[/failure]"
            )
