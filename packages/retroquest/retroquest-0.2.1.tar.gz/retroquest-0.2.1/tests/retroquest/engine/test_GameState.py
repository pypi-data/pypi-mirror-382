"""Unit tests for GameState: activation, updates, completion, inventory, and flags."""

import unittest
from engine.GameState import GameState

class DummyRoom:
    """Simple dummy room with a name used by GameState tests."""

    def __init__(self, name):
        """Initialize dummy room with the given name."""
        self.name = name
        self.items = []

class DummyQuest:
    """Dummy quest with configurable trigger and completion responses."""

    def __init__(self, name, description=False, completion=False):
        """Initialize dummy quest with configurable responses."""
        self.name = name
        self.description = description
        self.completion = completion

    def check_trigger(self, _game_state):
        """Return the configured trigger response."""
        return self.description

    def check_completion(self, _game_state):
        """Return the configured completion response."""
        return self.completion

    def is_main(self):
        """Return False as this is not a main quest."""
        return False

class TestGameState(unittest.TestCase):
    """Tests for GameState quest handling, inventory, and story flags."""

    def test_next_activated_quest(self):
        """Quest activation moves a triggered quest from non-activated to activated."""
        # Setup: quest1 triggers, quest2 does not
        self.gs.non_activated_quests = [self.quest1, self.quest2]
        activated = self.gs.next_activated_quest()
        self.assertEqual(activated, self.quest1)
        self.assertIn(self.quest1, self.gs.activated_quests)
        self.assertNotIn(self.quest1, self.gs.non_activated_quests)
        # No more triggers
        activated2 = self.gs.next_activated_quest()
        self.assertIsNone(activated2)

    def test_next_updated_quest(self):
        """Test quest update checking and next_updated_quest method."""
        # DummyQuest with check_update method
        class UpdateQuest(DummyQuest):
            """Dummy quest that can be updated."""
            def __init__(self, name, update=False):
                """Initialize an update-capable dummy quest with an update flag."""
                super().__init__(name)
                self.update = update
            def check_update(self, _game_state):
                """Return whether this dummy quest reports an update is available."""
                return self.update
        q1 = UpdateQuest("Q1", update=False)
        q2 = UpdateQuest("Q2", update=True)
        self.gs.activated_quests = [q1, q2]
        updated = self.gs.next_updated_quest()
        self.assertEqual(updated, q2)
        # No quest needs updating
        q2.update = False
        updated2 = self.gs.next_updated_quest()
        self.assertIsNone(updated2)

    def test_next_completed_quest(self):
        """Quest completion moves a completed quest from activated to completed."""
        # quest1 does not complete, quest2 does
        self.gs.activated_quests = [self.quest1, self.quest2]
        # Patch quest2 to complete
        self.quest2.completion = True
        def check_completion_true(_gs):
            """Return True to simulate quest completion for the patched quest."""
            return True
        self.quest2.check_completion = check_completion_true
        completed = self.gs.next_completed_quest()
        self.assertEqual(completed, self.quest2)
        self.assertIn(self.quest2, self.gs.completed_quests)
        self.assertNotIn(self.quest2, self.gs.activated_quests)
        # No more completions
        completed2 = self.gs.next_completed_quest()
        self.assertIsNone(completed2)

    def test_update_quest_string_return(self):
        """Test that update_quest returns formatted string for updated quests."""
        # Quest whose check_update returns True should produce formatted string
        class UpdatableQuest(DummyQuest):
            """Dummy quest that can be updated with description."""
            def __init__(self, name, description):
                """Initialize with name and description."""
                super().__init__(name, description)
            def check_update(self, _game_state):
                """Always return True for updates."""
                return True
            def is_main(self):
                """Declare this update as the main quest update."""
                return True
        uq = UpdatableQuest("Hero's Call", description="Answer the call")
        self.gs.activated_quests = [uq]
        update_str = self.gs.update_quest()
        self.assertIn("Hero's Call", update_str)
        self.assertIn("(main quest)", update_str)
        self.assertIn("Answer the call", update_str)

    def test_complete_quest_string_return(self):
        """Ensure completed quest string includes expected fragments."""
        class CompletableQuest(DummyQuest):
            """Dummy quest used to test completion string formatting."""
            def __init__(self, name, completion):
                """Initialize with a name and configured completion text."""
                super().__init__(name, description=False, completion=completion)
            def check_completion(self, _game_state):
                """Always indicate completion for this test quest."""
                return True
            def is_main(self):
                """Indicate this dummy is a side quest for the test."""
                return False
        cq = CompletableQuest("Find Relic", completion=True)
        cq.completion = "You have recovered the relic."
        self.gs.activated_quests = [cq]
        complete_str = self.gs.complete_quest()
        self.assertIn("Find Relic", complete_str)
        self.assertIn("(side quest)", complete_str)
        self.assertIn("relic", complete_str.lower())
        # Subsequent call returns None
        self.assertIsNone(self.gs.complete_quest())

    def test_is_quest_activated_and_completed(self):
        """Verify that activation and completion checks by name behave correctly."""
        self.gs.activated_quests = [self.quest1]
        self.assertTrue(self.gs.is_quest_activated("Quest1"))
        self.assertFalse(self.gs.is_quest_completed("Quest1"))
        self.gs.completed_quests = [self.quest2]
        self.assertTrue(self.gs.is_quest_completed("Quest2"))
        self.assertFalse(self.gs.is_quest_activated("Quest2"))

    def test_story_flag_overwrite(self):
        """Story flags can be set and then overwritten with new values."""
        self.gs.set_story_flag("door_open", True)
        self.assertTrue(self.gs.get_story_flag("door_open"))
        self.gs.set_story_flag("door_open", False)
        self.assertFalse(self.gs.get_story_flag("door_open"))

    def test_remove_item_more_than_exists(self):
        """Removing more items than present should only remove available count."""
        class DummyItem:
            """Minimal item type used for inventory removal tests."""
            def get_name(self):
                """Return the item's full name used in tests."""
                return "stone"

            def get_short_name(self):
                """Return the item's short name used in tests."""
                return "stn"
        for _ in range(2):
            self.gs.add_item_to_inventory(DummyItem())
        removed = self.gs.remove_item_from_inventory("stone", 5)
        self.assertEqual(removed, 2)
        self.assertEqual(self.gs.get_item_count("stone"), 0)

    def test_get_item_prefers_inventory_before_rooms(self):
        """Lookup should prefer inventory matches over identical room items."""
        # Same name item in inventory and room; inventory should be found first
        class DummyItem:
            """Simple dummy item with name accessors for lookup tests."""
            def __init__(self, name):
                """Initialize dummy item with given name."""
                self._n = name

            def get_name(self):
                """Return the dummy item's full name."""
                return self._n

            def get_short_name(self):
                """Return the dummy item's short name."""
                return self._n
        inv_item = DummyItem("amulet")
        room_item = DummyItem("amulet")
        room = DummyRoom("Chamber")
        room.items = [room_item]
        self.gs.add_item_to_inventory(inv_item)
        self.gs.all_rooms = {room.name: room}
        found = self.gs.get_item("amulet")
        self.assertIs(found, inv_item)
    def setUp(self):
        """Create a GameState with a test room and two dummy quests."""
        self.room = DummyRoom("TestRoom")
        self.quest1 = DummyQuest("Quest1", description=True, completion=False)
        self.quest2 = DummyQuest("Quest2", description=False, completion=True)
        self.gs = GameState(self.room, all_rooms=None, all_quests=[self.quest1, self.quest2])

    def test_mark_visited(self):
        """mark_visited should add the room's name to visited_rooms."""
        new_room = DummyRoom("AnotherRoom")
        self.gs.mark_visited(new_room)
        self.assertIn("AnotherRoom", self.gs.visited_rooms)

    def test_story_flag(self):
        """Setting and clearing a story flag should reflect in get_story_flag."""
        self.gs.set_story_flag("flag1", True)
        self.assertTrue(self.gs.get_story_flag("flag1"))
        self.gs.set_story_flag("flag1", False)
        self.assertFalse(self.gs.get_story_flag("flag1"))

    def test_inventory(self):
        """Basic inventory operations: add, has_item, remove by name."""
        class DummyItem:
            """Tiny inventory item exposing name accessors for tests."""
            def get_name(self):
                """Return inventory test item's full name."""
                return "item1"

            def get_short_name(self):
                """Return inventory test item's short name."""
                return "itm1"
        item = DummyItem()
        self.gs.add_item_to_inventory(item)
        self.assertTrue(self.gs.has_item("item1"))
        self.assertTrue(self.gs.has_item("itm1"))
        self.gs.remove_item_from_inventory("item1")
        self.assertFalse(self.gs.has_item("item1"))

    def test_multiple_items_inventory(self):
        """Test inventory batching functionality with multiple items of the same type."""
        class DummyItem:
            """Dummy item used to exercise multiple-items inventory behavior."""
            def __init__(self, name):
                """Store the provided name on the dummy item."""
                self.item_name = name

            def get_name(self):
                """Return the stored full name for the dummy item."""
                return self.item_name

            def get_short_name(self):
                """Return a short form of the item's name for tests."""
                return self.item_name[:3]

        # Add multiple items of the same type
        for _ in range(5):
            coin = DummyItem("coin")
            self.gs.add_item_to_inventory(coin)

        # Add multiple items of different types
        for _ in range(3):
            key = DummyItem("key")
            self.gs.add_item_to_inventory(key)

        # Add a single item
        sword = DummyItem("sword")
        self.gs.add_item_to_inventory(sword)

        # Test inventory summary
        summary = self.gs.get_inventory_summary()
        self.assertEqual(summary["coin"], 5)
        self.assertEqual(summary["key"], 3)
        self.assertEqual(summary["sword"], 1)

        # Test item counts
        self.assertEqual(self.gs.get_item_count("coin"), 5)
        self.assertEqual(self.gs.get_item_count("key"), 3)
        self.assertEqual(self.gs.get_item_count("sword"), 1)
        self.assertEqual(self.gs.get_item_count("nonexistent"), 0)

        # Test has_item with multiple items
        self.assertTrue(self.gs.has_item("coin"))
        self.assertTrue(self.gs.has_item("key"))
        self.assertTrue(self.gs.has_item("sword"))
        self.assertFalse(self.gs.has_item("potion"))

        # Test stats display with batching
        stats_output = self.gs.stats()
        self.assertIn("5 coin", stats_output)
        self.assertIn("3 key", stats_output)
        self.assertIn("sword", stats_output)  # Single item without count
        self.assertNotIn("1 sword", stats_output)  # Should not show count for single items

        # Test partial removal
        removed = self.gs.remove_item_from_inventory("coin", 2)
        self.assertEqual(removed, 2)
        self.assertEqual(self.gs.get_item_count("coin"), 3)

        # Test removing more than available
        removed = self.gs.remove_item_from_inventory("key", 5)
        self.assertEqual(removed, 3)  # Should only remove what's available
        self.assertEqual(self.gs.get_item_count("key"), 0)

        # Test remove all items of a type
        removed = self.gs.remove_all_items_from_inventory("coin")
        self.assertEqual(removed, 3)
        self.assertEqual(self.gs.get_item_count("coin"), 0)
        self.assertFalse(self.gs.has_item("coin"))

        # Verify only sword remains
        self.assertTrue(self.gs.has_item("sword"))
        self.assertEqual(len(self.gs.inventory), 1)

    def test_learn_spell_and_has_spell(self):
        """Learning a spell should register it and make it queryable by name."""
        class DummySpell:
            """Minimal spell object with name attribute for testing."""
            def __init__(self, name):
                """Initialize dummy spell with a name attribute."""
                self.name = name
        spell = DummySpell("fireball")
        self.gs.learn_spell(spell)
        self.assertTrue(self.gs.has_spell("fireball"))

    def test_stats(self):
        """Stats should include items, spells, visited rooms and return a string."""
        # Add some items and spells
        class DummyItem:
            """Tiny dummy item used in stats test."""
            def get_name(self):
                """Return the stats test item's full name."""
                return "item1"

            def get_short_name(self):
                """Return the stats test item's short name."""
                return "itm1"
        class DummySpell:
            """Tiny dummy spell exposing get_name used in stats."""
            def __init__(self, name):
                """Create a tiny dummy spell with the given name."""
                self.name = name

            def get_name(self):
                """Return the dummy spell's name."""
                return self.name
        self.gs.add_item_to_inventory(DummyItem())
        self.gs.learn_spell(DummySpell("fireball"))
        self.gs.set_story_flag("flag1", True)
        # Mark a room as visited
        self.gs.mark_visited(self.room)
        # Call stats and check output
        stats_output = self.gs.stats()
        self.assertIn("item1", stats_output)
        self.assertIn("fireball", stats_output)
        # self.assertIn("flag1", stats_output)
        self.assertIn("TestRoom", stats_output)
        # Check that the output is a string
        self.assertIsInstance(stats_output, str)

    def test_get_room_by_name(self):
        """get_room should lookup a room by name or return None if missing."""
        # Add another room to all_rooms and test lookup by name
        another_room = DummyRoom("AnotherRoom")
        self.gs.all_rooms = {self.room.name: self.room, another_room.name: another_room}
        self.assertEqual(self.gs.get_room("AnotherRoom"), another_room)
        # Test for a room that does not exist
        self.assertIsNone(self.gs.get_room("NonExistentRoom"))

    def test_get_item_inventory_and_room(self):
        """get_item should find items in inventory first, then in rooms, by name."""
        # Dummy item for inventory
        class DummyItem:
            """Inventory dummy for get_item tests."""
            def get_name(self):
                """Return the inventory dummy's full name for get_item tests."""
                return "item1"

            def get_short_name(self):
                """Return the inventory dummy's short name for get_item tests."""
                return "itm1"
        # Dummy item for room
        class DummyRoomItem:
            """Room dummy for get_item tests."""
            def get_name(self):
                """Return the room-dummy item's full name for get_item tests."""
                return "item2"

            def get_short_name(self):
                """Return the room-dummy item's short name for get_item tests."""
                return "itm2"
        item_inventory = DummyItem()
        item_room = DummyRoomItem()
        self.gs.add_item_to_inventory(item_inventory)
        # Patch all_rooms to be a dict for get_item
        room_with_item = DummyRoom("RoomWithItem")
        room_with_item.items = [item_room]
        self.gs.all_rooms = {self.room.name: self.room, room_with_item.name: room_with_item}
        # Test inventory (long and short name)
        self.assertEqual(self.gs.get_item("item1"), item_inventory)
        self.assertEqual(self.gs.get_item("itm1"), item_inventory)
        # Test room (long and short name)
        self.assertEqual(self.gs.get_item("item2"), item_room)
        self.assertEqual(self.gs.get_item("itm2"), item_room)
        # Test not found
        self.assertIsNone(self.gs.get_item("notfound"))

    def test_get_quest(self):
        """Ensure quests can be retrieved by name from game state lists."""
        # Should find quests by name (case-insensitive) in all quest lists
        self.gs.non_activated_quests = [self.quest1]
        self.gs.activated_quests = [self.quest2]
        completed_quest = DummyQuest("Quest3", description=True, completion=True)
        self.gs.completed_quests = [completed_quest]
        # Find in non_activated_quests
        self.assertEqual(self.gs.get_quest("Quest1"), self.quest1)
        self.assertEqual(self.gs.get_quest("quest1"), self.quest1)
        # Find in activated_quests
        self.assertEqual(self.gs.get_quest("Quest2"), self.quest2)
        # Find in completed_quests
        self.assertEqual(self.gs.get_quest("Quest3"), completed_quest)
        # Not found
        self.assertIsNone(self.gs.get_quest("NotAQuest"))

    def test_add_item_to_inventory_with_count(self):
        """Test that add_item_to_inventory works with count parameter."""
        from engine.Item import Item

        # Create test items
        coin = Item("coin", "A golden coin")
        sword = Item("sword", "A sharp sword")

        # Test default behavior (count=1)
        self.gs.add_item_to_inventory(sword)
        self.assertEqual(self.gs.get_item_count("sword"), 1)

        # Test adding multiple items with count parameter
        self.gs.add_item_to_inventory(coin, count=5)
        self.assertEqual(self.gs.get_item_count("coin"), 5)

        # Test adding more of the same item
        self.gs.add_item_to_inventory(coin, count=3)
        self.assertEqual(self.gs.get_item_count("coin"), 8)

        # Verify inventory summary
        summary = self.gs.get_inventory_summary()
        self.assertEqual(summary["coin"], 8)
        self.assertEqual(summary["sword"], 1)

        # Verify total inventory size
        self.assertEqual(len(self.gs.inventory), 9)  # 8 coins + 1 sword

    def test_remove_item_from_inventory_or_room(self):
        """Test removing items from inventory first, then from current room."""
        from engine.Item import Item

        # Create test items
        coin = Item("coin", "A golden coin")
        sword = Item("sword", "A sharp sword")

        # Add items to inventory
        self.gs.add_item_to_inventory(coin, count=3)
        self.gs.add_item_to_inventory(sword, count=1)

        # Add items to current room
        self.gs.current_room.items.append(Item("coin", "A golden coin"))
        self.gs.current_room.items.append(Item("coin", "A golden coin"))
        self.gs.current_room.items.append(Item("gem", "A precious gem"))

        # Test removing from inventory only (sufficient items available)
        removed = self.gs.remove_item_from_inventory_or_room("sword", 1)
        self.assertEqual(removed, 1)
        self.assertEqual(self.gs.get_item_count("sword"), 0)
        self.assertEqual(len(self.gs.current_room.items), 3)  # Room items unchanged

        # Test removing from inventory and room (not enough in inventory)
        removed = self.gs.remove_item_from_inventory_or_room("coin", 5)
        self.assertEqual(removed, 5)  # 3 from inventory + 2 from room
        self.assertEqual(self.gs.get_item_count("coin"), 0)
        self.assertEqual(len(self.gs.current_room.items), 1)  # Only gem left

        # Test removing more than available
        removed = self.gs.remove_item_from_inventory_or_room("gem", 3)
        self.assertEqual(removed, 1)  # Only 1 gem was available in room
        self.assertEqual(len(self.gs.current_room.items), 0)  # Room now empty

        # Test removing non-existent item
        removed = self.gs.remove_item_from_inventory_or_room("nonexistent", 1)
        self.assertEqual(removed, 0)

        # Test with short names
        potion = Item("Health Potion", "A red potion", short_name="potion")
        self.gs.add_item_to_inventory(potion)
        removed = self.gs.remove_item_from_inventory_or_room("potion", 1)
        self.assertEqual(removed, 1)
        self.assertEqual(self.gs.get_item_count("Health Potion"), 0)

    def test_remove_item_from_inventory_or_room_no_room_items(self):
        """Test removing items when current room has no items attribute."""
        from engine.Item import Item

        # Create a room without items attribute
        class RoomWithoutItems:
            """Test room that deliberately lacks an items attribute."""

            def __init__(self, name):
                """Initialize room with name but no items attribute."""
                self.name = name
                # Intentionally no items attribute

        room_without_items = RoomWithoutItems("Test Room")
        self.gs.current_room = room_without_items

        # Add item to inventory
        coin = Item("coin", "A golden coin")
        self.gs.add_item_to_inventory(coin, count=2)

        # Try to remove more items than in inventory - should handle gracefully
        removed = self.gs.remove_item_from_inventory_or_room("coin", 5)
        self.assertEqual(removed, 2)  # Only got 2 from inventory, room has no items
        self.assertEqual(self.gs.get_item_count("coin"), 0)


# if __name__ == "__main__":
#     unittest.main()
