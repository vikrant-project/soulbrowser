"""Visual accessibility aids."""

from dataclasses import dataclass
from typing import Optional, Tuple
import asyncio


@dataclass
class VisualConfig:
    """Visual accessibility configuration."""
    high_contrast: bool = False
    large_text: bool = False
    text_scale: float = 1.0
    reduce_motion: bool = False
    color_filter: Optional[str] = None  # protanopia, deuteranopia, tritanopia
    cursor_size: str = "normal"  # normal, large, xlarge
    focus_highlight: bool = True
    

class VisualAids:
    """Visual accessibility aids for Soul Browser."""
    
    def __init__(self, config: Optional[VisualConfig] = None):
        self.config = config or VisualConfig()
        
    async def apply_high_contrast(self, page, enabled: bool = True) -> None:
        """Apply high contrast mode."""
        if enabled:
            await page.evaluate("""() => {
                const style = document.createElement("style");
                style.id = "soul-high-contrast";
                style.textContent = `
                    * {
                        background-color: #000 !important;
                        color: #fff !important;
                        border-color: #fff !important;
                    }
                    a { color: #ffff00 !important; }
                    img { filter: invert(1) hue-rotate(180deg) !important; }
                `;
                document.head.appendChild(style);
            }""")
        else:
            await page.evaluate("""() => {
                const style = document.getElementById("soul-high-contrast");
                if (style) style.remove();
            }""")
            
    async def apply_text_scaling(self, page, scale: float = 1.5) -> None:
        """Apply text scaling."""
        await page.evaluate(f"""() => {{
            document.documentElement.style.fontSize = "{scale * 100}%";
        }}""")
        
    async def apply_color_filter(self, page, filter_type: str) -> None:
        """Apply color blindness filter."""
        filters = {
            "protanopia": "url(#protanopia-filter)",
            "deuteranopia": "url(#deuteranopia-filter)",
            "tritanopia": "url(#tritanopia-filter)",
            "achromatopsia": "grayscale(100%)"
        }
        
        if filter_type in filters:
            await page.evaluate(f"""() => {{
                // Add SVG filters for color blindness simulation
                const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
                svg.id = "soul-color-filters";
                svg.innerHTML = `
                    <defs>
                        <filter id="protanopia-filter">
                            <feColorMatrix type="matrix" values="
                                0.567,0.433,0,0,0
                                0.558,0.442,0,0,0
                                0,0.242,0.758,0,0
                                0,0,0,1,0"/>
                        </filter>
                        <filter id="deuteranopia-filter">
                            <feColorMatrix type="matrix" values="
                                0.625,0.375,0,0,0
                                0.7,0.3,0,0,0
                                0,0.3,0.7,0,0
                                0,0,0,1,0"/>
                        </filter>
                        <filter id="tritanopia-filter">
                            <feColorMatrix type="matrix" values="
                                0.95,0.05,0,0,0
                                0,0.433,0.567,0,0
                                0,0.475,0.525,0,0
                                0,0,0,1,0"/>
                        </filter>
                    </defs>
                `;
                document.body.appendChild(svg);
                document.documentElement.style.filter = "{filters[filter_type]}";
            }}""")
            
    async def reduce_motion(self, page, enabled: bool = True) -> None:
        """Reduce or eliminate animations."""
        if enabled:
            await page.evaluate("""() => {
                const style = document.createElement("style");
                style.id = "soul-reduce-motion";
                style.textContent = `
                    *, *::before, *::after {
                        animation-duration: 0.001ms !important;
                        animation-iteration-count: 1 !important;
                        transition-duration: 0.001ms !important;
                    }
                `;
                document.head.appendChild(style);
            }""")
            
    async def enhance_cursor(self, page, size: str = "large") -> None:
        """Enhance cursor visibility."""
        sizes = {"large": "32px", "xlarge": "48px"}
        cursor_size = sizes.get(size, "24px")
        
        await page.evaluate(f"""() => {{
            const style = document.createElement("style");
            style.id = "soul-cursor-enhance";
            style.textContent = `
                * {{ cursor: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='{cursor_size}' height='{cursor_size}' viewBox='0 0 24 24'%3E%3Cpath fill='%23000' stroke='%23fff' stroke-width='2' d='M5 3l14 9-7 2-4 7-3-18z'/%3E%3C/svg%3E") 0 0, auto !important; }}
            `;
            document.head.appendChild(style);
        }}""")
