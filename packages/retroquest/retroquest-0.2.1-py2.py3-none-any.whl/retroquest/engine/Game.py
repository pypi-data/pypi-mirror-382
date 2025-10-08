"""Main game engine class for RetroQuest."""
from typing import Any
from enum import Enum, auto

import pickle
import os

from .Character import Character
from .CommandParser import CommandParser
from .GameState import GameState
from .Item import Item
from .Spell import Spell
from .Act import Act
from .Audio import Audio

# The runtime phase of the game: controls startup/logo/act intro/act transitions
class GameRunState(Enum):
    """Enumeration of game run states."""
    SHOW_LOGO = auto()
    ACT_INTRO = auto()
    ACT_RUNNING = auto()
    ACT_TRANSITION = auto()
class Game:
    """
    Main Game class for RetroQuest: The Awakening.
    Handles the game loop, command parsing, and room transitions.
    """
    def __init__(self, acts: list[Act], dev_mode: bool = False) -> None:
        self.is_running = True
        self.acts = acts
        self.current_act = 0
        # Use the first room in current act's rooms as the starting room
        starting_room = next(iter(self.acts[self.current_act].rooms.values()))
        self.state = GameState(
            starting_room,
            all_rooms=self.acts[self.current_act].rooms,
            all_quests=self.acts[self.current_act].quests
        )
        self.acts[self.current_act].setup_gamestate(self.state)
        self.dev_mode = dev_mode
        self.command_parser = CommandParser(self, dev_mode)
        # Flag to indicate if we need to describe the room after a command
        self.has_changed_room = False
        self.run_state = GameRunState.SHOW_LOGO
        self.accept_input = False
        self.command_result = ''
        # Audio subsystem owned by Game
        self.audio = Audio()
        # Start act music if available
        self.audio.start_music(self.acts[self.current_act].music_file)
    def play_soundeffect(self, filename: str) -> None:
        """Delegate sound effect playback to the Audio subsystem."""
        self.audio.play_soundeffect(filename)

    def start_music(self) -> None:
        """Delegate starting music to the Audio subsystem for the current act."""
        self.audio.start_music(self.acts[self.current_act].music_file)

    def new_turn(self) -> None:
        """Advance the game state by one turn."""
        if self.run_state == GameRunState.SHOW_LOGO:
            self.run_state = GameRunState.ACT_INTRO
            self.accept_input = False
        elif self.run_state == GameRunState.ACT_INTRO:
            self.run_state = GameRunState.ACT_RUNNING
            self.accept_input = True
            self.has_changed_room = True
        elif self.run_state == GameRunState.ACT_RUNNING:
            if self.acts[self.current_act].is_completed(self.state):
                self.current_act += 1
                if self.current_act < len(self.acts):
                    self.run_state = GameRunState.ACT_TRANSITION
                    self.accept_input = False
                    # Transition to next act
                    starting_room = next(iter(self.acts[self.current_act].rooms.values()))
                    self.state = GameState(
                        starting_room,
                        all_rooms=self.acts[self.current_act].rooms,
                        all_quests=self.acts[self.current_act].quests
                    )
                    self.acts[self.current_act].setup_gamestate(self.state)
                    self.has_changed_room = True
                else:
                    # No more acts, end the game
                    self.is_running = False
                    self.accept_input = False
        elif self.run_state == GameRunState.ACT_TRANSITION:
            self.start_music()
            self.run_state = GameRunState.ACT_INTRO
            self.accept_input = False

    def get_result_text(self) -> str:
        """Get the next text to display."""
        if self.run_state == GameRunState.SHOW_LOGO:
            return self.get_ascii_logo()
        elif self.run_state == GameRunState.ACT_INTRO:
            return self.acts[self.current_act].get_act_intro()
        elif self.run_state == GameRunState.ACT_RUNNING:
            return self.command_result
        elif self.run_state == GameRunState.ACT_TRANSITION:
            return (
                self.command_result
                + f"\n\nCongratulations — you have completed Act {self.current_act}!\n\n"
                + "Take a moment to catch your breath and grab a cup of coffee. "
                + f"Get ready for Act {self.current_act + 1}, where new challenges, "
                + "characters, and mysteries await.\n"
            )
        return ""

    def handle_input(self, data: str) -> None:
        """Process input provided by the user."""
        if self.run_state == GameRunState.ACT_RUNNING:
            self.command_result = self.command_parser.parse(data)
        else:
            self.command_result = ''

    def is_act_running(self) -> bool:
        """Return True if the current act is running."""
        return self.run_state == GameRunState.ACT_RUNNING

    def is_act_transitioning(self) -> bool:
        """Return True if the current act is transitioning."""
        return self.run_state == GameRunState.ACT_TRANSITION

    def is_act_intro_showing(self) -> bool:
        """Return True if the current act is transitioning."""
        return self.run_state == GameRunState.ACT_INTRO

    def get_ascii_logo(self) -> str:
        """Return the ASCII logo and music track information for the game."""
        text = r'''
Welcome to
[bold yellow]
########  ######### ######## ########   #######   #######  ##     ## #########  #######  ########
##     ## ##           ##    ##     ## ##     ## ##     ## ##     ## ##        ##           ##
##     ## ##           ##    ##     ## ##     ## ##     ## ##     ## ##        ##           ##.
########  #########    ##    ########  ##     ## ##     ## ##     ## #########  #######     ##
##   ##   ##           ##    ##   ##   ##     ## ##  ## ## ##     ## ##               ##    ##.
##    ##  ##           ##    ##    ##  ##     ## ##   #### ##     ## ##        ##     ##    ##.
##     ## #########    ##    ##     ##  #######   #######   #######  #########  #######     ##.
[/bold yellow]
[bold]Music track:[/bold] '''
        text += self.acts[self.current_act].music_info
        return text

    def get_act_intro(self) -> None:
        """Get the introduction text for the current act."""
        return self.acts[self.current_act].get_act_intro()

    def get_command_completions(self) -> dict[str, Any]:
        """
        Generate command completion suggestions based on current game state.
        Returns a nested dictionary structure for tab completion.
        """
        # Helper to build nested dict for multi-word item names
        def build_nested_names(names: list[str]) -> dict[str, Any]:
            nested = {}
            for name in names:
                parts = name.split()
                d = nested
                for i, part in enumerate(parts):
                    if i == len(parts) - 1:
                        d[part] = None
                    else:
                        if part not in d or not isinstance(d[part], dict):
                            d[part] = {}
                        d = d[part]
            return nested

        all_items = self.state.current_room.get_items() + self.state.inventory
        item_names = [item.get_name().lower() for item in all_items]
        item_short_names = [
            item.get_short_name().lower()
            for item in all_items
            if item.get_short_name()
        ]
        all_item_names = item_names + item_short_names

        inventory_item_names = [item.get_name().lower() for item in self.state.inventory]
        inventory_item_short_names = [
            item.get_short_name().lower()
            for item in self.state.inventory
            if item.get_short_name()
        ]
        all_inventory_item_names = inventory_item_names + inventory_item_short_names

        room_item_names = [item.get_name().lower() for item in self.state.current_room.get_items()]
        room_item_short_names = [
            item.get_short_name().lower()
            for item in self.state.current_room.get_items()
            if item.get_short_name()
        ]
        all_room_item_names = room_item_names + room_item_short_names

        character_names = [
            char.get_name().lower()
            for char in self.state.current_room.get_characters()
        ]
        spell_names = [spell.get_name().lower() for spell in self.state.known_spells]
        exit_names = {
            direction: None
            for direction in self.state.current_room.get_exits(self.state)
        }
        file_names = {
            f: None
            for f in os.listdir('.')
            if f.endswith('.txt') and os.path.isfile(f)
        }

        # Build 'use' completions so that 'with' is suggested only after the full item name
        # use_with_dict = build_nested_names(all_item_names)
        # use_completions = build_command_with_preposition(all_item_names, 'with', use_with_dict)

        # Build 'give' completions so that 'to' is suggested only after the full item name
        # give_to_dict = build_nested_names(character_names)
        # give_completions = build_command_with_preposition(
        #     all_inventory_item_names, 'to', give_to_dict
        # )

        # Build directional completions based on actual exits
        directional_completions = {}
        available_exits = self.state.current_room.get_exits(self.state)

        # Short directions
        if 'north' in available_exits:
            directional_completions['n'] = None
        if 'south' in available_exits:
            directional_completions['s'] = None
        if 'east' in available_exits:
            directional_completions['e'] = None
        if 'west' in available_exits:
            directional_completions['w'] = None

        # Long directions
        for direction in ['north', 'south', 'east', 'west']:
            if direction in available_exits:
                directional_completions[direction] = None

        completions = {
            'go': exit_names,
            'move': exit_names,
            **directional_completions,  # Only include available directions
            # 'enter': None,
            # 'leave': None,
            # 'exit': None,
            # 'climb': build_nested_names(all_item_names),
            # 'ascend': build_nested_names(all_item_names),
            # 'descend': build_nested_names(all_item_names),
            # 'follow': None,
            # 'walk': None,

            'talk': {'to': build_nested_names(character_names)},
            'speak': {'to': build_nested_names(character_names)},
            'converse': {'with': build_nested_names(character_names)},
            'give': {
                **{k: {'to': {**build_nested_names(character_names)}}
                   for k in all_inventory_item_names}
            },
            'hand': build_nested_names(all_inventory_item_names),
            'buy': {
                **{k: {'from': {**build_nested_names(character_names)}}
                   for k in all_room_item_names}
            },

            'look': {
                'at': {
                    **build_nested_names(all_item_names),
                    **build_nested_names(character_names)
                },
                **build_nested_names(all_item_names),
                **build_nested_names(character_names),
            },
            'l': None,
            'observe': None,
            'survey': None,
            'inspect': {
                **build_nested_names(all_item_names),
                **build_nested_names(character_names)
            },
            'examine': {
                **build_nested_names(all_item_names),
                **build_nested_names(character_names)
            },
            'check': {
                **build_nested_names(all_item_names),
                **build_nested_names(character_names)
            },
            'read': build_nested_names(all_item_names),
            'search': None,
            'investigate': None,
            # 'listen': {'to': build_nested_names(all_item_names)},

            'take': build_nested_names(all_room_item_names),
            'pick': {'up': build_nested_names(all_room_item_names)},
            'grab': build_nested_names(all_room_item_names),
            'get': build_nested_names(all_room_item_names),
            'drop': build_nested_names(all_inventory_item_names),
            'discard': build_nested_names(all_inventory_item_names),
            'use': {
                **{k: {
                    '@': None,
                    'with': {
                        **build_nested_names(all_item_names),
                        **build_nested_names(character_names)
                    }
                } for k in all_item_names}
            },
            # 'eat': build_nested_names(all_inventory_item_names),
            # 'consume': build_nested_names(all_inventory_item_names),
            # 'drink': build_nested_names(all_inventory_item_names),
            # 'equip': build_nested_names(all_inventory_item_names),
            # 'wear': build_nested_names(all_inventory_item_names),
            # 'unequip': build_nested_names(all_inventory_item_names),
            # 'remove': build_nested_names(all_inventory_item_names),
            'inventory': None, 'i': None, 'inv': None,
            'open': build_nested_names(all_item_names),
            'close': build_nested_names(all_item_names),

            'cast': {
                **{k: {
                    '@': None,
                    'on': {
                        **build_nested_names(all_item_names),
                        **build_nested_names(character_names)
                    }
                } for k in spell_names}
            },
            'spells': None,

            'save': None,
            'load': None,
            'help': None, '?': None,
            'quit': None, 'exit': None,

            'sleep': None,
            'rest': None,
            'map': None,
            'stats': None,
        }

        # Add dev_execute_commands to completions if DEV_MODE
        if self.dev_mode:
            completions['dev_execute_commands'] = file_names

        # Process completions to split multi-word keys into nested levels
        def split_multiword_keys(comp_dict: Any) -> Any:
            if not isinstance(comp_dict, dict):
                return comp_dict

            new_dict = {}
            for key, value in comp_dict.items():
                parts = key.split()
                if len(parts) > 1:
                    # Multi-word key, create nested structure
                    d = new_dict
                    for i, part in enumerate(parts):
                        if i == len(parts) - 1:
                            # Last part, assign the recursively processed value
                            d[part] = split_multiword_keys(value)
                        else:
                            # Intermediate part, create nested dict if needed
                            if part not in d:
                                d[part] = {}
                            elif not isinstance(d[part], dict):
                                # If it's not a dict, convert it to one
                                d[part] = {}
                            d = d[part]
                else:
                    # Single word key, recursively process the value
                    new_dict[key] = split_multiword_keys(value)
            return new_dict

        completions = split_multiword_keys(completions)

        return completions

    def find_character(self, target: str) -> Character:
        """Find a character in the current room by name."""
        character_to_examine = None
        target = target.lower()
        for character in self.state.current_room.get_characters():
            if (character_to_examine is None and
                character.get_name().lower() == target):
                character_to_examine = character
        return character_to_examine

    def find_item(self, target: str, look_in_inventory: bool = True,
                  look_in_room: bool = True) -> Item:
        """
        Find an item by its name or short name in the inventory and/or current room.
        Returns the item object or None if not found.
        """
        target = target.lower()
        item_to_examine = None
        # Check inventory first
        if look_in_inventory:
            for item in self.state.inventory:
                if (item_to_examine is None and
                    (item.get_name().lower() == target or
                     item.get_short_name().lower() == target)):
                    item_to_examine = item
        # Then check items in the current room
        if look_in_room:
            for item in self.state.current_room.get_items():
                if (item_to_examine is None and
                    (item.get_name().lower() == target or
                     item.get_short_name().lower() == target)):
                    item_to_examine = item
        return item_to_examine

    def find_all_items(self, target: str, look_in_inventory: bool = True,
                       look_in_room: bool = True) -> list[Item]:
        """
        Find all items by their name or short name in the inventory and/or current room.
        Returns a list of all matching items.
        """
        target = target.lower()
        matching_items = []
        # Check inventory first
        if look_in_inventory:
            for item in self.state.inventory:
                if (item.get_name().lower() == target or
                    item.get_short_name().lower() == target):
                    matching_items.append(item)
        # Then check items in the current room
        if look_in_room:
            for item in self.state.current_room.get_items():
                if (item.get_name().lower() == target or
                    item.get_short_name().lower() == target):
                    matching_items.append(item)
        return matching_items

    def move(self, direction: str, _arg: str = None) -> str:
        """Move the player in the specified direction."""
        exits = self.state.current_room.get_exits(self.state)

        # Special handling for MainSquare navigation restriction
        if (self.state.current_room.name == "Main Square" and
            not self.state.get_story_flag("used_city_map") and
            direction != "south"):
            # Check if this would have been a valid direction with the map
            all_exits = self.state.current_room.exits  # Get unrestricted exits
            if direction in all_exits:
                return (
                    "[event]You wander through Greendale's winding streets, but without a proper "
                    "map to guide you, you quickly become lost in the maze of alleys and "
                    "buildings. Eventually, you find your way back to the Main Square, "
                    "feeling disoriented.[/event]"
                )

        if direction in exits:
            next_room_key = exits[direction]
            if next_room_key in self.state.all_rooms:
                self.state.current_room = self.state.all_rooms[next_room_key]
                self.state.current_room.on_enter(self.state)
                self.state.mark_visited(self.state.current_room)
                self.has_changed_room = True
                return (
                    f"[event]You move {direction} to "
                    f"[room_name]{self.state.current_room.name}[/room_name].[/event]\n\n"
                )
            else:
                return "[failure]That exit leads nowhere (room not found).[/failure]"
        else:
            return "[failure]You can't go that way.[/failure]"

    def help(self, _arg: str = None) -> str:
        """Display help text with available commands."""
        return (
            "[bold]Available Commands:[/bold]\n"
            "\n"
            "[bold]Movement:[/bold]\n"
            "  go <direction>, move <direction>, <direction>, <short_direction> "
            "(e.g., go north, n)\n"
            #"  enter <location>, go in, go inside\n"
            #"  leave <location>, exit <location>, go out\n"
            #"  climb <object>, ascend <object>\n"
            #"  descend <object>, go down <object>\n"
            #"  follow <path>, walk <path>\n"
            "\n"
            "[bold]Interaction:[/bold]\n"
            "  talk to <character>, speak to <character>, converse with <character>\n"
            "  say <word(s)> to <character>\n"
            "  give <item> to <character>, hand <item> to <character>\n"
            "  buy <item> from <character>\n"
            "\n"
            "[bold]Examination:[/bold]\n"
            "  look, observe, survey, l\n"
            "  look at <object>, inspect <object>, examine <object>, check <object>\n"
            "  search, investigate\n"
            #"  listen to <object/location>\n"
            "\n"
            "[bold]Inventory Management:[/bold]\n"
            "  take <item>, pick up <item>, grab <item>, get <item>\n"
            "  drop <item>, discard <item>\n"
            "  use <item>, use <item> with <item>\n"
            #"  eat <item>, consume <item>\n"
            #"  drink <item>\n"
            #"  equip <item>, wear <item>\n"
            #"  unequip <item>, remove <item>\n"
            "  inventory, i, inv\n"
            "  open <container>\n"
            "  close <container>\n"
            "\n"
            "[bold]Magic:[/bold]\n"
            "  cast <spell>\n"
            "  cast <spell> on <object/character>\n"
            "  spells\n"
            "\n"
            "[bold]Game Management:[/bold]\n"
            "  save, load\n"
            "  help, ?\n"
            "  quit, exit\n"
            "\n"
            "[bold]Miscellaneous:[/bold]\n"
            "  sleep, rest\n"
            "  map\n"
            "  stats\n"
        )

    def look(self) -> str:
        """Look around the current room."""
        self.has_changed_room = True
        return "[event]You take a look at your surroundings.[/event]\n\n"

    def examine(self, target: str) -> str:
        """Examine a specific item or character."""
        if not target:  # Check if target is an empty string or None
            return "Examine what?"

        # Check for items and characters as usual
        item_to_examine = self.find_item(target)
        if item_to_examine:
            return item_to_examine.examine(self.state)
        character_to_examine = self.find_character(target)
        if character_to_examine:
            return character_to_examine.examine(self.state)
        return f"You don't see any '{target}' here."

    def map(self) -> str:
        """Display a map of visited rooms and their exits."""
        # Print all visited rooms and their exits, each exit on a new indented line
        visited = set(self.state.visited_rooms)
        room_objs = {
            name: room
            for name, room in self.state.all_rooms.items()
            if room.name in visited
        }
        if not room_objs:
            return "No rooms visited yet."
        output = ["[bold]Visited Rooms and Exits:[/bold]"]
        for name, room in room_objs.items():
            exits = room.get_exits(self.state)
            output.append(f"- [room_name]{room.name}[/room_name]:")
            if exits:
                for direction, dest in exits.items():
                    dest_name = (
                        self.state.all_rooms[dest].name
                        if dest in self.state.all_rooms
                        else dest
                    )
                    output.append(f"    {direction} -> [room_name]{dest_name}[/room_name]")
            else:
                output.append("    No exits")
        return "\n".join(output)

    def unknown(self, command: str) -> str:
        """Handle unknown commands."""
        return (
            f"I don't understand the command: '{command}'. "
            "Try 'help' for a list of valid commands."
        )

    def quit(self) -> str:
        """Quit the game."""
        self.is_running = False
        return ''

    def drop(self, item: str) -> str:
        """Drop an item from inventory to the current room."""
        item_to_drop = self.find_item(item, look_in_inventory=True, look_in_room=False)
        if item_to_drop:
            self.state.inventory.remove(item_to_drop)
            self.state.current_room.items.append(item_to_drop)
            return f"You drop the [item_name]{item_to_drop.get_name()}[/item_name]."
        return f"[failure]You don't have a '{item}' to drop.[/failure]"

    def take(self, item: str) -> str:
        """Take an item from the current room and add it to inventory."""
        items_to_take = self.find_all_items(
            item, look_in_inventory=False, look_in_room=True
        )
        if not items_to_take:
            return f"[failure]There is no '{item}' here to take.[/failure]"

        taken_items = []
        prevented_items = []

        for item_to_take in items_to_take:
            no_pickup = item_to_take.prevent_pickup()
            if no_pickup:
                # If the item has a prevent_pickup method that returns a message, track it
                prevented_items.append((item_to_take, no_pickup))
            else:
                self.state.current_room.items.remove(item_to_take)
                self.state.inventory.append(item_to_take)

                # Call picked_up on the item
                pickup_message = item_to_take.picked_up(self.state)
                taken_items.append((item_to_take, pickup_message))

        # Build response message
        responses = []

        if taken_items:
            if len(taken_items) == 1:
                item_obj, pickup_message = taken_items[0]
                response = (
                    f"[event]You take the [item_name]{item_obj.get_name()}[/item_name].[/event]"
                )
                if pickup_message:
                    response += " " + pickup_message
                responses.append(response)
            else:
                # Multiple items taken
                item_name = taken_items[0][0].get_name()  # Use the name from the first item
                responses.append(
                    f"[event]You take {len(taken_items)} "
                    f"[item_name]{item_name}[/item_name].[/event]"
                )
                # Add any pickup messages
                for item_obj, pickup_message in taken_items:
                    if pickup_message:
                        responses.append(pickup_message)

        # Add any prevention messages
        for item_obj, no_pickup in prevented_items:
            responses.append(no_pickup)

        if not taken_items and prevented_items:
            # All items were prevented from being picked up
            return "\n".join(responses)
        elif taken_items:
            return "\n".join(responses)
        else:
            # This shouldn't happen, but just in case
            return f"[failure]There is no '{item}' here to take.[/failure]"

    def inventory(self) -> str:
        """Display the player's inventory."""
        if not self.state.inventory:
            return "Your inventory is empty."
        lines = ["[bold]You are carrying:[/bold]"]
        for item in self.state.inventory:
            lines.append(f"- [item_name]{item.get_name()}[/item_name]")
        return "\n".join(lines)

    def talk(self, target: str) -> str:
        """Talk to a character in the current room."""
        if not target:
            return "[failure]Talk to whom?[/failure]"
        character_to_talk_to = self.find_character(target)
        if character_to_talk_to:
            return character_to_talk_to.talk_to(self.state)
        else:
            return (
                f"[failure]There is no character named "
                f"'[character_name]{target}[/character_name]' here to talk to.[/failure]"
            )

    def say(self, word: str, character_name: str) -> str:
        """Say a specific word or phrase to a character."""
        if not word:
            return "[failure]What do you want to say?[/failure]"
        if not character_name:
            return "[failure]Who do you want to say that to?[/failure]"

        character_to_speak_to = self.find_character(character_name)
        if character_to_speak_to:
            return character_to_speak_to.say_to(word, self.state)
        else:
            return (
                f"[failure]There is no character named "
                f"'[character_name]{character_name}[/character_name]' here to speak to.[/failure]"
            )

    def split_command(self, command_args: str, command: str,
                      delimiter: str) -> tuple[str, None, str, None, str]:
        """Split command arguments using a delimiter (e.g., 'give item to character')."""
        # Expected format: "<command> <item/character_name> <delimiter> <item/character_name>"
        parts = command_args.lower().split()
        if delimiter not in parts:
            return None, None, (
                f"[failure]Invalid command format. "
                f"Please use '{command} <target1> {delimiter} <target2>'.[/failure]"
            )
        del_index = parts.index(delimiter)
        if del_index == 0:  # No target1 provided
            return None, None, f"[failure]What do you want to {command}?[/failure]"
        target1 = " ".join(parts[:del_index])
        if del_index >= len(parts) - 1:  # No target2 provided
            return None, None, (
                f"[failure]Who/What should I {command} {target1} {delimiter}?[/failure]"
            )
        target2 = " ".join(parts[del_index+1:])
        return target1, target2, ''

    def give(self, command_args: str) -> str:
        """Give an item from inventory to a character."""
        # Split the command into item and character parts
        item_name, character_name, error = self.split_command(command_args, 'give', 'to')
        if item_name is None or character_name is None:
            return error

        # Check if item is in inventory
        item_to_give = self.find_item(item_name, look_in_inventory=True, look_in_room=False)
        if not item_to_give:
            return f"[failure]You don't have any '{item_name}' to give.[/failure]"

        # Check if character is in the room
        character_to_receive = self.find_character(character_name)
        if not character_to_receive:
            return (
                f"[failure]There is no character named "
                f"'{character_name.capitalize()}' here.[/failure]"
            )

        # Call give_item on the character
        return character_to_receive.give_item(self.state, item_to_give)

    def buy(self, command_args: str) -> str:
        """Buy an item from a character."""
        # Split the command into item and character parts
        item_name, character_name, error = self.split_command(command_args, 'buy', 'from')
        if item_name is None or character_name is None:
            return error

        # Check if character is in the room
        character_to_buy_from = self.find_character(character_name)
        if not character_to_buy_from:
            return (
                f"[failure]There is no character named "
                f"'{character_name.capitalize()}' here.[/failure]"
            )

        return character_to_buy_from.buy_item(item_name, self.state)

    def use(self, item_name_1: str, object_name: str = None) -> str:
        """Use an item, optionally with another item or on a character."""
        item_obj_1 = self.find_item(item_name_1, look_in_inventory=True, look_in_room=True)

        if not item_obj_1:
            return (
                f"[failure]You don't have a '{item_name_1}' to use, and there isn't one "
                "here.[/failure]"
            )

        # --- Handle two-item usage ---
        if object_name:
            item_obj_2 = self.find_item(object_name, look_in_inventory=True, look_in_room=True)

            if not item_obj_2:
                character_obj_2 = self.find_character(object_name)
                if character_obj_2:
                    return item_obj_1.use_on_character(self.state, character_obj_2)
                return (
                    f"[failure]You don't see a '{object_name}' to use with the "
                    f"[item_name]{item_obj_1.get_name()}[/item_name].[/failure]"
                )

            if item_obj_1 == item_obj_2:
                return (
                    f"[failure]You can't use the [item_name]{item_obj_1.get_name()}[/item_name] "
                    "with itself.[/failure]"
                )

            return item_obj_1.use_with(self.state, item_obj_2)

        # --- Handle single-item usage ---
        else:
            return item_obj_1.use(self.state)

    def cast(self, command_args: str) -> str:
        """Cast a spell, optionally on a target."""
        # Try to split for "cast <spell> on <target>"
        parts = command_args.lower().split(' on ', 1)
        spell_name = parts[0].strip()
        target_name = None
        if len(parts) > 1:
            target_name = parts[1].strip()

        spell_to_cast = None
        for spell_obj in self.state.known_spells:
            if spell_obj.get_name().lower() == spell_name:
                spell_to_cast = spell_obj
                break

        if not spell_to_cast:
            return f"[failure]You don't know any spell called '{spell_name}'.[/failure]"

        target_item = None
        target_character = None
        if target_name:
            # First try to find an item
            target_item = self.find_item(target_name, look_in_inventory=True, look_in_room=True)
            if not target_item:
                # If no item found, try to find a character
                target_character = self.find_character(target_name)
                if not target_character:
                    return (
                        f"[failure]You don't see a '{target_name}' to cast "
                        f"[spell_name]{spell_name}[/spell_name] on.[/failure]"
                    )

            # Cast spell on the found target (item or character)
            if target_item:
                # Pass game_state and target_item
                return spell_to_cast.cast_on_item(self.state, target_item)
            else:
                # Pass game_state and target_character
                return spell_to_cast.cast_on_character(self.state, target_character)
        else:
            # Spells that don't require a target
            return spell_to_cast.cast_spell(self.state)  # Pass game_state only

    def learn(self, spell: Spell) -> str:
        """Learn a new spell."""
        if spell not in self.state.known_spells:
            self.state.known_spells.append(spell)
            return (
                f"[event]You have learned the [spell_name]{spell.get_name()}[/spell_name] "
                "spell![/event]"
            )

    def spells(self) -> str:  # Method to list known spells
        """List all known spells."""
        if not self.state.known_spells:
            return "You don't know any spells yet."

        output = ["[bold]Known Spells:[/bold]"]
        for spell_obj in self.state.known_spells:
            output.append(
                f"  - [spell_name]{spell_obj.get_name()}[/spell_name]: "
                f"{spell_obj.get_description()}"
            )
        return "\n".join(output)

    def search(self) -> str:
        """Search the current room."""
        return self.state.current_room.search(self.state)  # Pass game_state

    def listen(self, target: str = None) -> str:
        """Listen to the environment or a specific item."""
        if not target:
            return self.state.current_room.get_ambient_sound()

        item_to_listen_to = self.find_item(target, look_in_inventory=True, look_in_room=True)
        if item_to_listen_to:
            return item_to_listen_to.listen(self.state)
        else:
            return (
                f"[failure]You don't see a '{target}' to listen to here or in your "
                "inventory.[/failure]"
            )

    def rest(self) -> str:
        """Rest in the current room."""
        return self.state.current_room.rest(self.state)

    def open(self, target: str) -> str:
        """Open an item."""
        if not target:
            return "[failure]Open what?[/failure]"
        item_to_open = self.find_item(target, look_in_inventory=True, look_in_room=True)
        if item_to_open:
            return item_to_open.open(self.state)  # Pass game_state to the item's open method
        else:
            return (
                f"[failure]You don't see a '{target}' to open here or in your inventory.[/failure]"
            )

    def close(self, target: str) -> str:
        """Close an item."""
        if not target:
            return "[failure]Close what?[/failure]"
        item_to_close = self.find_item(target, look_in_inventory=True, look_in_room=True)
        if item_to_close:
            return item_to_close.close(self.state)  # Pass game_state to the item's close method
        else:
            return (
                f"[failure]You don't see a '{target}' to close here or in your "
                "inventory.[/failure]"
            )

    def eat(self, item: str) -> str:
        """Eat an item."""
        if not item:
            return "[failure]Eat what?[/failure]"
        item_to_eat = self.find_item(item, look_in_inventory=True, look_in_room=True)
        if item_to_eat:
            return item_to_eat.eat(self.state)
        else:
            return (
                f"[failure]You don't see a '{item}' to eat here or in your inventory.[/failure]"
            )

    def drink(self, item: str) -> str:
        """Drink an item."""
        if not item:
            return "[failure]Drink what?[/failure]"
        item_to_drink = self.find_item(item, look_in_inventory=True, look_in_room=True)
        if item_to_drink:
            return item_to_drink.drink(self.state)
        else:
            return (
                f"[failure]You don't see a '{item}' to drink here or in your inventory.[/failure]"
            )

    def equip(self, item: str) -> str:
        """Equip an item."""
        if not item:
            return "[failure]Equip what?[/failure]"
        item_to_equip = self.find_item(item, look_in_inventory=True, look_in_room=True)
        if item_to_equip:
            return item_to_equip.equip(self.state)
        else:
            return (
                f"[failure]You don't see a '{item}' to equip here or in your inventory.[/failure]"
            )

    def unequip(self, item: str) -> str:
        """Unequip an item."""
        if not item:
            return "[failure]Unequip what?[/failure]"
        item_to_unequip = self.find_item(item, look_in_inventory=True, look_in_room=True)
        if item_to_unequip:
            return item_to_unequip.unequip(self.state)
        else:
            return (
                f"[failure]You don't see a '{item}' to unequip here or in your "
                "inventory.[/failure]"
            )

    def save(self) -> str:
        """Save the game state to a file."""
        try:
            with open('retroquest.save', 'wb') as f:
                pickle.dump(self.state, f)
            return "[event]Game saved successfully.[/event]"
        except OSError as e:
            return f"[failure]Failed to save game: {e}[/failure]"

    def load(self) -> str:
        """Load the game state from a file."""
        if not os.path.exists('retroquest.save'):
            return "[failure]No save file found.[/failure]"
        try:
            with open('retroquest.save', 'rb') as f:
                self.state = pickle.load(f)
            return "[event]Game loaded successfully.[/event]"
        except OSError as e:
            return f"[failure]Failed to load game: {e}[/failure]"

    def stats(self) -> str:
        """Display game statistics."""
        return self.state.stats()

    def dev_execute_commands(self, filename: str) -> str:
        """
        Execute a list of commands from a file, one per line, for dev/testing purposes.
        Returns a summary of the results.
        """
        if not os.path.exists(filename):
            return f"[failure]File not found: {filename}[/failure]"
        results = []
        with open(filename, 'rt', encoding='utf-8') as f:
            for line in f:
                command = line.strip()
                if not command or command.startswith('#'):
                    continue  # Skip empty lines and comments
                result = self.command_parser.parse(command)
                while self.state.next_activated_quest():
                    pass
                while self.state.next_updated_quest():
                    pass
                while self.state.next_completed_quest():
                    pass
                results.append(f"> {command}\n{result}")
        return "\n".join(results)
