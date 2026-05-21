"""Soul Browser Theme Management."""

from __future__ import annotations
import logging
from dataclasses import dataclass, field
from typing import Dict, Optional, Any, List
from enum import Enum

logger = logging.getLogger("soulbrowser.ui.theme")


class ThemeMode(Enum):
    """Theme mode options."""
    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"
    CUSTOM = "custom"


@dataclass
class ColorPalette:
    """Color palette for themes."""
    primary: str = "#6366f1"
    secondary: str = "#8b5cf6"
    background: str = "#ffffff"
    surface: str = "#f8fafc"
    text: str = "#1e293b"
    text_secondary: str = "#64748b"
    border: str = "#e2e8f0"
    accent: str = "#06b6d4"
    success: str = "#22c55e"
    warning: str = "#f59e0b"
    error: str = "#ef4444"


@dataclass
class Theme:
    """Theme configuration."""
    name: str
    mode: ThemeMode
    colors: ColorPalette = field(default_factory=ColorPalette)
    font_family: str = "Inter, system-ui, sans-serif"
    font_size_base: int = 14
    border_radius: int = 8
    animations_enabled: bool = True
    blur_effects: bool = True


class DarkMode:
    """Universal dark mode for all websites."""
    
    DARK_MODE_CSS = """
    html {
        filter: invert(1) hue-rotate(180deg) !important;
    }
    img, video, picture, canvas, iframe, embed, 
    [style*="background-image"], svg {
        filter: invert(1) hue-rotate(180deg) !important;
    }
    [data-dark-mode-ignore] {
        filter: none !important;
    }
    """
    
    SMART_DARK_MODE_JS = """
    (function() {
        const style = document.createElement("style");
        style.id = "soul-dark-mode";
        style.textContent = `
            :root {
                --soul-bg: #1a1a2e;
                --soul-surface: #16213e;
                --soul-text: #eee;
                --soul-text-muted: #a0a0a0;
            }
            * {
                scrollbar-color: #555 #1a1a2e;
            }
            body {
                background-color: var(--soul-bg) !important;
                color: var(--soul-text) !important;
            }
            article, section, main, div, p, span, li, td, th, header, footer, nav, aside {
                background-color: transparent !important;
                color: inherit !important;
            }
            a { color: #7dd3fc !important; }
            a:visited { color: #c4b5fd !important; }
            input, textarea, select, button {
                background-color: var(--soul-surface) !important;
                color: var(--soul-text) !important;
                border-color: #334155 !important;
            }
        `;
        document.head.appendChild(style);
    })();
    """
    
    def __init__(self, enabled: bool = False, smart_mode: bool = True):
        self.enabled = enabled
        self.smart_mode = smart_mode
    
    def get_injection_script(self) -> str:
        if not self.enabled:
            return ""
        return self.SMART_DARK_MODE_JS if self.smart_mode else f"""
        (function() {{
            const style = document.createElement("style");
            style.id = "soul-dark-mode";
            style.textContent = `{self.DARK_MODE_CSS}`;
            document.head.appendChild(style);
        }})();
        """
    
    def apply_to_page(self, page: Any) -> None:
        if self.enabled:
            try:
                page.add_init_script(self.get_injection_script())
            except Exception as e:
                logger.warning(f"Failed to inject dark mode: {e}")


class ThemeManager:
    """Manages browser themes and appearance."""
    
    BUILTIN_THEMES = {
        "default": Theme(
            name="Default",
            mode=ThemeMode.LIGHT,
            colors=ColorPalette()
        ),
        "dark": Theme(
            name="Dark",
            mode=ThemeMode.DARK,
            colors=ColorPalette(
                background="#0f172a",
                surface="#1e293b",
                text="#f1f5f9",
                text_secondary="#94a3b8",
                border="#334155"
            )
        ),
        "midnight": Theme(
            name="Midnight",
            mode=ThemeMode.DARK,
            colors=ColorPalette(
                primary="#818cf8",
                background="#030712",
                surface="#111827",
                text="#f9fafb",
                text_secondary="#9ca3af",
                border="#1f2937",
                accent="#22d3ee"
            )
        ),
        "nord": Theme(
            name="Nord",
            mode=ThemeMode.DARK,
            colors=ColorPalette(
                primary="#88c0d0",
                secondary="#81a1c1",
                background="#2e3440",
                surface="#3b4252",
                text="#eceff4",
                text_secondary="#d8dee9",
                border="#4c566a",
                accent="#a3be8c"
            )
        ),
        "solarized": Theme(
            name="Solarized Dark",
            mode=ThemeMode.DARK,
            colors=ColorPalette(
                primary="#268bd2",
                secondary="#2aa198",
                background="#002b36",
                surface="#073642",
                text="#839496",
                text_secondary="#657b83",
                border="#586e75",
                accent="#b58900"
            )
        ),
    }
    
    def __init__(self):
        self._current_theme = self.BUILTIN_THEMES["default"]
        self._custom_themes: Dict[str, Theme] = {}
        self._dark_mode = DarkMode()
    
    @property
    def current_theme(self) -> Theme:
        return self._current_theme
    
    def set_theme(self, theme_name: str) -> bool:
        if theme_name in self.BUILTIN_THEMES:
            self._current_theme = self.BUILTIN_THEMES[theme_name]
            return True
        if theme_name in self._custom_themes:
            self._current_theme = self._custom_themes[theme_name]
            return True
        return False
    
    def add_custom_theme(self, theme: Theme) -> None:
        self._custom_themes[theme.name.lower()] = theme
    
    def list_themes(self) -> List[str]:
        return list(self.BUILTIN_THEMES.keys()) + list(self._custom_themes.keys())
    
    def enable_dark_mode(self, smart_mode: bool = True) -> None:
        self._dark_mode.enabled = True
        self._dark_mode.smart_mode = smart_mode
    
    def disable_dark_mode(self) -> None:
        self._dark_mode.enabled = False
    
    def get_css_variables(self) -> str:
        colors = self._current_theme.colors
        return f"""
        :root {{
            --soul-primary: {colors.primary};
            --soul-secondary: {colors.secondary};
            --soul-background: {colors.background};
            --soul-surface: {colors.surface};
            --soul-text: {colors.text};
            --soul-text-secondary: {colors.text_secondary};
            --soul-border: {colors.border};
            --soul-accent: {colors.accent};
            --soul-success: {colors.success};
            --soul-warning: {colors.warning};
            --soul-error: {colors.error};
            --soul-font-family: {self._current_theme.font_family};
            --soul-font-size-base: {self._current_theme.font_size_base}px;
            --soul-border-radius: {self._current_theme.border_radius}px;
        }}
        """
