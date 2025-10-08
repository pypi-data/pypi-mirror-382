"""Integration tests for Act 3: golden path and key interactions."""

from typing import Optional
from retroquest.act3.Act3 import Act3
from retroquest.engine.Game import Game
from retroquest.act3.Act3StoryFlags import (
    FLAG_ACT3_MAIN_STARTED,
    FLAG_ACT3_MIRRORS_OF_EMBER_LIGHT_COMPLETED,
    FLAG_ACT3_BREATH_OF_THE_MOUNTAIN_COMPLETED,
    FLAG_ACT3_TIDEWARD_SIGILS_COMPLETED,
    FLAG_ACT3_MINERS_RESCUE_COMPLETED,
    FLAG_ACT3_OATH_OF_STILLNESS_COMPLETED,
    FLAG_ACT3_DRAGONS_MEMORY_RECEIVED,
    FLAG_ACT3_DRAGON_OATH_SPOKEN,
    FLAG_ACT3_OATH_SCROLLS_EXAMINED,
    FLAG_ACT3_LIFELIGHT_ELIXIR_CREATED,
    FLAG_ACT3_FORTRESS_GATES_EXAMINED,
)
from ..utils.utils import (
    check_character_in_room,
    check_current_room,
    check_item_in_room,
    check_quests,
    check_story_flag,
    execute_commands,
    check_item_in_inventory,
    check_item_count_in_inventory
)

class TestAct3Integration:
    """Integration tests for Act 3."""
    act3: Optional[Act3] = None
    game: Optional[Game] = None

    def setup_method(self):
        """Set up test fixtures."""
        self.act3 = Act3()
        self.act3.music_file = ''
        self.game = Game([self.act3])

    def test_act3_initialization(self):
        """Test that Act 3 initializes correctly."""
        assert self.act3 is not None
        assert isinstance(self.act3.rooms, dict)
        assert isinstance(self.act3.quests, list)
        assert self.act3.get_act_intro() is not None

    def test_game_with_act3(self):
        """Test that Game can be initialized with Act 3."""
        assert self.game is not None
        assert len(self.game.acts) == 1
        assert self.game.acts[0] == self.act3

    def test_golden_path_act3_completion(self):
        """Run the Act 3 golden path and assert expected progressions."""
        game = self.game

        # Start in Mira's Hut with Mira present
        check_current_room(game.state, "Mira's Hut")
        check_character_in_room(game.state.current_room, 'mira', True)

        # First talk: start main quest (The Three Virtues)
        result = execute_commands(game, ['talk to mira'])
        check_story_flag(game.state, FLAG_ACT3_MAIN_STARTED, True)
        assert 'three relics' in result.lower()
        # Ensure quest is activated (helpers auto-flush activations)
        check_quests(game.state, ['The Three Virtues'])

        # Examine note to start another quest
        result = execute_commands(game, ['examine keepsake note'])
        check_quests(game.state, ['Echoes of the Hidden Bond', 'The Three Virtues'])

        # Second talk: teleport to Tidal Causeway (Sunken Ruins entry) with companions
        # Cast light to find key
        result = execute_commands(game, ['talk to mira'])
        check_current_room(game.state, 'Tidal Causeway')
        check_character_in_room(game.state.current_room, 'mira', True)
        check_character_in_room(game.state.current_room, 'sir cedric', True)
        check_item_in_inventory(game.state, 'Rusted Locker Key', False)
        result = execute_commands(game, ['cast light'])
        assert 'shadow' in result.lower() and 'hollow' in result.lower() and'key' in result.lower()
        # Ensure rusted key present
        check_item_in_room(game.state.current_room, 'Rusted Locker Key', True)
        result = execute_commands(game, ['take rusted locker key'])
        check_item_in_inventory(game.state, 'Rusted Locker Key', True)
        check_item_in_room(game.state.current_room, 'Rusted Locker Key', False)

        # Step 3: move north to Shoreline Markers => should activate Tideward Sigils
        execute_commands(game, ['north'])
        check_current_room(game.state, 'Shoreline Markers')
        # Reveal the runes so the Tideward Sigils started flag is set
        execute_commands(game, ['search'])
        # Newly activated side quest should now be active alongside the main quest
        check_quests(game.state, ['Echoes of the Hidden Bond', 'The Three Virtues',
                                  'Tideward Sigils'])
        # Search/examine/take runes
        combined = execute_commands(game, ['search', 'examine steles', 'take moon rune shards'])
        assert 'moon' in combined.lower() or 'shard' in combined.lower()
        check_item_in_inventory(game.state, 'Moon Rune Shards', True)
        again = execute_commands(game, ['search'])
        assert 'already' in again.lower()

        # Step 5: Outer Wards — purify and set sigil; completes Tideward Sigils
        execute_commands(game, ['east'])
        check_current_room(game.state, 'Outer Wards')
        purify_result = execute_commands(game, ['cast purify on pillars'])
        assert any(k in purify_result.lower() for k in ['cleanse', 'rinse', 'cleansed'])
        use_result = execute_commands(game, ['use moon rune shards with pillars'])
        assert 'sigil' in use_result.lower()
        check_story_flag(game.state, FLAG_ACT3_TIDEWARD_SIGILS_COMPLETED, True)
        # Quest should be marked completed
        check_quests(game.state, ['Echoes of the Hidden Bond', 'The Three Virtues'])

        # Step 6: Removed

        # Step 7: Collapsed Pier (Vault) — key fails, cast unlock, open locker,
        # take three prism lanterns
        # Give the hint by examining the locker
        execute_commands(game, ['east'])
        check_current_room(game.state, 'Collapsed Pier')
        exam = execute_commands(game, ['examine locker'])
        assert 'fused' in exam.lower() or 'lock' in exam.lower()
        # Try the key and fail
        fail_key = execute_commands(game, ['use rusted locker key with locker'])
        assert 'too corroded' in fail_key.lower() or 'jams in the mechanism' in fail_key.lower()
        # Cast unlock on locker
        unlocked = execute_commands(game, ['cast unlock on locker'])
        assert ('locker' in unlocked.lower() and
                ('click' in unlocked.lower() or 'release' in unlocked.lower()))
        # Open locker and take all lanterns
        opened = execute_commands(game, ['open locker'])
        assert 'prism lantern' in opened.lower()
        # Collect three lanterns
        execute_commands(game, ['take prism lantern', 'take prism lantern', 'take prism lantern'])
        check_item_count_in_inventory(game.state, 'Prism Lantern', 3)

        # Step 8: Submerged Antechamber — navigate, mount lanterns and cast light
        # Move from Collapsed Pier back toward the Outer Wards and the submerged
        # antechamber where lanterns are mounted.
        execute_commands(game, ['west'])
        check_current_room(game.state, 'Outer Wards')
        execute_commands(game, ['south'])
        check_current_room(game.state, 'Submerged Antechamber')
        # Reveal the lantern brackets in the antechamber, then mount lanterns
        search_result = execute_commands(game, ['search'])
        assert 'bracket' in search_result.lower() or 'brackets' in search_result.lower()
        # Mount three lanterns to brackets
        execute_commands(game, ['use prism lantern with lantern bracket'])
        execute_commands(game, ['use prism lantern with lantern bracket'])
        execute_commands(game, ['use prism lantern with lantern bracket'])
        # After mounts, there should be no more prism lanterns in inventory
        check_item_count_in_inventory(game.state, 'Prism Lantern', 0)
        # Cast light to reveal the path
        light_result = execute_commands(game, ['cast light'])
        assert 'path' in light_result.lower() or 'lanterns' in light_result.lower()
        # After lighting, head west to the Tidal Causeway
        execute_commands(game, ['west'])
        check_current_room(game.state, 'Tidal Causeway')

        # Step 9: Tidal Causeway — examine mural, take Sea-Sealed Letter
        execute_commands(game, ['west'])
        check_current_room(game.state, 'Tidal Causeway')
        mural_reveal = execute_commands(game, ['examine mural'])
        assert 'reliquary' in mural_reveal.lower() or 'sea-sealed letter' in mural_reveal.lower()
        execute_commands(game, ['take sea-sealed letter', 'examine sea-sealed letter'])
        check_item_in_inventory(game.state, 'Sea-Sealed Letter', True)

        # Step 10: Sanctum — speak vow, then take crystal
        execute_commands(game, ['east', 'east'])
        check_current_room(game.state, 'Sanctum of the Tide')
        vow = execute_commands(game, ['say myself to tide-born guardian'])
        assert ('vow' in vow.lower() or 'waters draw back' in vow.lower() or
                'you may now take' in vow.lower())
        execute_commands(game, ['take crystal of light'])
        check_item_in_inventory(game.state, 'crystal of light', True)

        # Step 11: Talk to Mira to teleport to Mount Ember
        execute_commands(game, ['w', 'w', 'talk to mira'])
        check_current_room(game.state, 'Lower Switchbacks')

        # Step 12: Lower Switchbacks — talk to Ash Scholar to receive a brass mirror
        # Inspect the Emberwater Canteen for lore and a possible mirror hint
        examine_canteen = execute_commands(game, ['examine emberwater canteen'])
        assert ('expedition' in examine_canteen.lower() or
                'brass' in examine_canteen.lower() or 'canteen' in examine_canteen.lower())
        examine_canteen = execute_commands(game, ['take brass mirror segment'])
        check_item_count_in_inventory(game.state, 'Brass Mirror Segment', 1)

        talk_scholar = execute_commands(game, ['talk to ash scholar'])
        assert 'scholar' in talk_scholar.lower() or 'brass' in talk_scholar.lower()
        check_item_count_in_inventory(game.state, 'Brass Mirror Segment', 2)

        # Step 13: Obsidian Outcrops — search to reveal mirror segments and binding resin
        execute_commands(game, ['north'])
        check_current_room(game.state, 'Obsidian Outcrops')
        search_out = execute_commands(game, ['search'])
        assert 'brass' in search_out.lower() or 'resin' in search_out.lower()
        # Take discovered items
        execute_commands(game, ['take brass mirror segment', 'take binding resin'])
        check_item_count_in_inventory(game.state, 'Brass Mirror Segment', 3)
        check_item_in_inventory(game.state, 'Binding Resin')

        # Step 14: Mirror Terraces — install mirrors to form channel
        execute_commands(game, ['east'])
        check_current_room(game.state, 'Mirror Terraces')
        # There should be mounts and at least one brass segment in the room
        # Examine the inscription to update quest log
        execute_commands(game, ['examine inscription'])
        # Take the terrace-provided segment if present
        execute_commands(game, ['examine mirror mount', 'take brass mirror segment'])
        check_item_count_in_inventory(game.state, 'Brass Mirror Segment', 4)
        # Install three segments into mounts (use command format recognized by game)
        execute_commands(game, ['use brass mirror segment with mirror mount'])
        execute_commands(game, ['use binding resin with mirror mount'])
        # Before mending, the mirrors quest should not be completed and the flag not set
        check_story_flag(game.state, FLAG_ACT3_MIRRORS_OF_EMBER_LIGHT_COMPLETED, False)
        # After installing, cast the mend spell on a mount to finalize repairs
        execute_commands(game, ['cast mend on mirror mount'])
        # After mending, the mirrors quest should be completed and the flag set
        check_story_flag(game.state, FLAG_ACT3_MIRRORS_OF_EMBER_LIGHT_COMPLETED, True)

        # --- Step 15: Ember Gallery — find ash-fern and cooled slag, craft heat ward
        # Move back south to the Ember Gallery to gather ward components
        execute_commands(game, ['south'])
        check_current_room(game.state, 'Ember Gallery')
        # Search reveals ash-fern and cooled slag
        search_result = execute_commands(game, ['search'])
        assert 'ash-fern' in search_result.lower() or 'cooled slag' in search_result.lower()
        execute_commands(game, ['take ash-fern', 'take cooled slag'])
        check_item_in_inventory(game.state, 'ash-fern', True)
        check_item_in_inventory(game.state, 'cooled slag', True)
        # Combine to craft the heat-ward mix
        craft_result = execute_commands(game, ['use ash-fern with cooled slag'])
        assert 'heat' in craft_result.lower() or 'ward' in craft_result.lower()
        check_item_in_inventory(game.state, 'heat-ward mix', True)

        # --- Step 16: Fumarole Passages — calibrate vents and apply heat ward
        # Move east to the Fumarole Passages (now open because mirrors completed)
        execute_commands(game, ['north', 'east'])
        check_current_room(game.state, 'Fumarole Passages')
        # It should not be possible to move south
        execute_commands(game, ['south'])
        check_current_room(game.state, 'Fumarole Passages')
        # Take and use three vent stones to calibrate
        execute_commands(game, ['take vent stone', 'take vent stone', 'take vent stone'])
        check_item_count_in_inventory(game.state, 'Vent Stone', 3)
        # Use each vent stone to calibrate the vents
        execute_commands(game, ['use vent stone', 'use vent stone'])
        # Before the third calibration, applying the ward should fail
        fail_apply = execute_commands(game, ['use heat-ward mix'])
        assert 'not yet synchronized' in fail_apply.lower() or 'unstable' in fail_apply.lower()
        # Final calibration
        execute_commands(game, ['use vent stone'])
        # Now apply the heat-ward mix
        apply_result = execute_commands(game, ['use heat-ward mix'])
        assert 'ward' in apply_result.lower() or 'seals' in apply_result.lower()
        check_story_flag(game.state, FLAG_ACT3_BREATH_OF_THE_MOUNTAIN_COMPLETED, True)

        # --- Step 18: Phoenix Crater (Relic Trial) ---
        # Move south to Phoenix Crater
        execute_commands(game, ['south'])
        check_current_room(game.state, 'Phoenix Crater')
        # Reveal the phoenix
        execute_commands(game, ['rest'])
        check_character_in_room(game.state.current_room, 'phoenix', True)
        # Talk to the phoenix to get the riddle
        talk_result = execute_commands(game, ['talk to phoenix'])
        assert 'wisdom' in talk_result.lower() and 'time is short' in talk_result.lower()
        # Say the correct answer
        execute_commands(game, ['say patience to phoenix'])
        # Take the phoenix feather
        check_item_in_inventory(game.state, 'phoenix feather', True)

        # --- Step 19: Talk to Mira to teleport to Cavern Mouth (Caverns of Shadow) ---
        execute_commands(game, ['n', 'w', 'w', 's', 'talk to mira'])
        check_current_room(game.state, 'Cavern Mouth')
        check_character_in_room(game.state.current_room, 'mine overseer', True)

        # --- Step 20: Cavern Mouth: search and talk to Mine Overseer ---
        talk_result = execute_commands(game, ['talk to mine overseer'])
        assert 'tool cache' in talk_result.lower() and 'key' in talk_result.lower()
        check_item_in_inventory(game.state, "Miner's Key", True)
        # Should have started Miners' Rescue quest (side quest activation is implicit)
        # (If a helper for quest exists, could check for 'Miners' Rescue' in active quests)

        # --- Step 21: Tool Cache: search to find crate, unlock and open crate, take supplies ---
        execute_commands(game, ['north'])
        check_current_room(game.state, 'Tool Cache')

        # Initially, the supply crate should not be visible in the room
        check_item_in_room(game.state.current_room, 'supply crate', False)

        # Search the room to discover the hidden supply crate
        search_result = execute_commands(game, ['search'])
        assert 'discover a heavy supply crate' in search_result.lower()
        assert 'hidden behind stacked timbers' in search_result.lower()
        assert 'rescue supplies' in search_result.lower()

        # After searching, the supply crate should now be visible in the room
        check_item_in_room(game.state.current_room, 'supply crate', True)

        # Search again should give a different message indicating it's already found
        search_again = execute_commands(game, ['search'])
        assert 'already found' in search_again.lower()

        # Use key on crate
        unlock_result = execute_commands(game, ["use miner's key with supply crate"])
        assert 'unlock' in unlock_result.lower() or 'padlock' in unlock_result.lower()

        # Open crate
        open_result = execute_commands(game, ['open supply crate'])
        assert 'open' in open_result.lower() and 'braces' in open_result.lower()
        # Take all three supply items
        execute_commands(game, ['take reinforced braces'])
        execute_commands(game, ['take support straps'])
        execute_commands(game, ['take wedge blocks'])
        check_item_in_inventory(game.state, 'Reinforced Braces', True)
        check_item_in_inventory(game.state, 'Support Straps', True)
        check_item_in_inventory(game.state, 'Wedge Blocks', True)

        # --- Step 22: Collapsed Galleries - Miners' Rescue sequence ---
        execute_commands(game, ['east'])
        check_current_room(game.state, 'Collapsed Galleries')
        # Miners should not be present initially - they appear after passage is freed
        check_character_in_room(game.state.current_room, 'miners', False)
        check_item_in_room(game.state.current_room, 'fallen rock', True)

        # Initially, east exit should be blocked
        execute_commands(game, ['east'])
        check_current_room(game.state, 'Collapsed Galleries')  # Should still be here

        # Use reinforced braces with fallen rock (stabilizes collapse)
        stabilize_result = execute_commands(game, ['use reinforced braces with fallen rock'])
        assert 'stabilizing the collapse' in stabilize_result.lower()

        # Use support straps with fallen rock (secures the braces)
        secure_result = execute_commands(game, ['use support straps with fallen rock'])
        assert 'bind the reinforced braces securely' in secure_result.lower()

        # Use wedge blocks with fallen rock (frees passage and adds miners to room)
        free_result = execute_commands(game, ['use wedge blocks with fallen rock'])
        assert 'freeing the blocked passage' in free_result.lower()
        assert 'trapped miners emerging' in free_result.lower()

        # After freeing passage, miners should now be present and fallen rock should be gone
        check_character_in_room(game.state.current_room, 'miners', True)
        check_item_in_room(game.state.current_room, 'fallen rock', False)

        # Talk to miners (completes rescue and opens east exit)
        rescue_result = execute_commands(game, ['talk to miners'])
        assert ('miner steps forward' in rescue_result.lower() and
                'thank the gods' in rescue_result.lower())
        check_story_flag(game.state, FLAG_ACT3_MINERS_RESCUE_COMPLETED, True)

        # Now east exit should be available
        execute_commands(game, ['east'])
        check_current_room(game.state, 'Echo Chambers')

        # --- Step 23: Echo Chambers - Resonant Chant sequence ---
        check_item_in_room(game.state.current_room, 'runic walls', True)

        # Search to discover the Old Oath Scrolls
        search_result = execute_commands(game, ['search'])
        assert 'ancient scrolls' in search_result
        assert 'stone niche' in search_result

        # First examine the Old Oath Scrolls to understand the oath requirements
        examine_scrolls = execute_commands(game, ['examine old oath scrolls'])
        assert 'selflessness' in examine_scrolls.lower()
        assert 'disintegrate' in examine_scrolls.lower()
        check_story_flag(game.state, FLAG_ACT3_OATH_SCROLLS_EXAMINED, True)

        # After examination, scrolls should be consumed and no longer available
        check_item_in_room(game.state.current_room, 'Old Oath Scrolls', False)
        check_item_in_inventory(game.state, 'Old Oath Scrolls', False)

        # Examine runic walls (reveals chant instructions and adds rubbings to room)
        examine_result = execute_commands(game, ['examine runic walls'])
        assert 'Let stillness echo, let silence bind' in examine_result
        assert 'chant to quiet the phantoms' in examine_result.lower()

        # After examining, rubbings should be available in the room
        check_item_in_room(game.state.current_room, 'Resonant Chant Rubbings', True)

        # Take resonant chant rubbings (adds to inventory)
        check_item_in_inventory(game.state, 'Resonant Chant Rubbings', False)
        take_result = execute_commands(game, ['take resonant chant rubbings'])
        assert 'resonant chant rubbings' in take_result.lower()
        check_item_in_inventory(game.state, 'Resonant Chant Rubbings', True)

        # --- Step 24: Stillness Vestibule - Oath of Stillness sequence ---
        execute_commands(game, ['west', 'south'])
        check_current_room(game.state, 'Stillness Vestibule')
        check_item_in_room(game.state.current_room, 'echo stones', True)
        check_character_in_room(game.state.current_room, 'silence keeper', True)

        # Cast bless on echo stones (sanctifies them for the rite)
        bless_result = execute_commands(game, ['cast bless on echo stones'])
        assert (
            'sacred luminescence' in bless_result.lower() and
            'ancient chant' in bless_result.lower()
        )

        # Use resonant chant rubbings on echo stones (performs the Oath of Stillness)
        oath_result = execute_commands(game, ['use resonant chant rubbings with echo stones'])
        assert 'recite the resonant chant' in oath_result.lower()
        assert 'harmonious silence' in oath_result.lower()
        assert "dragon's hall now lies open" in oath_result.lower()
        check_story_flag(game.state, FLAG_ACT3_OATH_OF_STILLNESS_COMPLETED, True)

        # Resonant chant rubbings should be consumed and removed from inventory
        check_item_in_inventory(game.state, 'Resonant Chant Rubbings', False)

        # Now east exit to Dragon's Hall should be available
        execute_commands(game, ['east'])
        check_current_room(game.state, "Dragon's Hall")

        # --- Step 25: Dragon's Hall - Dragon's Memory (Story Clue) ---
        check_character_in_room(game.state.current_room, 'ancient dragon', True)
        # Dragon's scale should NOT be present initially (only after oath in step 26)
        check_item_in_room(game.state.current_room, "dragon's scale", False)

        # Talk to dragon (grants the Dragon's Memory)
        memory_result = execute_commands(game, ['talk to ancient dragon'])
        assert 'Lyra and Theron' in memory_result
        assert 'protected until the time of choosing' in memory_result.lower()
        assert 'ward—not of stone or steel, but of love' in memory_result.lower()
        check_story_flag(game.state, FLAG_ACT3_DRAGONS_MEMORY_RECEIVED, True)

        # --- Step 26: Dragon's Hall - Relic Trial (Oath and Scale) ---
        # Say oath to dragon (adds dragon's scale to room)
        oath_result = execute_commands(game, ['say oath to ancient dragon'])
        assert 'oath' in oath_result.lower()
        assert 'scale' in oath_result.lower()
        check_story_flag(game.state, FLAG_ACT3_DRAGON_OATH_SPOKEN, True)

        # Dragon's scale should now be present in the room
        check_item_in_room(game.state.current_room, "dragon's scale", True)

        # Take dragon's scale
        execute_commands(game, ['take dragon\'s scale'])
        check_item_in_inventory(game.state, "dragon's scale", True)
        check_item_in_room(game.state.current_room, "dragon's scale", False)

        # --- Step 27: Dragon's Hall - Return to Mira's Hut ---
        # Talk to Mira to teleport back to Mira's Hut
        talk_result = execute_commands(game, ['w', 'w', 'talk to mira'])
        assert 'three relics are yours' in talk_result.lower()
        assert 'return to my hut' in talk_result.lower()
        check_current_room(game.state, "Mira's Hut")

        # --- Step 28: Mira's Hut - Warding Rite and Lifelight Elixir ---
        # Talk to Mira to perform the Warding Rite
        warding_result = execute_commands(game, ['talk to mira'])
        assert 'three relics resonate' in warding_result.lower()
        assert 'lifelight elixir' in warding_result.lower()
        assert 'courage, wisdom, and selflessness' in warding_result.lower()
        check_story_flag(game.state, FLAG_ACT3_LIFELIGHT_ELIXIR_CREATED, True)

        # Lifelight Elixir should now be available in the room
        check_item_in_room(game.state.current_room, "lifelight elixir", True)

        # Take Lifelight Elixir
        execute_commands(game, ['take lifelight elixir'])
        check_item_in_inventory(game.state, "lifelight elixir", True)
        check_item_in_room(game.state.current_room, "lifelight elixir", False)

        # Talk to Mira again to teleport to fortress
        fortress_result = execute_commands(game, ['talk to mira'])
        assert 'final journey' in fortress_result.lower()
        assert 'fortress' in fortress_result.lower()
        check_current_room(game.state, "Entrance to Malakar's Fortress")

        # --- Step 29: Entrance to Malakar's Fortress - Examine Gates ---
        examine_result = execute_commands(game, ['examine gates'])
        assert 'massive gates' in examine_result.lower()
        assert 'act iii is complete' in examine_result.lower()
        check_story_flag(game.state, FLAG_ACT3_FORTRESS_GATES_EXAMINED, True)
