"""Audio subsystem: handles music and sound effects playback."""

import threading
from typing import Optional


def _import_pygame() -> Optional[object]:
    """Attempt to import pygame; return module or None if unavailable.

    Importing pygame can fail in headless CI or test environments. Defer the
    import until audio is actually requested so the rest of the engine can be
    imported without a hard dependency on pygame.
    """
    try:
        import pygame as pygame_module  # type: ignore

        return pygame_module
    except ImportError:
        return None


# Expose a module-level `pygame` object. If pygame isn't available, provide a
# small dummy with a `mixer` attribute so tests can monkeypatch
# `audio_module.pygame.mixer.*` without AttributeError.
_pygame_module = _import_pygame()
if _pygame_module is None:
    class _DummyMixer:
        """Minimal dummy mixer namespace used in tests when pygame is absent."""

    class _DummyPygame:
        mixer = _DummyMixer()

    pygame = _DummyPygame()
else:
    pygame = _pygame_module


class Audio:
    """Encapsulate audio playback (music and sound effects)."""

    def __init__(self) -> None:
        """Create an Audio helper bound to the owning Game instance."""

    def play_soundeffect(self, filename: str) -> None:
        """Play a sound effect (wav/ogg) mixed with music. Non-blocking."""
        pygame = _import_pygame()
        if pygame is None:
            print("[dim]Could not import pygame. Audio will not be available.[/dim]")
            return

        def play_fx():
            try:
                if not pygame.mixer.get_init():
                    pygame.mixer.init()
                sound = pygame.mixer.Sound('audio/soundeffects/' + filename)
                sound.play()
            except RuntimeError as e:
                print(f"[dim]Could not play sound effect '{filename}': {e}[/dim]")

        threading.Thread(target=play_fx, daemon=True).start()

    def start_music(self, music_file: str) -> None:
        """Start background music in a non-blocking thread if a file is provided."""
        pygame = _import_pygame()
        if pygame is None:
            return

        def play_music() -> None:
            try:
                if pygame.mixer.get_init():
                    pygame.mixer.music.stop()
                else:
                    pygame.mixer.init()
                music_path = 'audio/music/' + music_file
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.play(loops=-1)
            except RuntimeError as e:
                print(f"[dim]Could not play music: {e}[/dim]")

        if music_file is not None and music_file != '':
            threading.Thread(target=play_music, daemon=True).start()
