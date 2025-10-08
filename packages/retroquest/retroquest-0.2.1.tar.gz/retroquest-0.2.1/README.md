# RetroQuest: A Text Adventure Built with AI

Welcome to RetroQuest, a text adventure game built with GitHub Copilot! This project explores how far AI can go in creating a complete game with tests and game mechanics.

## How It Started

I started working on this text adventure in December 2024, but the project went dormant after just the initial commits.

In May 2025, I decided to try an experiment: What if GitHub Copilot could help finish this game? Could AI write all of the code and tests with just guidance from me? That's how RetroQuest was reborn - not just as a game, but as a test of pure AI-agent development.

## How Human and AI Work Together

Here's how I work with the AI to build this game:

-   **Planning:** I give the AI prompts and describe what needs to be built.
-   **Review:** I check all the code and tests the AI creates, giving feedback to make them better.
-   **Debugging:** When the AI gets stuck or makes mistakes, I work with AI to find the issues and then let the AI do the actual fixing.

It's a partnership where I provide direction and the AI does all of the coding work.
My role is to provide prompts and occationally do minor string edits, whitespace removals, etc.

## How to Play

### Starting the game

A simple command in your terminal gets the adventure underway:

```bash
python -m retroquest
```

This will run the game in Text mode, allowing you to immerse yourself in the adventure. If you instead want to run the game in more old-school terminal mode, you can use:

```bash
python -m retroquest -oldschool
```

### Commands

The game supports a variety of commands to navigate and interact with the world. However, the only command you will need to use to complete the game is:

```
help
```

This command will show you the list of all available commands in the game. You can also use the `?` command as a shortcut for `help`.

### Found issues?
Write an issue on GitHub and I'll have copilot take a look at it.

### Got stuck?
Likely a bug as well, look at the design files to see how to actually move forward or write an issue here as well.
