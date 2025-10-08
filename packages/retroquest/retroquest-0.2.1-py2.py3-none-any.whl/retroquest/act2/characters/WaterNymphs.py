"""Water Nymphs NPC definition.
"""

from ...engine.Character import Character
from ...engine.GameState import GameState
from ..Act2StoryFlags import (
    FLAG_FOREST_GUARDIANS_RIDDLES_COMPLETED
)

class WaterNymphs(Character):
    """Ethereal guardians of the Whispering Glade who test visitors with riddles."""

    def __init__(self) -> None:
        super().__init__(
            name="water nymphs",
            description=(
                "Graceful ethereal beings who dwell in the sacred waters of the "
                "Whispering Glade. Their forms seem to be made of living water and "
                "moonlight, constantly shifting between transparency and solidity. "
                "Their voices sound like the gentle babbling of streams mixed with "
                "wind chimes, and their eyes hold the wisdom of countless seasons. "
                "These ancient guardians are known to test visitors with riddles "
                "that reveal the true depth of one's connection to the natural world."
            ),
        )
        self.riddles_completed = False
        self.current_riddle = 0
        self.riddles = [
            {
                "question": (
                    "I stand tall and proud, my arms reaching skyward, and sing without "
                    "voice. The older I become, the more rings I show. What am I?"
                ),
                "answers": ["tree", "trees", "forest"],
                "explanation": (
                    "A tree grows from earth but reaches toward sky, sings in the wind, "
                    "and shows age through rings."
                ),
            },
            {
                "question": (
                    "I am the forest's blood that flows without wound, the sky's gift "
                    "that falls without being thrown. I give life yet can take it, "
                    "am soft yet can carve stone. What am I?"
                ),
                "answers": ["water"],
                "explanation": (
                    "Water is the lifeblood of the forest, falls as rain, nurtures life "
                    "but can flood, and over time carves through stone."
                ),
            },
            {
                "question": (
                    "We are many yet one, small yet mighty, busy yet patient. We "
                    "build without hands, work without rest, and turn death into life. "
                    "What are we?"
                ),
                "answers": [
                    "insect",
                    "insects",
                    "bug",
                    "bugs",
                    "ant",
                    "ants",
                    "beetle",
                    "beetles",
                ],
                "explanation": (
                    "Insects work as colonies, build complex structures, decompose "
                    "matter, and are essential to the forest ecosystem."
                ),
            },
        ]

    def _get_ordinal_word(self, number: int) -> str:
        """Convert a number to its ordinal word representation."""
        ordinals = ["first", "second", "third", "fourth", "fifth"]
        if 1 <= number <= len(ordinals):
            return ordinals[number - 1]
        else:
            return str(number)  # fallback for numbers beyond our list

    def talk_to(self, _game_state: GameState) -> str:
        event_msg = (
            f"[event]You approach the [character_name]{self.get_name()}[/character_name] "
            "by the sacred stream.[/event]"
        )
        if self.riddles_completed:
            # After completing all riddles
            return (
                event_msg
                + "\n"
                + (
                    f"[dialogue]The [character_name]{self.get_name()}[/character_name] "
                    "shimmer with approval. 'You have proven your wisdom and "
                    "understanding of the forest's ways, young seeker. The sacred "
                    "gifts are yours to take - the crystal-clear water and moonflowers "
                    "that grow here. Use them wisely in your quest to protect the "
                    "natural world.'[/dialogue]"
                )
            )
        elif self.current_riddle < len(self.riddles):
            # Present the current riddle
            riddle = self.riddles[self.current_riddle]
            return (
                event_msg
                + "\n"
                + (
                    f"[dialogue]The [character_name]{self.get_name()}[/character_name] "
                    "speak in harmonious, flowing voices like water over stones. "
                    "'Welcome, forest walker, to our sacred glade. To prove your "
                    "wisdom and earn our trust, you must answer our riddles three. "
                    "Listen carefully to the "
                    f"{self._get_ordinal_word(self.current_riddle + 1)} riddle:'[/dialogue]"
                )
                + "\n\n"
                + f"[dialogue]'{riddle['question']}'[/dialogue]\n\n"
                + (
                    "[info]Think carefully and speak your answer when you believe you "
                    "know it. Use the command 'say <your_answer> to water nymphs' to "
                    "give your solution.[/info]"
                )
            )
        else:
            # This shouldn't happen, but just in case
            return (
                event_msg
                + "\n"
                + (
                    f"[dialogue]The [character_name]{self.get_name()}[/character_name] "
                    "smile mysteriously. 'The riddles have been answered, young "
                    "one.'"
                    "[/dialogue]"
                )
            )

    def say_to(self, words: str, game_state: GameState) -> str:
        """Process player speech for riddle answering (overrides base)."""
        if self.riddles_completed:
            return (
                f"[info]The [character_name]{self.get_name()}[/character_name] have "
                "already accepted your wisdom. "
                f"They listen to your words '{words}' with gentle understanding "
                "but have no more riddles for you.[/info]"
            )

        if self.current_riddle >= len(self.riddles):
            return "[error]There are no more riddles to answer.[/error]"

        riddle = self.riddles[self.current_riddle]
        word_lower = words.lower().strip()

        if word_lower in riddle["answers"]:
            # Correct answer
            self.current_riddle += 1
            game_state.set_story_flag(
                f"water_nymph_riddle_{self.current_riddle}_completed", True
            )

            if self.current_riddle >= len(self.riddles):
                self.riddles_completed = True
                game_state.set_story_flag(
                    FLAG_FOREST_GUARDIANS_RIDDLES_COMPLETED, True
                )

                from ..items.CrystalClearWater import CrystalClearWater
                from ..items.Moonflowers import Moonflowers
                game_state.current_room.items.append(CrystalClearWater())
                game_state.current_room.items.append(Moonflowers())

                return (
                    f"[success]Correct! '{words}' is indeed the answer. "
                    f"{riddle['explanation']}[/success]\n\n"
                    + (
                        f"[dialogue]The [character_name]{self.get_name()}[/character_name] "
                        "sing in harmonious delight. 'Wisely spoken, all three riddles "
                        "answered! You have proven your deep understanding of the "
                        "forest's mysteries. Accept our gifts - the crystal-clear water "
                        "and moonflowers that grow in this sacred place. May they "
                        "serve you well in your noble quest.'[/dialogue]"
                    )
                    + "\n\n"
                    + (
                        "[info]The water nymphs gesture toward the stream and flowers, "
                        "making them accessible for you to take.[/info]"
                    )
                )
            else:
                next_riddle = self.riddles[self.current_riddle]
                return (
                    f"[success]Correct! '{words}' is the right answer. "
                    f"{riddle['explanation']}[/success]\n\n"
                    + (
                        f"[dialogue]The [character_name]{self.get_name()}[/character_name] "
                        "nod approvingly. 'Well spoken! Now for the "
                        f"{self._get_ordinal_word(self.current_riddle + 1)} riddle:'"
                        "[/dialogue]"
                    )
                    + "\n\n"
                    + f"[dialogue]'{next_riddle['question']}'[/dialogue]"
                )
        else:
            return (
                f"[failure]The [character_name]{self.get_name()}[/character_name] "
                f"shake their heads gently as you say '{words}'. "
                "'Not quite, young seeker. Think more deeply about the forest "
                "and its ways. The answer lies in understanding the natural "
                "world around you.'[/failure]\n\n"
                + f"[dialogue]'{riddle['question']}'[/dialogue]\n\n"
                + (
                    "[info]Consider what you've learned about the forest during your "
                    "journey.[/info]"
                )
            )

    def examine(self, _game_state: GameState) -> str:
        return (
            f"[event]You study the [character_name]{self.get_name()}[/character_name] "
            f"in wonder. {self.description} They move with fluid grace, and you can "
            "see the wisdom of ages in their ever-changing features. These are "
            "ancient guardians of the forest's deepest secrets.[/event]"
        )
