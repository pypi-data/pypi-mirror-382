"""An antechamber long caressed by tides and old rites."""
from ...engine.GameState import GameState
from ...engine.Room import Room
from ..Act3StoryFlags import (
    FLAG_ACT3_LANTERNS_OF_THE_DEEPS_LIT,
    FLAG_ACT3_TIDEWARD_SIGILS_COMPLETED,
)
from ..items import LanternBracket, PrismLantern

class SubmergedAntechamber(Room):
    """An antechamber where salt and memory linger in the stones."""

    def __init__(self) -> None:
        """Initialize the Submerged Antechamber and its exits."""
        super().__init__(
            name="Submerged Antechamber",
            description=(
                "The hall lies half-swallowed by tide and time. Salt-smoothed stone "
                "arches bear weathered carvings that pulse with a cold, inner glow. "
                "A hush hangs in the air as if the sea itself listens; faint, "
                "distant echoes suggest something patient and watchful beyond the "
                "veil of gloom. The place tastes of old prayers and the memory of "
                "rituals long since folded into the stones."
            ),
            items=[],
            characters=[],
            exits={
                "north": "OuterWards",
                "east": "SanctumOfTheTide",
                "west": "TidalCauseway"
            },
        )

    def describe(self, game_state: GameState) -> str:
        """Return the room description by delegating to the base class.

        This method intentionally forwards to the engine's `describe` helper
        so that common formatting (items, characters, exits) is preserved.
        """
        # If the Tideward sigils have been completed, the tide has withdrawn
        # and the room should no longer be described as submerged.
        # Adjust the stored description so the engine formatting reflects the
        # changed state, then restore the original text after describing.
        if game_state.get_story_flag(FLAG_ACT3_TIDEWARD_SIGILS_COMPLETED):
            self.description = (
                "The hall, recently unmasked by a withdrawing tide, shows the bare "
                "lines of its carved work. Salt crystals glitter on exposed stone; "
                "the air feels colder and the rooms' echoes are clearer than before."
            )
        return super().describe(game_state)

    def search(self, game_state: GameState, _target: str = None) -> str:
        """Search the antechamber for subtle traces and hidden marks."""
        # If the Tideward sigils haven't been completed, the water remains too
        # deep and obscures the niches — nothing can be revealed by searching.
        if not game_state.get_story_flag(FLAG_ACT3_TIDEWARD_SIGILS_COMPLETED):
            return (
                "[info]The water in the hall sits high and murky. It's impossible to "
                "search effectively here — the flooded approach hides whatever might "
                "lie beneath the surface.[/info]"
            )
        if game_state.get_story_flag(FLAG_ACT3_LANTERNS_OF_THE_DEEPS_LIT):
            return (
                "[info]The niches glow with steady, pearlescent flame. The Lanterns of the "
                "Deeps are already lit.[/info]"
            )
        # If brackets are not present yet, reveal them for mounting lanterns
        from ..items.LanternBracket import LanternBracket as _LB
        already_here = any(isinstance(i, _LB) for i in self.items)
        if not already_here:
            # Add three brackets to the room for players to mount lanterns on
            self.items.extend([LanternBracket(), LanternBracket(), LanternBracket()])
            # Mark that the lantern brackets have been discovered for quest logic
            from ..Act3StoryFlags import FLAG_ACT3_LANTERN_BRACKETS_FOUND
            game_state.set_story_flag(FLAG_ACT3_LANTERN_BRACKETS_FOUND, True)
            return (
                "[event]You wade through chilled water. As you peer into the niches, "
                "three carved brackets become apparent; their grooves catch the "
                "faint tide-light.[/event]"
            )
        return (
            "[info]You wade through chilled water. Three empty brackets line the "
            "approach; their carved grooves catch the faint tide-light.[/info]"
        )

    def mount_lantern(self, game_state: GameState) -> str:
        """Place a prism lantern into an available mount in the hall."""
        # Find an empty bracket
        empty = next(
            (
                b for b in self.items
                if isinstance(b, LanternBracket) and not b.has_lantern
            ),
            None
        )
        if empty is None:
            return "[info]All brackets here are already filled.[/info]"
        # Check inventory for a Prism Lantern
        lantern = next(
            (i for i in game_state.inventory if isinstance(i, PrismLantern)), None
        )
        if lantern is None:
            return (
                "[failure]You need a [item_name]Prism Lantern[/item_name] to mount "
                "here.[/failure]"
            )
        # Mount it
        game_state.inventory.remove(lantern)
        empty.put_lantern()
        return (
            "[event]You seat the prism lantern; water hums softly as the bracket takes its "
            "weight.[/event]"
        )

    def cast_light_here(self, game_state: GameState) -> str:
        """Cast light to awaken the hall's latent illumination using mounted lanterns."""
        # Light lanterns only if all three brackets have lanterns
        brackets = [b for b in self.items if isinstance(b, LanternBracket)]
        if not brackets:
            return ("[event]A warm spark flares in your palm and fades—nothing here seems to "
                    "catch.[/event]")
        if not all(b.has_lantern for b in brackets):
            return (
                "[failure]You kindle a spark, but without lanterns mounted, nothing "
                "gets lit.[/failure]"
            )
        if game_state.get_story_flag(FLAG_ACT3_LANTERNS_OF_THE_DEEPS_LIT):
            return "[info]The prism lanterns already burn with steady, cold flame.[/info]"
        game_state.set_story_flag(FLAG_ACT3_LANTERNS_OF_THE_DEEPS_LIT, True)
        return (
            "[success]Light pours from the prisms, weaving a clear path through "
            "the flooded hall. The way to the sanctum stands revealed.[/success]"
        )

    def get_exits(self, game_state: GameState) -> dict[str, str]:
        """Return exits, gating the sanctum entrance on two Act III story flags.

        The east exit leading to the Sanctum of the Tide is only available once
        the Tideward sigils have been completed and the Lanterns of the Deeps
        have been lit.
        """
        exits = dict(self.exits)
        lanterns_lit = game_state.get_story_flag(
            FLAG_ACT3_LANTERNS_OF_THE_DEEPS_LIT
        )
        sigils_done = game_state.get_story_flag(
            FLAG_ACT3_TIDEWARD_SIGILS_COMPLETED
        )
        if not (lanterns_lit and sigils_done):
            exits.pop("east", None)
        return exits
