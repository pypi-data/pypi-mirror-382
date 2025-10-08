# Story flag constants for use throughout the game
"""
Act1StoryFlags.py

This module defines story flag constants used throughout Act 1 of the game.
Each flag represents a specific event, interaction, or milestone that can be tracked
to manage game state and narrative progression.

Flags include:
- Discovery events (e.g., finding the lost letter, photo)
- Character interactions (e.g., talking to the grandmother, priest, fisherman, blacksmith, villager)
- Investigation and observation events (e.g., investigating withered crops,
    observing deer, examining the well)
- Magical progression (e.g., learning spells, unlocking magic, completing blessings)
- Major story milestones (e.g., witnessing shadow events, completing Shadows Over Willowbrook)

These constants are intended for use throughout the game's codebase to ensure consistent
reference to story flags and facilitate maintainable game logic.
"""
FLAG_FOUND_LOST_LETTER = "found_lost_letter"
FLAG_ASKED_GRANDMOTHER_ABOUT_LETTER = "asked_grandmother_about_letter"
FLAG_INVESTIGATED_WITHERED_CROPS = "investigated_withered_crops"
FLAG_WITNESSED_SHADOW_EVENT = "witnessed_shadow_event"
FLAG_ACCEPTED_MIRA_APPRENTICESHIP = "accepted_mira_apprenticeship"
FLAG_LEARNED_FIRST_SPELL = "learned_first_spell"
FLAG_MAGIC_FULLY_UNLOCKED = "magic_fully_unlocked"
FLAG_JOURNEY_BLESS_COMPLETED = "journey_bless_completed"
FLAG_PRIEST_TALKED_TO = "priest_talked_to"
FLAG_TALKED_TO_FISHERMAN = "talked_to_fisherman"
FLAG_DEER_CAN_BE_OBSERVED = "deer_can_be_observed"
FLAG_BLACKSMITH_MET = "blacksmith_met"
FLAG_FOUND_PHOTO = "found_photo"
FLAG_READ_PHOTO_MESSAGE = "read_photo_message"
FLAG_TALKED_TO_GRANDMOTHER_ABOUT_PHOTO = "talked_to_grandmother_about_photo"
FLAG_VILLAGER_TALKED_TO = "villager_talked_to"
FLAG_WELL_EXAMINED = "well_examined"
FLAG_CONNECT_WITH_NATURE = "connect_with_nature"
FLAG_SHADOWS_OVER_WILLOWBROOK_COMPLETED = "shadows_over_willowbrook_completed"
