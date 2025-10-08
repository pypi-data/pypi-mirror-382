"""RetroQuest Entry Point

This module provides the executable entry point for launching RetroQuest.

Responsibilities:
- Parse minimal CLI switches (currently only `-oldschool` to select prompt-based UI).
- Construct the `Game` instance with the ordered list of Acts to play.
- Instantiate and run either the Textual (rich TUI) or legacy prompt UI.

Design Notes:
- Acts are instantiated eagerly so that any cross-act setup (e.g., shared flags via
    engine) occurs before UI initialization.
- The previous temporary override to run only `Act3` has been removed in favor of the
    full progression `[Act1, Act2, Act3]`.
- Extend CLI argument handling here if additional runtime configuration flags are
    introduced (e.g., `--skip-act2`, `--load <save>`).

Usage:
`python -m retroquest` launches with the default Textual UI.
`python -m retroquest -oldschool` launches the simpler prompt-driven UI.
"""

import sys
from retroquest.engine.textualui.TextualApp import TextualApp
from retroquest.engine.promptui.PromptSessionApp import PromptSessionApp
from retroquest.engine.Game import Game
from retroquest.act1.Act1 import Act1
from retroquest.act2.Act2 import Act2
from retroquest.act3.Act3 import Act3

USE_TEXTUAL_UI = True

if '-oldschool' in sys.argv:
    USE_TEXTUAL_UI = False

def main() -> None:
    """Initialize and run the RetroQuest game loop.

    Steps:
    1. Build a `Game` with the full ordered Act sequence.
     2. Select UI implementation based on the `USE_TEXTUAL_UI` flag (set via CLI
         switch).
     3. Run the chosen application which manages the event loop until exit.

    Side Effects:
    - Creates UI application object and begins its run loop.
    - May read future CLI arguments (currently only `-oldschool`).
    """
    game = Game([Act1(), Act2(), Act3()], dev_mode=False)
    # game = Game([Act3()], dev_mode=True)
    app = TextualApp(game) if USE_TEXTUAL_UI else PromptSessionApp(game)
    app.run()

if __name__ == '__main__':
    main()
