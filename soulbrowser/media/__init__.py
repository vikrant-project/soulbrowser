"""
Soul Browser Media Module

Advanced media playback, recording, and control features.
"""

from .player import MediaPlayer, MediaInfo, EqualizerPreset
from .recorder import MediaRecorder, RecordingConfig, RecordingFormat

__all__ = [
    "MediaPlayer", "MediaInfo", "EqualizerPreset",
    "MediaRecorder", "RecordingConfig", "RecordingFormat"
]
