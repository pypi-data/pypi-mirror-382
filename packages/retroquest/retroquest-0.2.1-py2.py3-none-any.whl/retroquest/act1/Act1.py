from retroquest.engine.GameState import GameState
from retroquest.engine.Act import Act
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
from retroquest.act1.quests.ShadowsOverWillowbrook import ShadowsOverWillowbrookQuest
from retroquest.act1.quests.LostLetter import LostLetterQuest
from retroquest.act1.Act1StoryFlags import FLAG_SHADOWS_OVER_WILLOWBROOK_COMPLETED

class Act1(Act):
    def __init__(self) -> None:
        rooms = {
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
        quests = [
            ShadowsOverWillowbrookQuest(),
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
            LostLetterQuest(),
        ]
        music_file = "Conquest - Market (freetouse.com).mp3"
        super().__init__(name="Act1", rooms=rooms, quests=quests, music_file=music_file, music_info='Market by Conquest\nSource: https://freetouse.com/music\nCopyright Free Background Music')

    def get_act_intro(self) -> str:
        return (
            "[bold]ACT 1: THE CALL TO ADVENTURE[/bold]\n\n"
            "You are Elior, a humble farmer boy living in the quiet village of Willowbrook on the outskirts of Eldoria. "
            "Raised by your grandmother after your parents vanished mysteriously, your life is simple—tending crops and caring for animals. "
            "One stormy night, a strange light appears in the sky, and you dream of a shadowy figure calling your name.\n"
            "\nThe next morning, you awaken to find the village abuzz with rumors: livestock missing, strange footprints by the well, and the old mill's wheel turning on its own. "
            "Your grandmother, usually cheerful, seems worried and distracted, her gaze lingering on a faded photograph.\n"
            "\nAs you step outside, the air feels charged with something unfamiliar. The villagers gather in the square, debating what to do. "
            "Mira, the wise woman, catches your eye and beckons you over. [dialogue]'There are secrets in Willowbrook, child,'[/dialogue] she says. [dialogue]'Secrets that have waited for you.'[/dialogue]\n"
            "\nA distant bell tolls from the chapel, and a cold wind rustles the fields. You sense that today, everything will change. "
            "With questions swirling in your mind, you take your first step into the unknown.\n"
            "\nLet's get started! (Type 'help' for a list of commands.)\n"
        )

    def is_completed(self, game_state: GameState) -> bool:
        return game_state.get_story_flag(FLAG_SHADOWS_OVER_WILLOWBROOK_COMPLETED)
