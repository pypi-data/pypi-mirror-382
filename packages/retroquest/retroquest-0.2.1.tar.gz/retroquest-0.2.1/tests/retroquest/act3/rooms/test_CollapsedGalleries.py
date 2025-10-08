"""Unit tests for CollapsedGalleries room in Act 3."""
from retroquest.engine.GameState import GameState
from retroquest.act3.rooms.CollapsedGalleries import CollapsedGalleries
from retroquest.act3.items.FallenRock import FallenRock
from retroquest.act3.items.ReinforcedBraces import ReinforcedBraces
from retroquest.act3.items.SupportStraps import SupportStraps
from retroquest.act3.items.WedgeBlocks import WedgeBlocks
from retroquest.act3.characters.Miners import Miners
from retroquest.act3.Act3StoryFlags import FLAG_ACT3_MINERS_RESCUE_COMPLETED


class DummyGameState:
    """Dummy game state for testing inventory and story flags."""

    def __init__(self, room):
        """Initialize with empty inventory and flag set."""
        self.inventory = []
        self.flags = set()
        self.current_room = room

    def set_story_flag(self, flag, value):
        """Set or unset a story flag."""
        if value:
            self.flags.add(flag)
        else:
            self.flags.discard(flag)

    def get_story_flag(self, flag):
        """Return True if the flag is set, else False."""
        return flag in self.flags


def test_collapsed_galleries_init():
    """Test initialization and properties of CollapsedGalleries room."""
    room = CollapsedGalleries()
    assert room.name == "Collapsed Galleries"
    assert any(isinstance(i, FallenRock) for i in room.items)
    # Miners should not be present initially - they appear after passage is freed
    assert not any(isinstance(c, Miners) for c in room.characters)
    assert "south" in room.exits and "west" in room.exits and "east" in room.exits


def test_miners_rescue_progression():
    """Test the full miners rescue progression from steps 22."""
    room = CollapsedGalleries()
    gs = GameState(room, {'room': room}, [])
    fallen_rock = room.items[0]  # Should be FallenRock

    # Initially, miners should not be present
    assert not any(isinstance(c, Miners) for c in room.characters)

    # Get tools
    braces = ReinforcedBraces()
    gs.add_item_to_inventory(braces)
    straps = SupportStraps()
    gs.add_item_to_inventory(straps)
    blocks = WedgeBlocks()
    gs.add_item_to_inventory(blocks)

    # Step 0: Examine the fallen rock first (required before stabilization)
    examine_result = fallen_rock.examine(gs)
    assert "massive pile of fallen rock" in examine_result
    assert "unstable" in examine_result and "trapped" in examine_result
    assert "reinforcement" in examine_result

    # Step 1: Use reinforced braces with fallen rock
    result1 = fallen_rock.use_with(gs, braces)
    assert "stabilizing the collapse" in result1
    assert braces not in gs.inventory  # Braces should be consumed

    # Step 2: Use support straps with fallen rock
    result2 = fallen_rock.use_with(gs, straps)
    assert "bind the reinforced braces securely" in result2
    assert straps not in gs.inventory  # Straps should be consumed

    # Step 3: Use wedge blocks with fallen rock (this should add miners to room)
    result3 = fallen_rock.use_with(gs, blocks)
    assert "freeing the blocked passage" in result3
    assert "trapped miners emerging" in result3
    assert blocks not in gs.inventory  # Blocks should be consumed

    # After freeing passage, miners should now be present in the room
    assert any(isinstance(c, Miners) for c in room.characters)
    miners = next(c for c in room.characters if isinstance(c, Miners))

    # Step 4: Talk to miners
    result4 = miners.talk_to(gs)
    assert "Thank the gods you found us" in result4
    assert gs.get_story_flag(FLAG_ACT3_MINERS_RESCUE_COMPLETED)


def test_get_exits_blocks_east_until_completed():
    """Test that east exit is blocked until miners rescue is completed."""
    room = CollapsedGalleries()
    gs = DummyGameState(room)
    # By default, east is hidden
    exits = room.get_exits(gs)
    assert "east" not in exits
    assert "south" in exits and "west" in exits
    # Set completion flag
    gs.set_story_flag(FLAG_ACT3_MINERS_RESCUE_COMPLETED, True)
    exits2 = room.get_exits(gs)
    assert "east" in exits2


def test_fallen_rock_requires_stabilization_first():
    """Test that support straps can't be used before stabilization."""
    fallen_rock = FallenRock()
    gs = DummyGameState(None)
    straps = SupportStraps()
    # Try straps before stabilization
    result = straps.use_with(gs, fallen_rock)
    assert "stabilize the collapse with braces" in result
