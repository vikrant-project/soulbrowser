"""Soul Browser UI Module - Advanced UI/UX Components."""

from .theme import ThemeManager, Theme, DarkMode
from .tabs import TabManager, TabGroup
from .gestures import GestureController
from .keyboard import KeyboardShortcuts

__all__ = [
    "ThemeManager", "Theme", "DarkMode",
    "TabManager", "TabGroup",
    "GestureController", "KeyboardShortcuts"
]
