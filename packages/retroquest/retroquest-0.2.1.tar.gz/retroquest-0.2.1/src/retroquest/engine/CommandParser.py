"""Command parser for processing player input in RetroQuest."""
from __future__ import annotations

from typing import Any, TYPE_CHECKING

class CommandParser:
    """Parses and handles player commands for RetroQuest.

    Uses runtime calls into the Game instance; type hints use forward
    references to avoid circular imports.
    """

    if TYPE_CHECKING:
        from .Game import Game

    def __init__(self, game: "Game", dev_mode: bool = False) -> None:
        self.game = game
        self.last_raw: str | None = None
        self.dev_mode = dev_mode

    def parse(self, command: str) -> Any:
        """Parse and execute a player command, returning the result."""
        self.last_raw = command
        cmd = command.strip().lower()
        # Movement
        if cmd in ('go north', 'move north', 'north', 'n'):
            return self.game.move('north')
        elif cmd in ('go south', 'move south', 'south', 's'):
            return self.game.move('south')
        elif cmd in ('go east', 'move east', 'east', 'e'):
            return self.game.move('east')
        elif cmd in ('go west', 'move west', 'west', 'w'):
            return self.game.move('west')
        elif cmd.startswith('go '):
            # Handle other directions like "go secret_passage"
            direction = cmd[len('go '):].strip()
            return self.game.move(direction)
        # elif cmd.startswith('enter '):
        #     # Argument for "enter [location]" is cmd[len('enter '):].strip()
        #     # Current game.move('in') does not take an argument.
        #     return self.game.move('in', cmd[len('enter '):].strip())
        # elif cmd in ('go in', 'go inside'):
        #     return self.game.move('in')
        # elif cmd.startswith('leave '):
        #     # Argument for "leave [location]" is cmd[len('leave '):].strip()
        #     return self.game.move(
        #         'out', cmd[len('leave '):].strip()
        #     )  # Assuming 'out' handles the context
        # elif cmd.startswith('exit '):  # Handles "exit [location]" as per Commands.md
        #     # Argument for "exit [location]" is cmd[len('exit '):].strip()
        #     return self.game.move(
        #         'out', cmd[len('exit '):].strip()
        #     )  # Assuming 'out' handles the context
        # elif cmd == 'go out':
        #     return self.game.move('out')
        # elif cmd.startswith('climb '):
        #     # Argument for "climb [object]" is cmd[len('climb '):].strip()
        #     return self.game.move(
        #         'up', cmd[len('climb '):].strip()
        #     )  # Assuming 'up' handles the object context
        # elif cmd.startswith('ascend '):
        #     # Argument for "ascend [object]" is cmd[len('ascend '):].strip()
        #     return self.game.move(
        #         'up', cmd[len('ascend '):].strip()
        #     )  # Assuming 'up' handles the object context
        # elif cmd.startswith('descend '):
        #     # Argument for "descend [object]" is cmd[len('descend '):].strip()
        #     return self.game.move(
        #         'down', cmd[len('descend '):].strip()
        #     )  # Assuming 'down' handles the object context
        # elif cmd.startswith('go down '):  # Matches "go down [object]"
        #     # Argument for "go down [object]" is cmd[len('go down '):].strip()
        #     return self.game.move(
        #         'down', cmd[len('go down '):].strip()
        #     )  # Assuming 'down' handles the object context
        # elif cmd.startswith('follow '):
        #     arg = cmd[len('follow '):].strip()
        #     return self.game.move('follow', arg)
        # elif cmd.startswith('walk '):
        #     arg = cmd[len('walk '):].strip()
        #     return self.game.move(
        #         'follow', arg
        #     )  # Assuming 'walk' is an alias for 'follow' functionality

        # Interaction
        elif any(cmd.startswith(prefix) for prefix in
                 ('talk to ', 'speak to ', 'converse with ')):
            for prefix in ('talk to ', 'speak to ', 'converse with '):
                if cmd.startswith(prefix):
                    return self.game.talk(cmd[len(prefix):])
        elif cmd.startswith('say '):
            # Handle "say [word] to [character]"
            say_args = cmd[len('say '):].strip()
            if ' to ' in say_args:
                parts = say_args.split(' to ', 1)
                word = parts[0].strip()
                character = parts[1].strip()
                if word and character:
                    return self.game.say(word, character)
                else:
                    return (
                        "You need to specify both what to say and who to say it to. "
                        "Use say <word> to <character>"
                    )
            else:
                return (
                    "You need to specify who to say that to. "
                    "Use say <word> to <character>"
                )
        elif any(cmd.startswith(prefix) for prefix in
                 ('give ', 'hand ')):  # e.g. give bread to grandmother
            # This will pass "bread to grandmother". Game.give needs to parse it.
            for prefix in ('give ', 'hand '):
                if cmd.startswith(prefix):
                    return self.game.give(cmd[len(prefix):])
        elif cmd.startswith('buy '):  # e.g. buy rope from shopkeeper
            # This will pass "rope from shopkeeper". Game.buy needs to parse it.
            return self.game.buy(cmd[len('buy '):])
        # Examination
        elif cmd in ('look', 'observe', 'survey', 'l'):
            return self.game.look()
        elif any(cmd.startswith(prefix) for prefix in
                 ('look at ', 'inspect ', 'examine ', 'check ', 'look ')):
            for prefix in ('look at ', 'inspect ', 'examine ', 'check ', 'look '):
                if cmd.startswith(prefix):
                    return self.game.examine(cmd[len(prefix):])
        elif cmd == 'search' or cmd == 'investigate':
            return self.game.search()
        # elif cmd.startswith('listen to '):
        #     return self.game.listen(cmd[len('listen to '):])

        # Inventory Management
        elif any(cmd.startswith(prefix) for prefix in
                 ('take ', 'pick up ', 'grab ', 'get ')):
            for prefix in ('take ', 'pick up ', 'grab ', 'get '):
                if cmd.startswith(prefix):
                    return self.game.take(cmd[len(prefix):])
        elif any(cmd.startswith(prefix) for prefix in ('drop ', 'discard ')):
            for prefix in ('drop ', 'discard '):
                if cmd.startswith(prefix):
                    return self.game.drop(cmd[len(prefix):])
        elif cmd == 'use':
            return "What do you want to use?"
        elif cmd.startswith('use '):
            # Use the original command (not fully stripped) to preserve trailing spaces
            # to detect incomplete patterns
            original_tail = command[len('use '):]
            stripped_tail = original_tail.strip()
            if not stripped_tail:
                return "What do you want to use?"
            # Detect pattern ending with ' with' meaning second item missing
            if original_tail.lower().rstrip().endswith(' with'):
                return (
                    "You need to specify two items to use with each other. "
                    "Format: use <item1> with <item2>"
                )
            lower_tail = stripped_tail.lower()
            if ' with ' in lower_tail:
                # Split on the first occurrence of ' with ' using the original
                # (case-sensitive) stripped_tail for item names
                split_index = lower_tail.find(' with ')
                item1_name = stripped_tail[:split_index].strip()
                object_name = stripped_tail[split_index + 6:].strip()
                if not item1_name or not object_name:
                    return (
                        "You need to specify two items to use with each other. "
                        "Format: use <item1> with <item2>"
                    )
                return self.game.use(item1_name, object_name)
            else:
                return self.game.use(stripped_tail)  # General single-item usage
        # elif any(cmd.startswith(prefix) for prefix in ('eat ', 'consume ')):
        #     for prefix in ('eat ', 'consume '):
        #         if cmd.startswith(prefix):
        #             return self.game.eat(cmd[len(prefix):])
        # elif cmd.startswith('drink '):
        #     return self.game.drink(cmd[len('drink '):])
        # elif any(cmd.startswith(prefix) for prefix in ('equip ', 'wear ')):
        #     for prefix in ('equip ', 'wear '):
        #         if cmd.startswith(prefix):
        #             return self.game.equip(cmd[len(prefix):])
        # elif any(cmd.startswith(prefix) for prefix in ('unequip ', 'remove ')):
        #     for prefix in ('unequip ', 'remove '):
        #         if cmd.startswith(prefix):
        #             return self.game.unequip(cmd[len(prefix):])
        elif cmd in ('inventory', 'i', 'inv'):
            return self.game.inventory()
        elif cmd.startswith('open '):
            return self.game.open(cmd[len('open '):])
        elif cmd.startswith('close '):
            return self.game.close(cmd[len('close '):])

        # Magic
        elif cmd.startswith('cast '):  # Handles "cast [spell]" and "cast [spell] on [target]"
            # game.cast will receive the full string after "cast ", e.g., "revive" or
            # "fireball on goblin"
            return self.game.cast(cmd[len('cast '):])
        elif cmd == 'spells':
            return self.game.spells()  # Assumes game.spells() method exists

        # Game Management
        elif cmd in ('save',):
            return self.game.save()
        elif cmd in ('load',):
            return self.game.load()
        elif cmd in ('help', '?'):
            return self.game.help()
        elif cmd in ('quit', 'exit'):
            return self.game.quit()

        # Miscellaneous
        elif cmd in ('sleep', 'rest'):
            return self.game.rest()
        elif cmd == 'map':
            return self.game.map()
        elif cmd == 'stats':
            return self.game.stats()
        elif cmd.startswith('dev_execute_commands ') and self.dev_mode:
            filename = cmd[len('dev_execute_commands '):].strip()
            return self.game.dev_execute_commands(filename)
        else:
            return self.game.unknown(cmd)
