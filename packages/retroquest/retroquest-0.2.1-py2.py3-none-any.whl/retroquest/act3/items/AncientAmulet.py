"""Ancient Amulet item for Act III."""

from ...engine.Item import Item


class AncientAmulet(Item):
    """Heirloom catalyst linking three relic threads (Act III).

    Narrative Role:
        Serves as the convergence focus for three prerequisite relic quests. The amulet
        remains bound until conditions are satisfied elsewhere, reinforcing multi-quest
        synthesis.

    Key Mechanics:
        Non-carriable until narrative completion; interception via `prevent_pickup()`
        provides flavor feedback and defers acquisition.
    """

    def __init__(self) -> None:
        """Initialize Ancient Amulet with description and restrictions."""
        super().__init__(
            name="ancient amulet",
            short_name="amulet",
            description=(
                "A family heirloom whose runes glint like dew at dawn. It seems to "
                "resonate faintly in the presence of the other relics, as though "
                "completing an unseen circuit."
            ),
            can_be_carried=False,
        )

    def prevent_pickup(self) -> str:
        """Block premature pickup, giving narrative feedback through Mira."""
        return (
            "[character_name]Mira[/character_name] rests a gentle hand on the "
            "[item_name]amulet[/item_name]. [dialogue]'Not yet. It will choose its "
            "bearer when the circle is complete.'[/dialogue]"
        )
