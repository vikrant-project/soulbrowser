"""Input accessibility helpers."""

from dataclasses import dataclass
from typing import Optional, Dict, List, Callable
import asyncio


@dataclass
class InputConfig:
    """Input accessibility configuration."""
    sticky_keys: bool = False
    slow_keys_delay: int = 0
    bounce_keys_delay: int = 0
    mouse_keys: bool = False
    voice_control: bool = False


class InputHelpers:
    """Input accessibility helpers for Soul Browser."""
    
    def __init__(self, config: Optional[InputConfig] = None):
        self.config = config or InputConfig()
        self._key_modifiers: Dict[str, bool] = {
            "shift": False,
            "ctrl": False,
            "alt": False,
            "meta": False
        }
        
    async def enable_keyboard_navigation(self, page) -> None:
        """Enable enhanced keyboard navigation."""
        await page.evaluate("""() => {
            // Add visible focus indicators
            const style = document.createElement("style");
            style.id = "soul-keyboard-nav";
            style.textContent = `
                *:focus {
                    outline: 3px solid #4A90D9 !important;
                    outline-offset: 2px !important;
                }
                [tabindex]:focus {
                    outline: 3px solid #4A90D9 !important;
                }
            `;
            document.head.appendChild(style);
            
            // Add tabindex to clickable elements without it
            document.querySelectorAll("div[onclick], span[onclick]").forEach(el => {
                if (!el.hasAttribute("tabindex")) {
                    el.setAttribute("tabindex", "0");
                    el.setAttribute("role", "button");
                }
            });
        }""")
        
    async def enable_sticky_keys(self, page) -> None:
        """Enable sticky keys functionality."""
        await page.evaluate("""() => {
            let modifiers = { shift: false, ctrl: false, alt: false, meta: false };
            
            document.addEventListener("keydown", (e) => {
                if (["Shift", "Control", "Alt", "Meta"].includes(e.key)) {
                    const mod = e.key.toLowerCase().replace("control", "ctrl");
                    modifiers[mod] = !modifiers[mod];
                    
                    // Visual indicator
                    let indicator = document.getElementById("soul-sticky-indicator");
                    if (!indicator) {
                        indicator = document.createElement("div");
                        indicator.id = "soul-sticky-indicator";
                        indicator.style.cssText = `
                            position: fixed; bottom: 10px; right: 10px;
                            background: rgba(0,0,0,0.8); color: white;
                            padding: 5px 10px; border-radius: 5px;
                            font-family: monospace; z-index: 999999;
                        `;
                        document.body.appendChild(indicator);
                    }
                    
                    const active = Object.entries(modifiers)
                        .filter(([k, v]) => v)
                        .map(([k]) => k.toUpperCase())
                        .join(" + ");
                    indicator.textContent = active || "";
                    indicator.style.display = active ? "block" : "none";
                    
                    e.preventDefault();
                }
            });
        }""")
        
    async def get_focusable_elements(self, page) -> List[Dict]:
        """Get all focusable elements on page."""
        return await page.evaluate("""() => {
            const focusable = document.querySelectorAll(
                "a[href], button, input, textarea, select, " +
                "[tabindex]:not([tabindex=-1]), " +
                "[contenteditable=true]"
            );
            
            return Array.from(focusable).map((el, i) => ({
                index: i,
                tag: el.tagName.toLowerCase(),
                type: el.type || "",
                text: el.textContent?.trim().slice(0, 50) || "",
                label: el.getAttribute("aria-label") || "",
                id: el.id || "",
                tabindex: el.tabIndex
            }));
        }""")
        
    async def navigate_to_element(self, page, index: int) -> None:
        """Navigate focus to element by index."""
        await page.evaluate(f"""() => {{
            const focusable = document.querySelectorAll(
                "a[href], button, input, textarea, select, " +
                "[tabindex]:not([tabindex=-1])"
            );
            if (focusable[{index}]) {{
                focusable[{index}].focus();
                focusable[{index}].scrollIntoView({{ behavior: "smooth", block: "center" }});
            }}
        }}""")
