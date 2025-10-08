"""SilenceKeeper character for the Stillness Vestibule in Act 3."""
from ...engine.Character import Character
from ...engine.GameState import GameState


class SilenceKeeper(Character):
    """Guardian of the threshold to the dragon's hall."""

    def __init__(self) -> None:
        """Initialize SilenceKeeper with mysterious appearance."""
        super().__init__(
            name="silence keeper",
            description=(
                "A tall figure robed in shadow-dark fabric that seems to absorb "
                "sound itself. Their face is hidden beneath a deep hood, and they "
                "move without disturbing the stillness around them."
            )
        )

    def talk_to(self, _game_state: GameState) -> str:
        """Provide guidance on the Oath of Stillness."""
        return (
            "[dialogue]'The echo stones await sanctification,'[/dialogue] "
            "the Silence Keeper whispers, their voice barely "
            "disturbing the air. [dialogue]'Only when blessed "
            "can they amplify the ancient words that will quiet the restless "
            "spirits. Speak the resonant chant to the stones, and the path to "
            "the ancient one will open.'[/dialogue]"
        )
