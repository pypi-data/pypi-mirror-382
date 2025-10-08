# Design Rules

This document outlines the design rules and guidelines for both the game story and the implementation the game, focusing on key design patterns, technical considerations, and content guidelines to ensure a cohesive and engaging player experience.

## Hard Formatting & Static Rules (Enforced)

These MUST be satisfied for every Python file. Pull requests must explicitly state:
"Formatting constraints verified".

1. Maximum physical line length: 99 characters (count all characters including indentation).
2. Prefer keeping narrative lines ≤95 chars to allow safe future edits.
3. No tabs; indentation is 4 spaces.
4. No trailing whitespace anywhere.
5. Exactly one newline at end of file.
6. One-line module docstring for single-class modules (strictly one line, no wrapping).
7. All overridden methods (e.g., search, get_exits, gating helpers) require docstrings.
8. Unused parameters must be prefixed with an underscore (e.g., \_game_state, \_target).
9. Long prose must be wrapped by splitting into multiple adjacent string literals inside parentheses.
10. Avoid lines ending at 99 if possible; leave a small buffer for later wording refinements.

Violation of any item is grounds for rejection in code review / CI.

### Wrapping Guidance

When writing long narrative or return strings:

-   Wrap inside a parenthesized block using multiple string literals.
-   Break on sentence or clause boundaries; never split inside a word.
-   Keep each physical line ≤99 chars including indentation.
-   For f-strings nearing the limit, extract dynamic segments to variables first.

Example:

```
description = (
		"The hall extends into shadow, banners stirring in a draft that smells of old "
		"parchment and steel. A faint glow outlines a sealed archway ahead."
)
```

### Developer Completion Checklist (Must Pass Before Commit)

-   [ ] All lines ≤99 chars (`python scripts/check_line_length.py`).
-   [ ] No tabs / no trailing whitespace.
-   [ ] One-line module docstring where required.
-   [ ] All custom overrides documented.
-   [ ] Unused parameters underscored.
-   [ ] Docstrings updated to reflect changes.

### Automation (Recommended)

Add a custom line-length gate plus Ruff to enforce style:

`scripts/check_line_length.py` (example):

```
import sys
from pathlib import Path

MAX = 99
errors = []
for path in Path('src').rglob('*.py'):
		for i, line in enumerate(path.read_text().splitlines(), start=1):
				if len(line) > MAX:
						errors.append(f"{path}:{i}: {len(line)} > {MAX}")
if errors:
		print('Line length violations:')
		print('\n'.join(errors))
		sys.exit(1)
```

Pre-commit hook snippet:

```
repos:
	- repo: local
		hooks:
			- id: line-length
				name: Enforce 99-char line length
				entry: python scripts/check_line_length.py
				language: system
				pass_filenames: false
	- repo: https://github.com/astral-sh/ruff-pre-commit
		rev: v0.6.9
		hooks:
			- id: ruff
				args: [--line-length=99]
			- id: ruff-format
```

`.editorconfig` excerpt:

```
[*]
indent_style = space
indent_size = 4
trim_trailing_whitespace = true
insert_final_newline = true
max_line_length = 99
```

VS Code settings suggestion:

```
{
	"editor.rulers": [99],
	"files.trimTrailingWhitespace": true,
	"editor.wordWrap": "off"
}
```

## Game Story Design Rules

### Narrative Structure

-   Each act should have a main quest that drives the story forward, with side quests that enrich the world and characters.
-   The story should unfold through a series of key events that reveal character backstories, world lore, and the overarching conflict.
-   Each act should also have a number of side quests that provide additional context and depth to the main narrative.
-   All side quests need to be completed before the main quest can be finished, ensuring players fully engage with the story.
-   The design should describe a golden path through the story which contain all the steps needed to complete all quests, including the main quest and side quests.
-   The design should also contain additional optional content that can be explored for deeper lore and character development.

### Character Development

-   Characters should have distinct personalities, motivations, and arcs that evolve throughout the game.

### Dialogue

-   Dialogue should be engaging and reflect the character's personality.
-   Dialogue choices should impact relationships and story outcomes, allowing for player agency.

### World-Building

-   The world should be rich with lore, with locations, items, and characters that contribute to the overall narrative.
-   Locations should be interconnected, with logical transitions and exploration opportunities.

## Implementation Design Rules

### Architecture

-   Use a modular architecture that allows for easy expansion and maintenance.
-   Follow established design patterns for quest management, character interactions, and spell systems.
-   Implement a centralized game state management system to track player progress, story flags, and inventory.

### Quest Management

-   Quests should be structured in a way that allows for branching paths and dependencies.
-   Use a quest chain architecture where the main quest of an act is built up from all the side quests.
-   Each quest should have clear objectives, rewards, and consequences that affect the game world and player choices.

### Spell System

-   Spells should be learned through interactions with characters or found in the world.
-   Implement a spell learning system that requires specific conditions to be met before a spell can be taught.
-   Spells should have logical prerequisites and unlock in a way that feels natural to the player.

### Character Interactions

-   Characters should have rich dialogues.
-   Character states should change based on quest progress, affecting future interactions and story outcomes.

### Technical Considerations

These instructions are mandatory for all code contributions to ensure consistency, maintainability, and quality across the codebase. It shall be taken into account when doing any edits in any python file.

-   Ensure integration with existing systems, such as Game.py, GameState.py, and Quest.py base classes.
-   Maintain compatibility with the user interface system and save/load functionality.
-   Uses object-oriented programming principles to encapsulate game logic and data.
-   Create one class per file and name files according to the class they contain.
-   Use descriptive names for classes, methods, and variables to enhance readability and maintainability.
-   Use type hints for all function signatures to improve code clarity and facilitate static analysis.
-   Include docstrings for all modules, classes, functions and methods to explain their purpose and usage.
-   Follow PEP 8 style guidelines for Python code to ensure consistency across the codebase.
-   Do not share code between acts; each act should be self-contained. All common functionality should be implemented in the engine module.
-   Always update docstrings and comments to reflect any changes made to the code.
-   For files that contain only one class, make the module docstring a one-liner summarizing the class's purpose. no more than that! Just one line!
-   For files with multiple classes or functions, provide a somewhat more detailed module docstring explaining the overall purpose and functionality of the module.
-   Lines MUST NEVER exceed a maximum of 99 characters (including indentation spaces) for better readability. Be sure to really count EVERY character on a line. Be very thourough when counting characters!
-   Indentation spaces should be just that, spaces, not tab characters
-   Never use pylint inline directives in the code. All pylint configuration should be global
-   Never have trailing whitespace in any line
-   Always have a single newline at the end of each file
-   Prefix unused parameters with an underscore (e.g., \_game_state, \_target)
-   When mixing strings and variables, prioritize using f-strings when constructing messages or dialogues.
-   No trailing whitespaces at the end of lines

### Testing

-   All components in the engine should have extensive unit tests.
-   Every component in every act should also have unit tests. These tests should test the dynamics and behavior of the component, e.g. dynamic dialogues and things that change in the component depending on actions. Try to mock as little as possible and instead use the real implementations where feasible. The component tests should be placed in a similar structure to the code, ie. tests/retroquest/act<num>/rooms for rooms.
-   Use integration tests to verify that all steps in the golden path of the act works as expected, that the act can be completed successfully and that all quests are properly integrated.

### Details

-   Try to use isinstance when checking types, as it is more robust than comparing types directly. Avoid circular imports by doing local imports inside functions if needed.
-   Avoid using magic strings or numbers; instead, use constants or enums to represent important values.
-   When using multi-line strings, align the lines so that they match the indentation of the surrounding code.

## Chat

In the chat, try to be concise when describing what you are about to do, what you are doing and what you have done. Avoid unnecessary verbosity. Focus on the key changes or additions you are making to the codebase. This helps in maintaining clarity and efficiency in communication.
