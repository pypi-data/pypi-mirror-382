"""Tests for audio-related Game behavior and for the Audio helper class."""

import importlib

def test_audio_play_soundeffect_and_start_music(monkeypatch):
    """Audio should initialize mixer, load sound and play it, and start music."""
    audio_module = importlib.import_module('retroquest.engine.Audio')
    events = []

    # Mock mixer init/get_init and Sound
    monkeypatch.setattr(audio_module.pygame.mixer, 'get_init', lambda: False)
    monkeypatch.setattr(audio_module.pygame.mixer, 'init', lambda: events.append('mixer_init'))

    class FakeSound:
        """Fake Sound object that records load and play events."""

        def __init__(self, path):
            events.append(('sound_loaded', path))

        def play(self):
            """Record that the sound was played."""
            events.append('sound_played')

    monkeypatch.setattr(audio_module.pygame.mixer, 'Sound', FakeSound)

    # Replace Thread so target runs synchronously for testing
    class FakeThread:
        """Thread replacement that runs target synchronously for tests."""

        def __init__(self, target, *args, **kwargs):
            # store the target function to run synchronously
            self._target = target
            # Accept any additional args/kwargs from real Thread
            _ = args
            __ = kwargs
            events.append('thread_created')

        def start(self):
            """Start the fake thread by invoking its target immediately."""
            events.append('thread_started')
            self._target()

    monkeypatch.setattr(audio_module.threading, 'Thread', FakeThread)

    # Test play_soundeffect
    a = audio_module.Audio()
    a.play_soundeffect('sfx.wav')
    assert ('sound_loaded', 'audio/soundeffects/sfx.wav') in events
    assert 'sound_played' in events

    # Clear events and test start_music
    events.clear()

    # Mock music loader and player
    class FakeMusic:
        """Fake music controller that records load/play/stop events."""

        def load(self, path):
            """Record that music was loaded."""
            events.append(('music_loaded', path))

        def play(self, loops=-1):
            """Record that music was played with given loop count."""
            events.append(('music_played', loops))

        def stop(self):
            """Record that music was stopped."""
            events.append('music_stopped')

    monkeypatch.setattr(audio_module.pygame.mixer, 'music', FakeMusic())

    a.start_music('bg.mp3')
    assert ('music_loaded', 'audio/music/bg.mp3') in events
    assert ('music_played', -1) in events


def test_audio_start_music_no_file(monkeypatch):
    """start_music should do nothing for empty or None music file."""
    audio_module = importlib.import_module('retroquest.engine.Audio')
    events = []

    class FakeThread:
        """Thread replacement that records creation/start but does not run target."""

        def __init__(self, *args, **kwargs):
            # Accept and ignore any args/kwargs passed by callers
            _ = args
            __ = kwargs
            events.append('thread_created')

        def start(self):
            """Record that a fake thread was started."""
            events.append('thread_started')

    monkeypatch.setattr(audio_module.threading, 'Thread', FakeThread)

    a = audio_module.Audio()
    a.start_music('')
    a.start_music(None)
    # No thread should have been created
    assert not events
