"""Unit tests for DragonsHall room in Act 3."""
from retroquest.act3.rooms.DragonsHall import DragonsHall
from retroquest.act3.items.DragonsScale import DragonsScale
from retroquest.act3.characters.AncientDragon import AncientDragon


def test_dragons_hall_init():
    """Test initialization of DragonsHall."""
    room = DragonsHall()
    assert room.name == "Dragon's Hall"
    assert "vast chamber" in room.description
    assert "massive coils" in room.description
    assert "Ancient Dragon" in room.description

    # Check items - dragon's scale should NOT be present initially
    item_names = [item.get_name() for item in room.items]
    assert "dragon's scale" not in item_names

    # Check character
    assert any(isinstance(char, AncientDragon) for char in room.characters)


def test_dragons_hall_exits():
    """Test exits from Dragon's Hall."""
    room = DragonsHall()
    exits = room.exits

    assert "west" in exits
    assert exits["west"] == "StillnessVestibule"


def test_dragons_scale_not_initially_in_room():
    """Test that dragon's scale is NOT initially in the room."""
    room = DragonsHall()

    # Dragon's scale should not be present initially
    dragons_scale = None
    for item in room.items:
        if isinstance(item, DragonsScale):
            dragons_scale = item
            break

    assert dragons_scale is None


def test_add_dragons_scale_dynamically():
    """Test that dragon's scale can be added dynamically to the room."""
    room = DragonsHall()

    # Initially no dragon's scale
    assert not any(isinstance(item, DragonsScale) for item in room.items)

    # Add dragon's scale
    dragons_scale = DragonsScale()
    room.add_item(dragons_scale)

    # Now it should be present
    assert any(isinstance(item, DragonsScale) for item in room.items)
    assert dragons_scale.can_be_carried_flag is True
