"""AncientAmulet Item

Narrative Role:
Powerful heirloom artifact intentionally withheld early to establish narrative guardianship
and foreshadow magical systems and responsibility themes.

Key Mechanics / Interactions:
- Always blocks pickup via `prevent_pickup` dialogue from Mira, signaling preparation
prerequisites (not yet mechanically enforced beyond message).

Story Flags (Sets / Reads):
(none) – Gating currently narrative only.

Progression Effects:
- Builds anticipation for later acquisition, reinforcing preparation arc.

Design Notes:
- Future: replace unconditional block with conditional check (e.g., all preparation flags set)
    then allow carry.
- Potential synergy with rune/spell affinity once magical attunement is introduced.

"""

from ...engine.Item import Item

class AncientAmulet(Item):
    """
    Item representing the Ancient Amulet, a key narrative artifact in Act 1.
    """

    def __init__(self) -> None:
        """Initialize the Ancient Amulet item with name, description, and short name."""
        super().__init__(
            name="ancient amulet",
            description=(
                "A mysterious amulet inscribed with runes. It glows faintly and feels powerful "
                "to the touch."
            ),
            short_name="amulet"
        )

    def prevent_pickup(self) -> str:
        """Always blocks pickup with narrative justification (no readiness check yet)."""
        return (
            "[character_name]Mira[/character_name] places a protective hand over the "
            "[item_name]amulet[/item_name]. [dialogue]'This is not yet yours to claim, "
            "[character_name]Elior[/character_name]. The [item_name]Ancient Amulet[/item_name] "
            "is a powerful artifact that must be earned through preparation and wisdom. "
            "Complete your journey preparations first, and it shall be yours.'[/dialogue]"
        )
