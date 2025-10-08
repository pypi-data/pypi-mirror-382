"""Tests for Act 2 room definitions and connectivity."""

import pytest
from retroquest.act2.rooms.MountainPath import MountainPath
from retroquest.act2.rooms.GreendaleGates import GreendaleGates
from retroquest.act2.rooms.MainSquare import MainSquare
from retroquest.act2.rooms.MarketDistrict import MarketDistrict
from retroquest.act2.rooms.SilverStagInn import SilverStagInn
from retroquest.act2.rooms.InnRooms import InnRooms
from retroquest.act2.rooms.MerchantsWarehouse import MerchantsWarehouse
from retroquest.act2.rooms.CastleApproach import CastleApproach
from retroquest.act2.rooms.CastleCourtyard import CastleCourtyard
from retroquest.act2.rooms.GreatHall import GreatHall
from retroquest.act2.rooms.ResidentialQuarter import ResidentialQuarter
from retroquest.act2.rooms.HealersHouse import HealersHouse
from retroquest.act2.rooms.HiddenLibrary import HiddenLibrary
from retroquest.act2.rooms.ForestTransition import ForestTransition
from retroquest.act2.rooms.ForestEntrance import ForestEntrance
from retroquest.act2.rooms.AncientGrove import AncientGrove
from retroquest.act2.rooms.WhisperingGlade import WhisperingGlade
from retroquest.act2.rooms.HeartOfTheForest import HeartOfTheForest


class MockGameState:
    """Mock GameState for testing that only provides get_story_flag method"""
    def __init__(self):
        """Initialize mock game state with empty story flags."""
        self.story_flags = []

    def get_story_flag(self, flag):
        """Check if a story flag is set."""
        return flag in self.story_flags

ROOM_CLASSES = {
    "MountainPath": MountainPath,
    "GreendaleGates": GreendaleGates,
    "MainSquare": MainSquare,
    "MarketDistrict": MarketDistrict,
    "SilverStagInn": SilverStagInn,
    "InnRooms": InnRooms,
    "MerchantsWarehouse": MerchantsWarehouse,
    "CastleApproach": CastleApproach,
    "CastleCourtyard": CastleCourtyard,
    "GreatHall": GreatHall,
    "ResidentialQuarter": ResidentialQuarter,
    "HealersHouse": HealersHouse,
    "HiddenLibrary": HiddenLibrary,
    "ForestTransition": ForestTransition,
    "ForestEntrance": ForestEntrance,
    "AncientGrove": AncientGrove,
    "WhisperingGlade": WhisperingGlade,
    "HeartOfTheForest": HeartOfTheForest,
}


@pytest.mark.parametrize("_room_name,room_class", ROOM_CLASSES.items())
def test_room_creation(_room_name, room_class):
    """Test that all Act2 rooms can be created without errors"""
    room = room_class()
    assert room is not None
    assert room.name is not None
    assert room.description is not None
    assert hasattr(room, 'items')
    assert hasattr(room, 'characters')
    assert hasattr(room, 'exits')


def test_all_rooms_have_valid_exits():
    """Test that all room exits reference valid room names"""
    valid_room_names = set(ROOM_CLASSES.keys())

    # Create a mock GameState for testing
    mock_game_state = MockGameState()

    for room_name, room_class in ROOM_CLASSES.items():
        room = room_class()
        exits = room.get_exits(mock_game_state)
        for direction, target_room in exits.items():
            # Special handling for secret passages and special exits
            if direction in ["secret_passage", "upstairs", "downstairs"]:
                continue
            assert target_room in valid_room_names, (
                f"Room {room_name} has invalid exit to {target_room}"
            )


def test_room_connectivity():
    """Test that room connections are bidirectional where expected"""
    rooms = {name: cls() for name, cls in ROOM_CLASSES.items()}

    # Check that if room A has an exit to room B, room B should have a corresponding exit back to A
    # (with some exceptions for special exits like upstairs/downstairs, secret passages)

    direction_opposites = {
        "north": "south",
        "south": "north",
        "east": "west",
        "west": "east",
    }

    for room_name, room in rooms.items():
        for direction, target_room_name in room.exits.items():
            if direction in direction_opposites and target_room_name in rooms:
                target_room = rooms[target_room_name]
                opposite_direction = direction_opposites[direction]

                # Special handling for inn - call use_key to unlock exits
                if room_name == "SilverStagInn" or target_room_name == "SilverStagInn":
                    if hasattr(room, 'use_key'):
                        room.use_key()
                    if hasattr(target_room, 'use_key'):
                        target_room.use_key()

                # Check if the target room has the expected return exit
                assert opposite_direction in target_room.exits, (
                    f"Room {target_room_name} should have {opposite_direction} exit "
                    f"back to {room_name}"
                )
                assert target_room.exits[opposite_direction] == room_name, (
                    f"Room {target_room_name}'s {opposite_direction} exit should lead "
                    f"to {room_name}"
                )


def test_room_descriptions_not_empty():
    """Test that all rooms have non-empty descriptions"""
    for room_name, room_class in ROOM_CLASSES.items():
        room = room_class()
        assert len(room.description.strip()) > 0, f"Room {room_name} has empty description"


def test_room_names_match_class_names():
    """Test that room names match their expected values"""
    expected_names = {
        "MountainPath": "Mountain Path",
        "GreendaleGates": "Greendale Gates",
        "MainSquare": "Main Square",
        "MarketDistrict": "Market District",
        "SilverStagInn": "The Silver Stag Inn",
        "InnRooms": "Inn Rooms",
        "MerchantsWarehouse": "Merchant's Warehouse",
        "CastleApproach": "Castle Approach",
        "CastleCourtyard": "Castle Courtyard",
        "GreatHall": "Great Hall",
        "ResidentialQuarter": "Residential Quarter",
        "HealersHouse": "Healer's House",
        "HiddenLibrary": "Hidden Library",
        "ForestTransition": "Forest Transition",
        "ForestEntrance": "Forest Entrance",
        "AncientGrove": "Ancient Grove",
        "WhisperingGlade": "Whispering Glade",
        "HeartOfTheForest": "Heart of the Forest",
    }

    for class_name, room_class in ROOM_CLASSES.items():
        room = room_class()
        expected_name = expected_names[class_name]
        assert room.name == expected_name, (
            f"Room {class_name} should have name '{expected_name}', got '{room.name}'"
        )
