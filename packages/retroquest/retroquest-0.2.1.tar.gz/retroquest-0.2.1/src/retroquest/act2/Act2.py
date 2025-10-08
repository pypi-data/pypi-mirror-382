"""Handles the logic for Act 2, including room transitions and quest management."""
from retroquest.engine import GameState
from retroquest.engine.Act import Act
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
from retroquest.act2.quests.TheGatheringStorm import TheGatheringStormQuest
from retroquest.act2.quests.TheKnightsTest import TheKnightsTestQuest
from retroquest.act2.quests.SuppliesForTheJourney import SuppliesForTheJourneyQuest
from retroquest.act2.quests.EchoesOfThePast import EchoesOfThePastQuest
from retroquest.act2.quests.TheInnkeepersDaughter import TheInnkeepersDaughterQuest
from retroquest.act2.quests.TheMerchantsLostCaravan import TheMerchantsLostCaravanQuest
from retroquest.act2.quests.TheHealersApprentice import TheHealersApprenticeQuest
from retroquest.act2.quests.TheAncientLibrary import TheAncientLibraryQuest
from retroquest.act2.quests.TheForestGuardiansRiddles import TheForestGuardiansRiddles
from retroquest.act2.quests.TheHermitsWarning import TheHermitsWarningQuest
from retroquest.act2.quests.WhispersInTheWind import WhispersInTheWind
from retroquest.act2.quests.CedricksLostHonorQuest import CedricksLostHonorQuest
from retroquest.act2.Act2StoryFlags import FLAG_GATHERING_STORM_COMPLETED

class Act2(Act):
    """Handles the logic for Act 2, including room transitions and quest management.

    Args:
        Act (Act): The base class for all acts in the game.
    """
    def __init__(self) -> None:
        rooms = {
            "MountainPath": MountainPath(),
            "GreendaleGates": GreendaleGates(),
            "MainSquare": MainSquare(),
            "MarketDistrict": MarketDistrict(),
            "SilverStagInn": SilverStagInn(),
            "InnRooms": InnRooms(),
            "MerchantsWarehouse": MerchantsWarehouse(),
            "CastleApproach": CastleApproach(),
            "CastleCourtyard": CastleCourtyard(),
            "GreatHall": GreatHall(),
            "ResidentialQuarter": ResidentialQuarter(),
            "HealersHouse": HealersHouse(),
            "HiddenLibrary": HiddenLibrary(),
            "ForestTransition": ForestTransition(),
            "ForestEntrance": ForestEntrance(),
            "AncientGrove": AncientGrove(),
            "WhisperingGlade": WhisperingGlade(),
            "HeartOfTheForest": HeartOfTheForest(),
        }
        quests = [
            # Main Quest
            TheGatheringStormQuest(),

            # Greendale Phase Side Quests
            TheKnightsTestQuest(),
            SuppliesForTheJourneyQuest(),
            EchoesOfThePastQuest(),
            TheHealersApprenticeQuest(),
            TheAncientLibraryQuest(),
            TheInnkeepersDaughterQuest(),
            CedricksLostHonorQuest(),

            # Forest Phase Side Quests
            TheMerchantsLostCaravanQuest(),
            TheForestGuardiansRiddles(),
            WhispersInTheWind(),
            TheHermitsWarningQuest(),
        ]
        music_file = "Walen - Medieval Village (freetouse.com).mp3"
        music_info = (
            'Music track: Medieval Village by Walen\nSource: https://freetouse.com/music\n'
            'Free To Use Music for Video'
        )
        super().__init__(name="Act II: Greendale & The Forest Edge", rooms=rooms, quests=quests,
                         music_file=music_file, music_info=music_info)

    def get_act_intro(self) -> str:
        return (
            "[bold]ACT 2: THE GATHERING STORM[/bold]\n\n"
            "After the mysterious events in Willowbrook and the revelation of your growing magical "
            "abilities, you have left your quiet village behind. The mountain path stretches "
            "before you, winding through rocky terrain toward your destination: Greendale, a "
            "bustling city that serves as the gateway between civilization and the mystical "
            "Enchanted Forest.\n\n"
            "As you crest the final ridge, the sight takes your breath away. Below lies Greendale—"
            "larger than any settlement you've ever seen, with stone buildings, "
            "busy market squares, "
            "and an impressive castle rising majestically above the city walls. Smoke rises from "
            "countless chimneys, and you can hear the distant sounds of commerce and conversation "
            "carried on the mountain breeze.\n"
            "\nYour grandmother's words echo in your mind: [dialogue]'Seek out Sir Cedric at the "
            "castle. He will help you understand your heritage and the growing darkness that "
            "threatens our world.'[/dialogue] The ancient amulet she gave you feels warm against "
            "your chest, a reminder of the mysteries you must uncover.\n"
            "\nBeyond Greendale, you glimpse the edge of the Enchanted Forest—an ancient woodland "
            "where magic flows like water and spirits older than memory dwell among the trees. The "
            "very air seems to shimmer with possibility and danger.\n"
            "\nThis is where your true journey begins. In Greendale, you must prove yourself "
            "worthy, forge alliances with powerful allies, and master the magical arts. Only "
            "then will you be ready to face the forest's deepest secrets and the growing storm "
            "that threatens all you hold dear.\n"
            "\nTake a deep breath and step forward into your destiny.\n"
        )

    def is_completed(self, game_state: GameState) -> bool:
        return game_state.get_story_flag(FLAG_GATHERING_STORM_COMPLETED)
