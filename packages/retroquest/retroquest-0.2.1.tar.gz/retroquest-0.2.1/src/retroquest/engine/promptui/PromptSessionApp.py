"""Terminal-based UI using prompt_toolkit for command input and rich for output."""
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import NestedCompleter
from rich.console import Console
from rich.theme import Theme

from audio.soundeffects.SoundEffects import NEW_QUEST_SOUND, QUEST_COMPLETED_SOUND
from retroquest.engine import Game

class PromptSessionApp:
    """
    Prompt-based user interface for RetroQuest.
    """

    def __init__(self, game: Game) -> None:
        """Initialize the prompt session app with the given game instance."""
        custom_theme = Theme({
            "default": "black on #000000",
            "character_name": "bold blue",
            "dialogue": "italic cyan",
            "item_name": "bold green",
            "spell.name": "bold magenta",
            "room_name": "bold cyan",
            "quest_name": "red",
            "event": "dim",
            "failure": "bold red",
            "success": "bold green",
            "exits": "bold yellow"
        })
        self.console = Console(theme=custom_theme)
        self.completer = NestedCompleter.from_nested_dict({})
        self.session = PromptSession(completer=self.completer, complete_while_typing=True)
        self.game = game

    def get_output_text(self) -> str:
        """Get the current output text to display."""
        result =  self.game.get_result_text()
        if not self.game.is_act_running():
            return result
        if self.game.has_changed_room:
            # If the command resulted in a room change, describe the new room
            self.game.has_changed_room = False
            result += self.game.state.current_room.describe(self.game.state)
        txt = []
        quest_sound = 0
        while (quest := self.game.state.next_activated_quest()):
            quest_type = "main" if quest.is_main() else "side"
            txt.append(
                f"[quest_name]{quest.name} ({quest_type} quest)[/quest_name]\n{quest.description}"
            )
        if txt:
            result += "\n\nQuest(s) activated:\n" + "\n".join(txt)
            quest_sound = 1
        txt = []
        while (quest := self.game.state.next_updated_quest()):
            quest_type = "main" if quest.is_main() else "side"
            txt.append(
                f"[quest_name]{quest.name} ({quest_type} quest)[/quest_name]\n{quest.description}"
            )
        if txt:
            result += "\n\nQuest(s) updated:\n" + "\n".join(txt)
            quest_sound = 1
        txt = []
        while (quest := self.game.state.next_completed_quest()):
            quest_type = "main" if quest.is_main() else "side"
            txt.append(
                f"[quest_name]{quest.name} ({quest_type} quest)[/quest_name]\n{quest.description}"
            )
        if txt:
            result += "\n\nQuest(s) completed:\n" + "\n".join(txt)
            quest_sound = 2
        result += '\n'
        if quest_sound == 1:
            self.game.play_soundeffect(NEW_QUEST_SOUND)
        elif quest_sound == 2:
            self.game.play_soundeffect(QUEST_COMPLETED_SOUND)
        return result

    def run(self) -> None:
        """Main game loop that handles user input and updates the display."""
        while self.game.is_running:
            if (not (self.game.is_act_running() or self.game.is_act_transitioning())
                or self.game.has_changed_room):
                self.console.clear()
            self.console.print(self.get_output_text())
            if self.game.accept_input:
                completions = self.game.get_command_completions()
                self.session.completer = NestedCompleter.from_nested_dict(completions)
                user_input = self.session.prompt('> ')
                self.game.state.history.append(user_input)
                self.game.handle_input(user_input)
            else:
                self.session.prompt('Press Enter to continue...')
                self.game.handle_input('')
            self.game.new_turn()
