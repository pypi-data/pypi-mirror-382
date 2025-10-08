"""Shared theme for RetroQuest UI components."""
# Shared theme for RetroQuest (used by both Rich and Textual UIs)
custom_theme = {
    "character_name": "bold blue",
    "dialogue": "italic cyan",
    "item_name": "bold green",
    "spell_name": "bold magenta",
    "room_name": "bold cyan",
    "quest_name": "#5050d0",
    "event": "dim",
    "failure": "bold red",
    "success": "bold green",
    "exits": "bold yellow"
}

def apply_theme(s: str) -> str:
    """
    Replace all occurrences of '[key]' in the string s with '[value]' for each key in custom_theme.
    """
    for key, value in custom_theme.items():
        s = s.replace(f"[{key}]", f"[{value}]")
        s = s.replace(f"[/{key}]", f"[/{value}]")
    return s

