"""Helper utilities for test assertions and command execution."""

results = []

# Helper functions for assertions
def check_item_in_inventory(game_state, item_name: str, should_be_present: bool = True):
    """Check if an item is present or absent in the player's inventory."""
    inventory_names = [item.get_name().lower() for item in game_state.inventory]
    if should_be_present:
        assert item_name.lower() in inventory_names, (
            f"{item_name} not found in inventory, but was expected."
        )
    else:
        assert item_name.lower() not in inventory_names, (
            f"{item_name} found in inventory, but was not expected."
        )

def check_item_count_in_inventory(game_state, item_name: str, expected_count: int):
    """Check that the inventory contains exactly the expected count of a specific item."""
    inventory_names = [item.get_name().lower() for item in game_state.inventory]
    actual_count = inventory_names.count(item_name.lower())
    assert actual_count == expected_count, (
        f"Expected {expected_count} {item_name} in inventory, but found {actual_count}."
    )

def check_item_in_room(current_room, item_name: str, should_be_present: bool = True):
    """Check if an item is present or absent in the current room."""
    room_item_names = [item.get_name().lower() for item in current_room.get_items()]
    if should_be_present:
        assert item_name.lower() in room_item_names, (
            f"{item_name} not found in room {current_room.name}, but was expected."
        )
    else:
        assert item_name.lower() not in room_item_names, (
            f"{item_name} found in room {current_room.name}, but was not expected."
        )

def check_character_in_room(current_room, character_name: str, should_be_present: bool = True):
    """Check if a character is present or absent in the current room."""
    room_character_names = [char.get_name().lower() for char in current_room.get_characters()]
    if should_be_present:
        assert character_name.lower() in room_character_names, (
            f"Character '{character_name}' not found in room {current_room.name}, "
            f"but was expected."
        )
    else:
        assert character_name.lower() not in room_character_names, (
            f"Character '{character_name}' found in room {current_room.name}, "
            f"but was not expected."
        )

def check_spell_known(game_state, spell_name: str, should_be_present: bool = True):
    """Check if a spell is known or unknown by the player."""
    spell_names = [spell.get_name().lower() for spell in game_state.known_spells]
    if should_be_present:
        assert spell_name.lower() in spell_names, (
            f"Spell '{spell_name}' not found in known spells, but was expected."
        )
    else:
        assert spell_name.lower() not in spell_names, (
            f"Spell '{spell_name}' found in known spells, but was not expected."
        )

def check_story_flag(game_state, flag_name: str, expected_value: bool = True):
    """Check if a story flag has the expected value."""
    assert game_state.get_story_flag(flag_name) == expected_value, (
        f"Story flag '{flag_name}' was not {expected_value}."
    )

def check_current_room(game_state, expected_room_name: str):
    """Check if the player is currently in the expected room."""
    assert game_state.current_room.name == expected_room_name, f"Not in '{expected_room_name}'"

def check_quest_completed(game_state, quest_name: str):
    """Check if a quest with the given name is completed."""
    assert game_state.is_quest_completed(quest_name), (
        f"Quest '{quest_name}' should be completed but is not"
    )

def check_quests(game_state, expected_active_quests):
    """
    Asserts that the specified quests (by name) are currently active, no more, no less.
    """
    active_quest_names = sorted([q.name for q in game_state.activated_quests])
    expected_names = sorted(expected_active_quests)
    assert active_quest_names == expected_names, (
        f"Active quests do not match.\nExpected: {expected_names}\nActual: {active_quest_names}"
    )

def execute_commands(game, commands_list):
    """Execute a list of commands in sequence and return combined results."""
    part_result = []
    for cmd in commands_list:
        part_result.append(game.command_parser.parse(cmd))
        while game.state.next_activated_quest():
            pass
        while game.state.next_updated_quest():
            pass
        while game.state.next_completed_quest():
            pass
    results.extend(part_result)
    _debug_print_history()
    return "".join(part_result)

def _debug_print_history():
    """Print the command execution history for debugging purposes."""
    for res_str in results:
        print(res_str)
