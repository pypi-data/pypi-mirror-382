"""Primary Textual UI application wiring layout, panels, and interaction flow."""
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input
from textual.containers import Horizontal, Vertical
from textual.css.query import NoMatches

from audio.soundeffects.SoundEffects import NEW_QUEST_SOUND, QUEST_COMPLETED_SOUND

from ...engine.Game import Game
from .GameController import GameController
from .RoomPanel import RoomPanel
from .ResultPanel import ResultPanel
from .QuestLogPanel import QuestLogPanel
from .InventoryPanel import InventoryPanel
from .CommandInput import CommandInput
from .Popup import Popup, PopupType
from .SpellPanel import SpellPanel

class TextualApp(App):  # pylint: disable=too-many-instance-attributes
    """Textual application hosting RetroQuest interactive UI.

    Responsibilities:
        * Orchestrate layout composition (room, result, quest log, inventory, spells).
        * Route input submission to game controller then refresh dependent panels.
        * Manage modal popup queue and persistence of prior input focus.

    Design Notes:
        Lightweight state is stored on the instance; heavy logic remains in the
        controller and engine. Popup sequencing uses a FIFO queue to preserve order
        when multiple quest events trigger in a single turn.
    """
    TITLE = "RetroQuest"
    SUB_TITLE = "A Text Adventure"
    CSS_PATH = "styles.tcss"

    def __init__(self, game: Game) -> None:  # noqa: D401 (simple initializer)
        super().__init__()
        self.controller = GameController(game)
        self._popup_queue: list[tuple[str, str, 'PopupType']] = []
        self._focus_before_popup = None  # Stores widget focused prior to popup
        # Panel/widget placeholders (assigned in compose) for type checkers
        self.room_panel: RoomPanel | None = None
        self.result_panel: ResultPanel | None = None
        self.questlog_panel: QuestLogPanel | None = None
        self.inventory_panel: InventoryPanel | None = None
        self.spell_panel: SpellPanel | None = None
        self.command_input: CommandInput | None = None

    def compose(self) -> ComposeResult:  # type: ignore[override]
        """Construct and yield application layout containers & widgets."""
        self.room_panel = RoomPanel()
        self.result_panel = ResultPanel()
        self.questlog_panel = QuestLogPanel()
        self.inventory_panel = InventoryPanel()
        self.spell_panel = SpellPanel()
        self.command_input = CommandInput(self.controller)
        yield Header()
        yield Horizontal(
            Vertical(
                self.room_panel,
                self.result_panel,
                classes="main_column frame"
            ),
            Vertical(
                Horizontal(
                    self.inventory_panel,
                    self.spell_panel,
                    id="inventory_spell_row"
                ),
                self.questlog_panel,
                classes="frame"
            ),
            id="main_row"
        )
        yield self.command_input
        yield Footer()

    async def on_mount(self) -> None:  # type: ignore[override]
        """Initialize panels with starting content and focus command input."""
        assert self.room_panel and self.questlog_panel and self.inventory_panel
        assert self.spell_panel and self.command_input
        self.room_panel.update_room(self.controller.start(), wide=True)
        self.questlog_panel.update_questlog('')
        self.inventory_panel.update_inventory([])
        self.spell_panel.update_spells([])
        self.command_input.focus()
        self.update_input()

    def update_input(self) -> None:
        """Adjust input placeholder based on whether game expects command or continue."""
        assert self.command_input is not None
        if self.controller.game.accept_input:
            self.command_input.placeholder = 'What do you want to do?'
        else:
            self.command_input.placeholder = 'Press Enter to continue'
        self.command_input.value = ""

    def open_popup(self, border_text: str, text: str, popup_type: PopupType) -> None:
        """Open popup or enqueue if one already displayed."""
        try:
            self.get_widget_by_id("popup")
        except NoMatches:
            # Save currently focused widget before opening popup
            self._focus_before_popup = self.focused
            popup = Popup(border_text, text, popup_type)
            self.mount(popup)
            popup.focus()
            return
        # If a popup already exists, queue the new one
        self._popup_queue.append((border_text, text, popup_type))

    def close_popup(self, response: str | None = None) -> None:
        """Close current popup; handle queued popups and optional quit flow."""
        popup = self.get_widget_by_id("popup")
        if not self.controller.game.is_running:
            if response == "y":
                self.controller.save_game()
            self.exit()
        # Show next popup in queue if any
        if self._popup_queue:
            next_border, next_text, next_type = self._popup_queue.pop(0)
            popup.set_content(next_border, next_text, next_type)
        else:
            # Restore focus to the widget that was focused before popup
            if self._focus_before_popup and self._focus_before_popup.is_attached:
                self._focus_before_popup.focus()
            else:
                self.command_input.focus()
            self._focus_before_popup = None
            popup.remove()

    def on_input_submitted(self, message: Input.Submitted) -> None:  # type: ignore[override]
        """Handle command submission, advance game turn, refresh panels."""
        command = message.value.strip()
        self.controller.game.handle_input(command)
        self.controller.game.new_turn()
        self.update_input()
        assert self.result_panel and self.room_panel
        assert self.inventory_panel and self.spell_panel
        if self.controller.game.is_act_running():
            self.result_panel.update_result(self.controller.game.get_result_text())
            self.room_panel.update_room(self.controller.get_room(), wide=False)
        else:
            self.room_panel.update_room(self.controller.game.get_result_text(), wide=True)
        self.inventory_panel.update_inventory(self.controller.get_inventory())
        self.spell_panel.update_spells(self.controller.get_spells())
        self.handle_quests()
        if not self.controller.game.is_running:
            self.open_popup(
                "Quit Game", "Do you want to save before quitting?", PopupType.QUESTION
            )

    def handle_quests(self) -> None:
        """Process queued quest state changes and open popups with sounds."""
        while True:
            quest_complete_popup = self.controller.complete_quest()
            if isinstance(quest_complete_popup, str) and quest_complete_popup.strip():
                self.controller.play_soundeffect(QUEST_COMPLETED_SOUND)
                self.open_popup("Quest Completed", quest_complete_popup, PopupType.INFO)
            else:
                break
        while True:
            quest_update_popup = self.controller.update_quest()
            if isinstance(quest_update_popup, str) and quest_update_popup.strip():
                self.controller.play_soundeffect(NEW_QUEST_SOUND)
                self.open_popup("Quest Updated", quest_update_popup, PopupType.INFO)
            else:
                break
        while True:
            quest_popup = self.controller.activate_quest()
            if isinstance(quest_popup, str) and quest_popup.strip():
                self.controller.play_soundeffect(NEW_QUEST_SOUND)
                self.open_popup("Quest Activated", quest_popup, PopupType.INFO)
            else:
                break
        self.questlog_panel.update_questlog(
            self.controller.get_active_quests(), self.controller.get_completed_quests()
        )

    # Add default CSS for layout if not present
    BINDINGS = [("ctrl+q", "quit", "Quit")]

    async def action_quit(self) -> None:  # type: ignore[override]
        """Quit application (binding: ctrl+q)."""
        self.exit()
