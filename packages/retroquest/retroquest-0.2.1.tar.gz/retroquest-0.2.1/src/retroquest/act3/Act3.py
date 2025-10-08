"""Act 3 of RetroQuest: The Awakening."""

from retroquest.engine.Act import Act
from retroquest.engine.GameState import GameState

from .quests import (
    TheThreeVirtuesQuest,
    TidewardSigilsQuest,
    LanternsOfTheDeepsQuest,
    MirrorsOfEmberlightQuest,
    BreathOfTheMountain,
    MinersRescue,
    OathOfStillness,
    EchoesOfTheHiddenBondQuest,
)
from .rooms import (
    CavernMouth,
    CollapsedGalleries,
    CollapsedPier,
    DragonsHall,
    EchoChambers,
    EmberGallery,
    FortressEntrance,
    FumarolePassages,
    LowerSwitchbacks,
    MirasHut,
    MirrorTerraces,
    ObsidianOutcrops,
    OuterWards,
    PhoenixCrater,
    SanctumOfTheTide,
    ShorelineMarkers,
    StillnessVestibule,
    SubmergedAntechamber,
    TidalCauseway,
    ToolCache,
)
from .spells import LightSpell, PurifySpell, UnlockSpell, MendSpell, BlessSpell


class Act3(Act):
    """Act 3 of RetroQuest: The Awakening."""

    def __init__(self) -> None:
        """Initialize Act 3 with all rooms and quests."""
        rooms = {
            # Starting hub
            "MirasHut": MirasHut(),

            # Sunken Ruins
            "TidalCauseway": TidalCauseway(),
            "ShorelineMarkers": ShorelineMarkers(),
            "OuterWards": OuterWards(),
            "CollapsedPier": CollapsedPier(),
            "SubmergedAntechamber": SubmergedAntechamber(),
            "SanctumOfTheTide": SanctumOfTheTide(),

            # Mount Ember
            "LowerSwitchbacks": LowerSwitchbacks(),
            "ObsidianOutcrops": ObsidianOutcrops(),
            "MirrorTerraces": MirrorTerraces(),
            "FumarolePassages": FumarolePassages(),
            "EmberGallery": EmberGallery(),
            "PhoenixCrater": PhoenixCrater(),

            # Caverns of Shadow
            "CavernMouth": CavernMouth(),
            "ToolCache": ToolCache(),
            "CollapsedGalleries": CollapsedGalleries(),
            "EchoChambers": EchoChambers(),
            "StillnessVestibule": StillnessVestibule(),
            "DragonsHall": DragonsHall(),

            # Ending
            "FortressEntrance": FortressEntrance(),
        }

        quests = [
            # Main Quest
            TheThreeVirtuesQuest(),
            # Storytelling Quest
            EchoesOfTheHiddenBondQuest(),
            # Sunken Ruins Side Quests
            TidewardSigilsQuest(),
            LanternsOfTheDeepsQuest(),
            # Mount Ember Side Quests
            MirrorsOfEmberlightQuest(),
            BreathOfTheMountain(),
            # Caverns of Shadow Side Quests
            MinersRescue(),
            OathOfStillness(),
        ]

        music_file = "Orchestronika - Feel The Storm (freetouse.com).mp3"
        music_info = (
            'Music track: Feel The Storm by Orchestronika\n'
            'Source: https://freetouse.com/music\n'
            'No Copyright Vlog Music for Videos'
        )
        super().__init__(
            'Act III', rooms, quests, music_file=music_file, music_info=music_info
        )

    def get_act_intro(self) -> str:
        """Return the introductory text for Act III."""
        return (
            "[bold]ACT III: THE AWAKENING[/bold]\n\n"
            "You and Sir Cedric return to Willowbrook, the village where it all began. "
            "Mira is waiting — the only one who can reveal how to confront Malakar "
            "and what must be done next. "
            "Her guidance will chart your path toward the Obsidian Fortress "
            "and the trials ahead.\n\n"
            "Gather your resolve; the final hunt begins where the first questions "
            "were asked.\n\n"
            "Let's begin. (Type 'help' for a list of commands.)\n"
        )

    def is_completed(self, _game_state: GameState) -> bool:
        """Check if Act III is completed based on the completion flag."""
        # Act III completes when the fortress gate is opened and the endgame is triggered.
        # Note: This will be updated when Act IV is implemented
        return False
        # return game_state.get_story_flag(FLAG_ACT3_FORTRESS_GATES_EXAMINED)

    def setup_gamestate(self, game_state: GameState) -> None:
        """Ensure essential Act III magic is available at start."""
        # Learn core Act III spells so Sunken Ruins progression is possible
        if not game_state.has_spell(PurifySpell().name):
            game_state.learn_spell(PurifySpell())
        if not game_state.has_spell(UnlockSpell().name):
            game_state.learn_spell(UnlockSpell())
        if not game_state.has_spell(LightSpell().name):
            game_state.learn_spell(LightSpell())
        if not game_state.has_spell(MendSpell().name):
            game_state.learn_spell(MendSpell())
        if not game_state.has_spell(BlessSpell().name):
            game_state.learn_spell(BlessSpell())
