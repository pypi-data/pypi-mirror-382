"""Local Craftsmen (Act II)

Role:
        Collective artisan NPC representing Greendale's skilled working guilds. Acts as the
        in-world tutor granting the player the Mend spell once they've demonstrated civic virtue.

Gating Logic:
        - Requires story flag FLAG_HELPED_ELDERLY_RESIDENTS == True (earned by assisting
            Families / elderly with a Walking Stick) before dialogue becomes welcoming.
        - First successful post-gate interaction awards the Mend spell (utility + thematic
            reinforcement of restorative, community-focused play style).

Story Flags Consumed / Set:
        - Reads: FLAG_HELPED_ELDERLY_RESIDENTS
        - Does not set new flags; instead confers a spell reward once.

Rewards & Progression:
        - Grants spell 'mend' (via learn_spell) if not already known after gating condition.
        - Subsequent interactions become flavor / affirmation of player's contribution.

Design Notes:
        - Spell learning implemented through observation rather than direct teaching to
            vary acquisition modality versus formal mentor NPCs.
        - Avoids additional flags to keep complexity low and self-contained.
        - If future crafting systems are added, this class could become a hub—migrate
            extended logic into an engine service to keep narrative clarity.
"""

from ...engine.Character import Character
from ...engine.GameState import GameState
from ..Act2StoryFlags import FLAG_HELPED_ELDERLY_RESIDENTS

class LocalCraftsmen(Character):
    """Collective artisan NPC that awards the Mend spell after civic aid."""
    def __init__(self) -> None:
        super().__init__(
            name="local craftsmen",
            description=(
                "Skilled artisans working at various crafts - blacksmithing, carpentry, "
                "tailoring, and magical repair work. They demonstrate traditional "
                "techniques passed down through generations."
            ),
        )

    def talk_to(self, game_state: GameState) -> str:
        from ..spells.MendSpell import MendSpell
        if not game_state.get_story_flag(FLAG_HELPED_ELDERLY_RESIDENTS):
            name = self.get_name()
            return (
                f"[failure]The [character_name]{name}[/character_name] eye you with "
                "suspicion and refuse to talk to you. They don't seem to trust "
                "you yet. Perhaps you need to prove yourself to the community "
                "first.[/failure]"
            )
        if not game_state.has_spell(MendSpell().name):
            game_state.learn_spell(MendSpell())
            name = self.get_name()
            return (
                f"[success]You speak with the [character_name]{name}[/character_name] and "
                "watch them work, observing their techniques for repairing items. "
                "As you study their methods, you begin to understand the magical "
                "principles behind restoration and repair. Through careful study, "
                "you learn the [spell_name]mend[/spell_name] spell![/success]"
            )
        else:
            name = self.get_name()
            return (
                f"[character_name]{name}[/character_name]: Good to see you again! "
                "How has your repair magic been working? The mend spell is one of the "
                "most useful pieces of magic a person can learn."
            )
