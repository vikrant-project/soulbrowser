"""Soul Browser Keyboard Shortcuts."""

from __future__ import annotations
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Callable, Any, Set
from enum import Enum

logger = logging.getLogger("soulbrowser.ui.keyboard")


class Modifier(Enum):
    """Keyboard modifiers."""
    CTRL = "ctrl"
    ALT = "alt"
    SHIFT = "shift"
    META = "meta"  # Cmd on Mac, Win on Windows


@dataclass
class KeyBinding:
    """Keyboard shortcut binding."""
    key: str
    modifiers: Set[Modifier]
    action: str
    description: str
    enabled: bool = True


class KeyboardShortcuts:
    """Keyboard shortcut manager."""
    
    DEFAULT_SHORTCUTS = [
        # Navigation
        KeyBinding("t", {Modifier.CTRL}, "new_tab", "Open new tab"),
        KeyBinding("w", {Modifier.CTRL}, "close_tab", "Close current tab"),
        KeyBinding("Tab", {Modifier.CTRL}, "next_tab", "Switch to next tab"),
        KeyBinding("Tab", {Modifier.CTRL, Modifier.SHIFT}, "prev_tab", "Switch to previous tab"),
        KeyBinding("1", {Modifier.CTRL}, "tab_1", "Switch to tab 1"),
        KeyBinding("2", {Modifier.CTRL}, "tab_2", "Switch to tab 2"),
        KeyBinding("3", {Modifier.CTRL}, "tab_3", "Switch to tab 3"),
        KeyBinding("9", {Modifier.CTRL}, "tab_last", "Switch to last tab"),
        KeyBinding("n", {Modifier.CTRL}, "new_window", "Open new window"),
        KeyBinding("n", {Modifier.CTRL, Modifier.SHIFT}, "new_incognito", "Open incognito window"),
        KeyBinding("t", {Modifier.CTRL, Modifier.SHIFT}, "reopen_tab", "Reopen closed tab"),
        
        # Page actions
        KeyBinding("r", {Modifier.CTRL}, "reload", "Reload page"),
        KeyBinding("r", {Modifier.CTRL, Modifier.SHIFT}, "hard_reload", "Hard reload (bypass cache)"),
        KeyBinding("Escape", set(), "stop_loading", "Stop loading"),
        KeyBinding("l", {Modifier.CTRL}, "focus_url", "Focus URL bar"),
        KeyBinding("d", {Modifier.CTRL}, "bookmark", "Bookmark page"),
        KeyBinding("f", {Modifier.CTRL}, "find", "Find on page"),
        KeyBinding("g", {Modifier.CTRL}, "find_next", "Find next"),
        KeyBinding("g", {Modifier.CTRL, Modifier.SHIFT}, "find_prev", "Find previous"),
        KeyBinding("p", {Modifier.CTRL}, "print", "Print page"),
        KeyBinding("s", {Modifier.CTRL}, "save_page", "Save page"),
        KeyBinding("u", {Modifier.CTRL}, "view_source", "View page source"),
        
        # History & Bookmarks
        KeyBinding("h", {Modifier.CTRL}, "history", "Open history"),
        KeyBinding("b", {Modifier.CTRL, Modifier.SHIFT}, "bookmarks", "Open bookmarks"),
        KeyBinding("j", {Modifier.CTRL}, "downloads", "Open downloads"),
        KeyBinding("Left", {Modifier.ALT}, "back", "Go back"),
        KeyBinding("Right", {Modifier.ALT}, "forward", "Go forward"),
        
        # Zoom
        KeyBinding("+", {Modifier.CTRL}, "zoom_in", "Zoom in"),
        KeyBinding("-", {Modifier.CTRL}, "zoom_out", "Zoom out"),
        KeyBinding("0", {Modifier.CTRL}, "zoom_reset", "Reset zoom"),
        KeyBinding("f", {Modifier.CTRL, Modifier.SHIFT}, "fullscreen", "Toggle fullscreen"),
        
        # Developer
        KeyBinding("i", {Modifier.CTRL, Modifier.SHIFT}, "devtools", "Open DevTools"),
        KeyBinding("j", {Modifier.CTRL, Modifier.SHIFT}, "console", "Open Console"),
        KeyBinding("c", {Modifier.CTRL, Modifier.SHIFT}, "inspect", "Inspect element"),
        
        # Soul Browser Special
        KeyBinding("p", {Modifier.CTRL, Modifier.SHIFT}, "privacy_mode", "Toggle privacy mode"),
        KeyBinding("a", {Modifier.CTRL, Modifier.SHIFT}, "ad_blocker", "Toggle ad blocker"),
        KeyBinding("m", {Modifier.CTRL, Modifier.SHIFT}, "dark_mode", "Toggle dark mode"),
        KeyBinding("v", {Modifier.CTRL, Modifier.SHIFT}, "vpn", "Toggle VPN"),
        KeyBinding("k", {Modifier.CTRL}, "command_palette", "Open command palette"),
        KeyBinding("e", {Modifier.CTRL, Modifier.SHIFT}, "extensions", "Open extensions"),
        KeyBinding(",", {Modifier.CTRL}, "settings", "Open settings"),
    ]
    
    def __init__(self):
        self._shortcuts: Dict[str, KeyBinding] = {}
        self._action_handlers: Dict[str, Callable] = {}
        self._enabled = True
        self._load_defaults()
    
    def _load_defaults(self) -> None:
        """Load default shortcuts."""
        for shortcut in self.DEFAULT_SHORTCUTS:
            key = self._get_key(shortcut.key, shortcut.modifiers)
            self._shortcuts[key] = shortcut
    
    def _get_key(self, key: str, modifiers: Set[Modifier]) -> str:
        """Generate a unique key for the shortcut."""
        mod_str = "+".join(sorted(m.value for m in modifiers))
        return f"{mod_str}+{key}" if mod_str else key
    
    def add_shortcut(self, key: str, modifiers: Set[Modifier], action: str, description: str) -> None:
        """Add a keyboard shortcut."""
        binding = KeyBinding(key, modifiers, action, description)
        shortcut_key = self._get_key(key, modifiers)
        self._shortcuts[shortcut_key] = binding
    
    def remove_shortcut(self, key: str, modifiers: Set[Modifier]) -> bool:
        """Remove a keyboard shortcut."""
        shortcut_key = self._get_key(key, modifiers)
        return self._shortcuts.pop(shortcut_key, None) is not None
    
    def register_handler(self, action: str, handler: Callable) -> None:
        """Register an action handler."""
        self._action_handlers[action] = handler
    
    def handle_key(self, key: str, modifiers: Set[Modifier]) -> bool:
        """Handle a key press."""
        if not self._enabled:
            return False
        
        shortcut_key = self._get_key(key, modifiers)
        binding = self._shortcuts.get(shortcut_key)
        
        if not binding or not binding.enabled:
            return False
        
        handler = self._action_handlers.get(binding.action)
        if handler:
            try:
                handler()
                return True
            except Exception as e:
                logger.error(f"Shortcut handler failed: {e}")
        
        return False
    
    def list_shortcuts(self) -> List[KeyBinding]:
        """List all shortcuts."""
        return list(self._shortcuts.values())
    
    def get_shortcuts_by_category(self) -> Dict[str, List[KeyBinding]]:
        """Get shortcuts organized by category."""
        categories = {
            "Navigation": ["new_tab", "close_tab", "next_tab", "prev_tab", "tab_1", "tab_2", "tab_3", "tab_last", "new_window", "new_incognito", "reopen_tab"],
            "Page": ["reload", "hard_reload", "stop_loading", "focus_url", "bookmark", "find", "find_next", "find_prev", "print", "save_page", "view_source"],
            "History": ["history", "bookmarks", "downloads", "back", "forward"],
            "Zoom": ["zoom_in", "zoom_out", "zoom_reset", "fullscreen"],
            "Developer": ["devtools", "console", "inspect"],
            "Soul Browser": ["privacy_mode", "ad_blocker", "dark_mode", "vpn", "command_palette", "extensions", "settings"],
        }
        
        result = {}
        for category, actions in categories.items():
            result[category] = [
                binding for binding in self._shortcuts.values()
                if binding.action in actions
            ]
        
        return result
    
    def get_injection_script(self) -> str:
        """Get script for keyboard shortcut detection."""
        return """
(function() {
    document.addEventListener("keydown", function(e) {
        const modifiers = [];
        if (e.ctrlKey) modifiers.push("ctrl");
        if (e.altKey) modifiers.push("alt");
        if (e.shiftKey) modifiers.push("shift");
        if (e.metaKey) modifiers.push("meta");
        
        window.postMessage({
            type: "soul_keyboard",
            key: e.key,
            modifiers: modifiers
        }, "*");
    });
})();
"""
    
    def apply_to_page(self, page: Any) -> None:
        """Apply keyboard scripts to a page."""
        try:
            page.add_init_script(self.get_injection_script())
        except Exception as e:
            logger.warning(f"Failed to inject keyboard scripts: {e}")
    
    def export_shortcuts(self) -> List[Dict]:
        """Export shortcuts configuration."""
        return [
            {
                "key": b.key,
                "modifiers": [m.value for m in b.modifiers],
                "action": b.action,
                "description": b.description,
                "enabled": b.enabled
            }
            for b in self._shortcuts.values()
        ]
    
    def import_shortcuts(self, shortcuts: List[Dict]) -> None:
        """Import shortcuts configuration."""
        for shortcut in shortcuts:
            try:
                modifiers = {Modifier(m) for m in shortcut.get("modifiers", [])}
                self.add_shortcut(
                    shortcut["key"],
                    modifiers,
                    shortcut["action"],
                    shortcut.get("description", "")
                )
            except (KeyError, ValueError) as e:
                logger.warning(f"Invalid shortcut: {shortcut}, {e}")
