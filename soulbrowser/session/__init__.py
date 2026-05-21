"""
Soul Browser Session Module

Session management, tab management, and workspace features.
"""

from .session_manager import SessionManager
from .tab_manager import TabManager
from .workspace import WorkspaceManager

__all__ = ["SessionManager", "TabManager", "WorkspaceManager"]
