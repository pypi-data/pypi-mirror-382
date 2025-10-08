"""Integration tests for Act 1: golden path and story progression."""

from act1.Act1 import Act1
from engine.Game import Game
from retroquest.act1.rooms.EliorsCottage import EliorsCottage
from retroquest.act1.rooms.VegetableField import VegetableField
from retroquest.act1.rooms.ChickenCoop import ChickenCoop
from retroquest.act1.rooms.VillageSquare import VillageSquare
from retroquest.act1.rooms.MirasHut import MirasHut
from retroquest.act1.rooms.BlacksmithsForge import BlacksmithsForge
from retroquest.act1.rooms.GeneralStore import GeneralStore
from retroquest.act1.rooms.VillageWell import VillageWell
from retroquest.act1.rooms.AbandonedShed import AbandonedShed
from retroquest.act1.rooms.OldMill import OldMill
from retroquest.act1.rooms.Riverbank import Riverbank
from retroquest.act1.rooms.ForestPath import ForestPath
from retroquest.act1.rooms.HiddenGlade import HiddenGlade
from retroquest.act1.rooms.VillageChapel import VillageChapel
from retroquest.act1.rooms.RoadToGreendale import RoadToGreendale
from retroquest.act1.quests.HintOfMagic import HintOfMagicQuest
from retroquest.act1.quests.CuriosityKilledTheCat import CuriosityKilledTheCatQuest
from retroquest.act1.quests.FishingExpedition import FishingExpeditionQuest
from retroquest.act1.quests.KnowYourVillage import KnowYourVillageQuest
from retroquest.act1.quests.LetThereBeLight import LetThereBeLightQuest
from retroquest.act1.quests.MagicForReal import MagicForRealQuest
from retroquest.act1.quests.MagnetFishingExpedition import MagnetFishingExpeditionQuest
from retroquest.act1.quests.OhDeerOhDeer import OhDeerOhDeerQuest
from retroquest.act1.quests.PreparingForTheRoad import PreparingForTheRoadQuest
from retroquest.act1.quests.FadedPhotograph import FadedPhotographQuest
from retroquest.act1.quests.LostLetter import LostLetterQuest
from retroquest.act1.quests.ShadowsOverWillowbrook import ShadowsOverWillowbrookQuest
from ..utils.utils import (check_character_in_room, check_current_room, check_quests,
                            execute_commands, check_item_in_inventory, check_item_in_room,
                            check_spell_known, check_story_flag)

# Room setup for integration test
ROOMS = {
    "EliorsCottage": EliorsCottage(),
    "VegetableField": VegetableField(),
    "ChickenCoop": ChickenCoop(),
    "VillageSquare": VillageSquare(),
    "MirasHut": MirasHut(),
    "BlacksmithsForge": BlacksmithsForge(),
    "GeneralStore": GeneralStore(),
    "VillageWell": VillageWell(),
    "AbandonedShed": AbandonedShed(),
    "OldMill": OldMill(),
    "Riverbank": Riverbank(),
    "ForestPath": ForestPath(),
    "HiddenGlade": HiddenGlade(),
    "VillageChapel": VillageChapel(),
    "RoadToGreendale": RoadToGreendale(),
}

# Quest setup for integration test
QUESTS = [
    HintOfMagicQuest(),
    CuriosityKilledTheCatQuest(),
    FishingExpeditionQuest(),
    KnowYourVillageQuest(),
    LetThereBeLightQuest(),
    MagicForRealQuest(),
    MagnetFishingExpeditionQuest(),
    OhDeerOhDeerQuest(),
    PreparingForTheRoadQuest(),
    FadedPhotographQuest(),
    ShadowsOverWillowbrookQuest(),
    LostLetterQuest()
]

def test_golden_path_act1_completion():
    """Test the complete golden path through Act 1 from start to finish."""
    # Setup Game
    act = Act1()
    act.music_file = ''
    game = Game([act])
    execute_commands(game, ['look'])

    # Step 1: Elior’s Cottage
    check_quests(game.state, ["Shadows Over Willowbrook", "Hint of Magic"])
    check_item_in_room(game.state.current_room, "bread", should_be_present=False)
    check_item_in_room(game.state.current_room, "Elior's Journal", should_be_present=False)
    execute_commands(game, ["use lantern"])
    check_item_in_room(game.state.current_room, "bread")
    check_item_in_room(game.state.current_room, "Elior's Journal")
    execute_commands(game, ["take bread", "talk to grandmother"])
    check_spell_known(game.state, "revive", should_be_present=False)
    check_item_in_inventory(game.state, "bread")
    check_item_in_room(game.state.current_room, "bread", should_be_present=False)
    check_quests(game.state, ["Shadows Over Willowbrook", "Hint of Magic"])
    execute_commands(game, ["use journal", "talk to grandmother"])
    check_spell_known(game.state, "revive")
    check_quests(game.state, ["Shadows Over Willowbrook", "Magic for real"])

    # Step 2: Vegetable Field
    execute_commands(game, ["go south", "take rusty hoe"])
    check_quests(game.state, ["Shadows Over Willowbrook", "Magic for real", "Know your village"])
    check_current_room(game.state, "Vegetable Field")
    check_item_in_inventory(game.state, "rusty hoe")
    check_item_in_room(game.state.current_room, "rusty hoe", should_be_present=False)

    execute_commands(game, ["use hoe", "take knife", "cast revive"])
    check_item_in_inventory(game.state, "coin")
    check_item_in_inventory(game.state, "dull knife")
    inventory_count_after_first_hoe_use = len(game.state.inventory)
    execute_commands(game, ["use hoe"])
    assert len(game.state.inventory) == inventory_count_after_first_hoe_use, \
        "Using hoe again should not add items to inventory"

    # Step 3: Chicken Coop
    execute_commands(game, ["go south", "use bread with chicken"])
    check_current_room(game.state, "Chicken Coop")
    check_item_in_inventory(game.state, "bread", should_be_present=False)
    check_item_in_room(game.state.current_room, "key")

    execute_commands(game, ["take key"])
    check_item_in_inventory(game.state, "key")

    execute_commands(game, ["take egg"])
    check_item_in_inventory(game.state, "egg")
    check_item_in_room(game.state.current_room, "egg", should_be_present=False)

    # Step 4: Village Square
    execute_commands(game, ["go north", "go north", "go east"])
    check_current_room(game.state, "Village Square")
    execute_commands(game, ["take bucket", "talk to villager"])
    check_item_in_inventory(game.state, "bucket")

    # Step 5: Village Well
    execute_commands(game, ["go west", "go south", "go east"])
    check_current_room(game.state, "Village Well")
    execute_commands(game, ["examine well", "use bucket with well"])
    check_item_in_inventory(game.state, "bucket (full)")

    # Step 6: Blacksmith's Forge
    execute_commands(game, ["go east"])
    check_current_room(game.state, "Blacksmith's Forge")
    execute_commands(game, ["talk to blacksmith", "give coin to blacksmith"])
    check_item_in_inventory(game.state, "coin", should_be_present=False)
    check_item_in_inventory(game.state, "dull knife", should_be_present=False)
    check_item_in_inventory(game.state, "sharp knife")

    # Step 7: Vegetable Field
    execute_commands(game, ["go west", "go west", "use hoe"])
    check_current_room(game.state, "Vegetable Field")
    check_item_in_inventory(game.state, "coin")

    # Step 7.5: Visit Mira's Hut for encouragement and hints
    execute_commands(game, ["go north", "go east", "go north"])
    check_current_room(game.state, "Mira's Hut")
    # Mira should be present in the room
    check_character_in_room(game.state.current_room, "mira", should_be_present=True)
    # Talk to Mira for encouragement and hints
    execute_commands(game, ["talk to mira"])
    # No new items or spells are expected at this point, but ensure the player remains on the correct quest path
    check_quests(game.state, ["Shadows Over Willowbrook", "Magic for real", "Know your village"])

    # Step 8: General Store - Buy Rope
    execute_commands(game, ["go south", "go east"]) # Veg Field -> Village Square -> General Store
    check_current_room(game.state, "General Store")
    execute_commands(game, ["take apple", "take rope", "take matches"]) # Added "take apple"
    check_item_in_inventory(game.state, "apple", should_be_present=False) #Cannot be in inventory yet, just in room
    check_item_in_inventory(game.state, "rope", should_be_present=False) #Cannot be in inventory yet, just in room
    check_item_in_inventory(game.state, "matches", should_be_present=False) #Cannot be in inventory yet, just in room
    execute_commands(game, ["talk to shopkeeper", "buy rope from shopkeeper"]) # Added "take apple"
    check_item_in_inventory(game.state, "apple") # Added check for apple
    check_item_in_inventory(game.state, "rope")
    check_item_in_inventory(game.state, "coin", should_be_present=False)

    # Step 9: Abandoned Shed - Use Key
    # Path: General Store (current) -> Village Square -> Village Well -> Abandoned Shed
    execute_commands(game, ["go south", "go west", "go south"])
    check_quests(game.state, ["Shadows Over Willowbrook", "Magic for real", "Know your village", "Curiosity killed the cat"])
    check_current_room(game.state, "Abandoned Shed")
    check_item_in_room(game.state.current_room, "mysterious box", should_be_present=False) # Box is not present yet

    execute_commands(game, ["search"]) # Search does not reveals items since door is locked
    check_item_in_room(game.state.current_room, "fishing rod", should_be_present=False)
    check_item_in_room(game.state.current_room, "magnet", should_be_present=False)

    check_quests(game.state, ["Shadows Over Willowbrook", "Magic for real", "Know your village", "Curiosity killed the cat"])
    execute_commands(game, ["use key with door"]) # Changed: Assumes 'use key' unlocks the shed door
    check_quests(game.state, ["Shadows Over Willowbrook", "Magic for real", "Know your village"])
    check_item_in_inventory(game.state, "key", should_be_present=False) # Key is used up or its state changes
    check_item_in_room(game.state.current_room, "mysterious box") # Box is present

    execute_commands(game, ["search"]) # Search reveals items
    check_item_in_room(game.state.current_room, "fishing rod") # Fishing rod is now visible/obtainable
    check_item_in_room(game.state.current_room, "magnet") # Magnet is now visible/obtainable

    execute_commands(game, ["take fishing rod", "take magnet"]) # Take both items

    check_item_in_inventory(game.state, "fishing rod")
    check_item_in_room(game.state.current_room, "fishing rod", should_be_present=False)

    check_item_in_inventory(game.state, "magnet")
    check_item_in_room(game.state.current_room, "magnet", should_be_present=False)

    # Step 10: Old Mill - Use Rope, Take Millstone Fragment
    # Path: Abandoned Shed (current) -> Old Mill
    execute_commands(game, ["go south"])
    check_current_room(game.state, "Old Mill")

    execute_commands(game, ["use rope with mechanism"]) # Assuming "use rope" is enough, and it interacts with the mechanism
    check_item_in_inventory(game.state, "rope", should_be_present=False)
    check_item_in_room(game.state.current_room, "millstone fragment")

    execute_commands(game, ["take millstone fragment"])
    check_item_in_inventory(game.state, "millstone fragment")
    check_item_in_room(game.state.current_room, "millstone fragment", should_be_present=False)

    # Step 11: Return to Blacksmith's Forge
    # Path: Old Mill (current) -> Abandoned Shed -> Village Well -> Blacksmith's Forge
    execute_commands(game, ["go north", "go north", "go east"])
    check_current_room(game.state, "Blacksmith's Forge")

    check_quests(game.state, ["Shadows Over Willowbrook", "Magic for real", "Know your village"])
    execute_commands(game, ["give millstone fragment to blacksmith"])
    check_item_in_inventory(game.state, "millstone fragment", should_be_present=False)
    check_quests(game.state, ["Shadows Over Willowbrook", "Magic for real", "Know your village", "Oh deer, oh deer"])

    # Step 12: Riverbank
    # Path: Blacksmith's Forge (current) -> Village Well -> Abandoned Shed -> Old Mill -> Riverbank
    execute_commands(game, ["go west", "go south", "go south", "go east"])
    check_current_room(game.state, "Riverbank")

    execute_commands(game, ["use fishing rod with river"])
    check_item_in_inventory(game.state, "fish", should_be_present=False) # Fish is not in inventory as player cannot fish

    execute_commands(game, ["talk to fisherman"])
    check_quests(game.state, ["Shadows Over Willowbrook", "Magic for real", "Know your village", "Oh deer, oh deer", "Fishing expedition"])
    # Fisherman teaches fishing - no direct item/spell yet, but sets up next action
    execute_commands(game, ["use fishing rod with river"])
    check_item_in_inventory(game.state, "fish")

    check_quests(game.state, ["Shadows Over Willowbrook", "Magic for real", "Know your village", "Oh deer, oh deer", "Fishing expedition"])
    execute_commands(game, ["give fish to fisherman"])
    check_item_in_inventory(game.state, "fish", should_be_present=False)
    check_spell_known(game.state, "purify")
    check_quests(game.state, ["Shadows Over Willowbrook", "Magic for real", "Know your village", "Oh deer, oh deer"])

    # Step 13: Forest Path
    # Path: Riverbank (current) -> Forest Path
    execute_commands(game, ["go south"])
    check_current_room(game.state, "Forest Path")
    # Vines should be in the room initially
    check_item_in_room(game.state.current_room, "vines", should_be_present=True)
    check_item_in_room(game.state.current_room, "stick", should_be_present=False) # Stick is not present yet
    check_item_in_inventory(game.state, "sharp knife") # Elior has the sharp knife

    execute_commands(game, ["use sharp knife with vines"])
    # Vines should be removed from the room
    check_item_in_room(game.state.current_room, "vines", should_be_present=False)
    # Sharp Knife should be removed from inventory (it breaks)
    check_item_in_inventory(game.state, "sharp knife", should_be_present=False)
    # Stick should be added to the room
    check_item_in_room(game.state.current_room, "stick", should_be_present=True)

    execute_commands(game, ["take stick"])
    check_item_in_inventory(game.state, "stick")
    check_item_in_room(game.state.current_room, "stick", should_be_present=False)

    # Step 14: Hidden Glade
    # Path: Forest Path (current) -> Hidden Glade
    execute_commands(game, ["go south"])
    check_current_room(game.state, "Hidden Glade")
    # Deer and Rare Flower should not be present initially
    check_character_in_room(game.state.current_room, "deer", should_be_present=False)
    check_item_in_room(game.state.current_room, "rare flower", should_be_present=False)

    # Elior rests, and if deer_can_be_observed is true (set by Blacksmith), Deer and Rare Flower appear
    # The flag deer_can_be_observed was set in step 11.
    check_quests(game.state, ["Shadows Over Willowbrook", "Magic for real", "Know your village", "Oh deer, oh deer"])
    execute_commands(game, ["rest"])
    check_character_in_room(game.state.current_room, "deer", should_be_present=True)
    check_item_in_room(game.state.current_room, "rare flower", should_be_present=True)
    check_quests(game.state, ["Shadows Over Willowbrook", "Magic for real", "Know your village"])

    execute_commands(game, ["take rare flower"])
    check_item_in_inventory(game.state, "rare flower")
    check_item_in_room(game.state.current_room, "rare flower", should_be_present=False)
    # Deer remains in the room
    check_character_in_room(game.state.current_room, "deer", should_be_present=True)

    # Step 15: Village Chapel (First Visit - Part 1)
    # Path: Hidden Glade (current) -> Village Chapel
    execute_commands(game, ["go south"])
    check_current_room(game.state, "Village Chapel")
    check_item_in_room(game.state.current_room, "candle") # Candle should be in the chapel

    execute_commands(game, ["talk to priest"]) # Priest mentions needing matches
    check_quests(game.state, ["Shadows Over Willowbrook", "Magic for real", "Know your village", "Let there be light"])

    # Step 16: General Store (Visit for Matches)
    # Path: Village Chapel (current) -> Hidden Glade -> Forest Path -> Riverbank -> Old Mill -> Abandoned Shed -> Village Well -> Blacksmith's Forge -> General Store
    execute_commands(game, ["go north", "go north", "go north", "go west", "go north", "go north", "go east", "go north"])
    check_current_room(game.state, "General Store")

    check_item_in_room(game.state.current_room, "matches") # Matches in room
    execute_commands(game, ["talk to shopkeeper"]) # Ask for matches
    check_item_in_inventory(game.state, "matches") # Matches obtained
    check_item_in_room(game.state.current_room, "matches", should_be_present=False) # Matches not in room

    # Step 17: Village Chapel (First Visit - Part 2)
    # Path: General Store (current) -> Blacksmith's Forge -> Village Well -> Abandoned Shed -> Old Mill -> Riverbank -> Forest Path -> Hidden Glade -> Village Chapel
    execute_commands(game, ["go south", "go west", "go south", "go south", "go east", "go south", "go south", "go south"])
    check_current_room(game.state, "Village Chapel")

    # Pre-check: locket should not be visible yet
    check_item_in_room(game.state.current_room, "locket", should_be_present=False)
    check_item_in_inventory(game.state, "matches") # Ensure matches are in inventory

    check_quests(game.state, ["Shadows Over Willowbrook", "Magic for real", "Know your village", "Let there be light"])
    execute_commands(game, ["use candle with matches"]) # Using candle with matches should reveal the locket
    check_item_in_room(game.state.current_room, "locket") # Locket is now visible
    check_quests(game.state, ["Shadows Over Willowbrook", "Magic for real", "Know your village"])

    execute_commands(game, ["take locket"])
    check_item_in_inventory(game.state, "locket")
    check_item_in_room(game.state.current_room, "locket", should_be_present=False)
    check_spell_known(game.state, "bless")

    # Step 18: Return to Mira’s Hut
    # Path: Village Chapel (current) -> Hidden Glade -> Forest Path -> Riverbank -> Old Mill -> Abandoned Shed -> Village Well -> Village Square -> Mira's Hut
    execute_commands(game, ["go north", "go north", "go north", "go west", "go north", "go north", "go east", "go north", "go west", "go north"])
    check_current_room(game.state, "Mira's Hut")

    check_quests(game.state, ["Shadows Over Willowbrook", "Magic for real", "Know your village"])
    execute_commands(game, ["give rare flower to mira"])
    check_item_in_inventory(game.state, "rare flower", should_be_present=False)
    check_spell_known(game.state, "heal")
    check_spell_known(game.state, "unlock")
    check_spell_known(game.state, "light")
    check_story_flag(game.state, "magic_fully_unlocked", True)
    check_quests(game.state, ["Shadows Over Willowbrook", "Know your village", "Preparing for the road"])

    # Step 19: Return to Abandoned Shed (Second Visit)
    # Path: Mira's Hut (current) -> Village Square -> Elior's Cottage -> Vegetable Field -> Village Well -> Abandoned Shed
    execute_commands(game, ["go south", "go west", "go south", "go east", "go south"])
    check_current_room(game.state, "Abandoned Shed")
    # Box should be in the room from the first visit
    check_item_in_room(game.state.current_room, "mysterious box")

    # Make sure the box is locked initially
    mysterious_box = game.find_item("mysterious box", look_in_inventory=False, look_in_room=True)
    assert mysterious_box is not None, "Mysterious Box not found in Abandoned Shed"
    assert mysterious_box.locked, "Mysterious Box should be locked initially"

    execute_commands(game, ["cast unlock on mysterious box"])
    assert not mysterious_box.locked, "Mysterious Box should be unlocked after casting Unlock spell"
    check_item_in_room(game.state.current_room, "map", should_be_present=False) # Map is still in the box

    execute_commands(game, ["open mysterious box"])
    check_item_in_inventory(game.state, "map")
    check_item_in_room(game.state.current_room, "map", should_be_present=False) # Map is now in inventory

    # Step 20: Return to Vegetable Field
    # Path: Abandoned Shed (current) -> Village Well -> Vegetable Field
    execute_commands(game, ["go north", "go west"])
    check_current_room(game.state, "Vegetable Field")
    # Withered carrot should be present in the room from the start if not taken
    # Or, if it was taken earlier and not revivable then, it might be in inventory.
    # Design doc: "Withered carrot (Available in Vegetable Field from start)"
    # Design doc: Step 2: "Attempt to cast revive (fails, but hints at magic)" - implies it might have been taken.
    # Let's assume it was left in the room, or if taken, it's still "Withered carrot".
    # For the test, we need to ensure it's targetable. If it was taken, the command would be `cast revive on Withered carrot` (targeting inventory).
    # If it's in the room, it might be `cast revive on Withered carrot` (targeting room item).
    # The design doc for step 18 says: "Cast revive on the Withered carrot." - not specifying location.
    # Let's assume the game logic handles finding the Withered Carrot either in room or inventory.
    # For a clean test, let's ensure it's in the room first if it wasn't picked up.
    # However, the initial setup of VegetableField likely places it. If player took it in step 2, it's in inventory.

    # To make this test robust, we should check if it's in inventory first, then room.
    # Or, rely on the game's `cast` command to find it.
    # The `RoomsAct1.md` states `Withered carrot (start)` for Vegetable Field items.
    # It's not explicitly taken in the Golden Path until it's revived.
    # Let's assume it's in the room for this test.
    check_item_in_room(game.state.current_room, "Withered carrot")

    execute_commands(game, ["cast revive on Withered carrot"])
    check_item_in_room(game.state.current_room, "Withered carrot", should_be_present=False) # And removed from room
    check_item_in_room(game.state.current_room, "Fresh Carrot", should_be_present=True) # Carrot should now be present after revival

    execute_commands(game, ["take carrot"])
    check_item_in_inventory(game.state, "fresh carrot")
    check_item_in_room(game.state.current_room, "fresh carrot", should_be_present=False) # And removed from room

    # Step 21: Return to Village Well & Retrieve Shiny Ring
    # Path: Vegetable Field (current) -> Village Well
    execute_commands(game, ["go east"])
    check_current_room(game.state, "Village Well")

    # Ensure items for fishing the ring are present before combination
    check_item_in_inventory(game.state, "fishing rod")
    check_item_in_inventory(game.state, "magnet")
    check_item_in_inventory(game.state, "stick")

    # Combine Fishing Rod with Magnet
    execute_commands(game, ["use fishing rod with magnet"])
    check_item_in_inventory(game.state, "fishing rod", should_be_present=False)
    check_item_in_inventory(game.state, "magnet", should_be_present=False)
    check_item_in_inventory(game.state, "magnetic fishing rod")
    check_quests(game.state, ["Shadows Over Willowbrook", "Know your village", "Preparing for the road", "Magnet fishing expedition"])

    # Combine Magnetic Fishing Rod with Stick
    execute_commands(game, ["use magnetic fishing rod with stick"])
    check_item_in_inventory(game.state, "magnetic fishing rod", should_be_present=False)
    check_item_in_inventory(game.state, "stick", should_be_present=False)
    check_item_in_inventory(game.state, "extended magnetic fishing rod")

    # Test: Attempt to use extended magnetic fishing rod BEFORE purifying the well
    execute_commands(game, ["use extended magnetic fishing rod with well"])
    check_item_in_inventory(game.state, "shiny ring", should_be_present=False) # Ring should not be obtained
    check_item_in_inventory(game.state, "extended magnetic fishing rod") # Rod should still be in inventory

    check_quests(game.state, ["Shadows Over Willowbrook", "Know your village", "Magnet fishing expedition", "Preparing for the road"])
    execute_commands(game, ["cast purify on well", "use extended magnetic fishing rod with well"])
    check_item_in_inventory(game.state, "shiny ring") # Ring is now in inventory
    check_item_in_inventory(game.state, "extended magnetic fishing rod", should_be_present=False) # Rod is consumed or disappears
    check_quests(game.state, ["Shadows Over Willowbrook", "Know your village", "Preparing for the road"])

    # Step 22: Return to Hidden Glade (Second Visit)
    execute_commands(game, ["go south", "go south", "go east", "go south", "go south"])
    check_current_room(game.state, "Hidden Glade")

    execute_commands(game, ["cast light"])
    check_spell_known(game.state, "grow")

    # Step 23: Return to Forest Path
    # Path: Hidden Glade (current) -> Forest Path
    execute_commands(game, ["go north"])
    check_current_room(game.state, "Forest Path")
    # Casting grow on bush should make wild berries appear in the room.
    check_item_in_room(game.state.current_room, "wild berries", should_be_present=False) # Not there before casting

    execute_commands(game, ["cast grow on bush"]) # Or "cast grow spell"
    check_item_in_room(game.state.current_room, "wild berries") # Should be present now

    execute_commands(game, ["take wild berries"])
    check_item_in_inventory(game.state, "wild berries")
    check_item_in_room(game.state.current_room, "wild berries", should_be_present=False) # Taken from room

    # Step 24: Return to Elior's Cottage
    # Path: Forest Path (current) -> Riverbank -> Old Mill -> Abandoned Shed -> Village Well -> Vegetable Field -> Elior's Cottage
    execute_commands(game, ["go north", "go west", "go north", "go north", "go west", "go north"])
    check_current_room(game.state, "Elior's Cottage")
    check_item_in_inventory(game.state, "locket") # Locket should still be there from Step 15

    execute_commands(game, ["give locket to grandmother"])
    check_item_in_inventory(game.state, "locket", should_be_present=False)
    check_item_in_inventory(game.state, "travel cloak")

    # Step 25: Village Chapel (Prepare for Journey)
    execute_commands(game, ["go south", "go east", "go south", "go south", "go east", "go south", "go south", "go south"])
    check_current_room(game.state, "Village Chapel")
    execute_commands(game, ["cast bless"])
    check_story_flag(game.state, "journey_bless_completed", True)

    # Step 26: Road to Greendale (Interactions)
    # Path: Village Chapel (current) -> Road to Greendale
    check_quests(game.state, ["Shadows Over Willowbrook", "Know your village", "Preparing for the road"])
    execute_commands(game, ["go east"])
    check_quests(game.state, ["Shadows Over Willowbrook", "Preparing for the road"])
    check_current_room(game.state, "Road to Greendale")
    check_item_in_inventory(game.state, "shiny ring") # Ensure shiny ring is present

    execute_commands(game, ["give shiny ring to merchant"]) # Assumes merchant is present
    check_item_in_inventory(game.state, "shiny ring", should_be_present=False)
    check_item_in_inventory(game.state, "wandering boots")
    check_quests(game.state, ["Shadows Over Willowbrook", ])

    # Step 27: Return to Mira’s Hut (Final Visit)
    # Path: Road to Greendale (current) -> Village Chapel -> Hidden Glade -> Forest Path -> Riverbank -> Old Mill -> Abandoned Shed -> Village Well -> Village Square -> Mira's Hut
    execute_commands(game, ["go west", "go north", "go north", "go north", "go west", "go north", "go north", "go west", "go north", "go east", "go north"])
    check_current_room(game.state, "Mira's Hut")
    # Verify all quest items are present before talking to Mira
    check_item_in_inventory(game.state, "travel cloak")
    # Bless was cast, assume it fulfills "Magical protection"
    check_item_in_inventory(game.state, "wild berries")
    check_item_in_inventory(game.state, "apple")
    check_item_in_inventory(game.state, "egg")
    check_item_in_inventory(game.state, "fresh carrot")
    check_item_in_inventory(game.state, "wandering boots")
    check_item_in_inventory(game.state, "map")
    # Verify all spells are known
    check_spell_known(game.state, "revive")
    check_spell_known(game.state, "purify")
    check_spell_known(game.state, "bless")
    check_spell_known(game.state, "heal")
    check_spell_known(game.state, "unlock")
    check_spell_known(game.state, "light")
    check_spell_known(game.state, "grow")
    # Verify that bless is cast
    check_story_flag(game.state, "journey_bless_completed", True)

    execute_commands(game, ["talk to mira"])
    check_item_in_inventory(game.state, "ancient amulet")

    # Step 28: Road to Greendale (Departure)
    execute_commands(game, ["go south", "go west", "go south", "go east", "go south", "go south", "go east", "go south", "go south", "go south", "go east"])
    check_current_room(game.state, "Road to Greendale")
    check_item_in_inventory(game.state, "map")
    check_item_in_inventory(game.state, "ancient amulet") # Ensure amulet is still there

    # This command should ideally trigger an Act I completion state.
    # We'll check for the command execution. Further checks depend on how game handles act completion.
    execute_commands(game, ["use map"])
    # Final check: Act I should be completed
    assert game.acts[game.current_act].is_completed(game.state), "Act I is not marked as completed."

