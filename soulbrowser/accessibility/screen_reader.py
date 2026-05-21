"""Screen reader support and ARIA enhancements."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import asyncio


@dataclass
class ARIAConfig:
    """ARIA attributes configuration."""
    announce_page_changes: bool = True
    live_region_politeness: str = "polite"
    focus_indicators: bool = True
    landmark_navigation: bool = True
    heading_navigation: bool = True
    skip_links: bool = True


class ScreenReaderSupport:
    """Comprehensive screen reader support for Soul Browser."""
    
    def __init__(self, config: Optional[ARIAConfig] = None):
        self.config = config or ARIAConfig()
        self._announcements: List[str] = []
        self._focus_history: List[str] = []
        
    async def announce(self, message: str, priority: str = "polite") -> None:
        """Announce message to screen reader."""
        self._announcements.append({
            "message": message,
            "priority": priority,
            "timestamp": asyncio.get_event_loop().time()
        })
        
    async def get_page_structure(self, page) -> Dict[str, Any]:
        """Extract page structure for screen reader navigation."""
        return await page.evaluate("""() => {
            const structure = {
                headings: [],
                landmarks: [],
                links: [],
                forms: [],
                tables: [],
                images: []
            };
            
            // Collect headings
            document.querySelectorAll("h1,h2,h3,h4,h5,h6").forEach((h, i) => {
                structure.headings.push({
                    level: parseInt(h.tagName[1]),
                    text: h.textContent.trim(),
                    id: h.id || `heading-${i}`
                });
            });
            
            // Collect landmarks
            const landmarks = document.querySelectorAll(
                "[role=banner],[role=navigation],[role=main],[role=contentinfo]," +
                "[role=search],[role=complementary],[role=form]," +
                "header,nav,main,footer,aside,form"
            );
            landmarks.forEach((el, i) => {
                structure.landmarks.push({
                    role: el.getAttribute("role") || el.tagName.toLowerCase(),
                    label: el.getAttribute("aria-label") || "",
                    id: el.id || `landmark-${i}`
                });
            });
            
            // Collect links
            document.querySelectorAll("a[href]").forEach((a, i) => {
                structure.links.push({
                    text: a.textContent.trim() || a.getAttribute("aria-label") || "",
                    href: a.href,
                    id: a.id || `link-${i}`
                });
            });
            
            return structure;
        }""")
        
    async def enable_focus_tracking(self, page) -> None:
        """Enable focus tracking for keyboard navigation."""
        await page.evaluate("""() => {
            document.addEventListener("focusin", (e) => {
                const el = e.target;
                el.style.outline = "3px solid #4A90D9";
                el.style.outlineOffset = "2px";
            });
            document.addEventListener("focusout", (e) => {
                e.target.style.outline = "";
                e.target.style.outlineOffset = "";
            });
        }""")
        
    async def inject_skip_links(self, page) -> None:
        """Inject skip navigation links."""
        await page.evaluate("""() => {
            if (document.getElementById("soul-skip-links")) return;
            
            const skipNav = document.createElement("div");
            skipNav.id = "soul-skip-links";
            skipNav.innerHTML = `
                <a href="#main" class="soul-skip-link">Skip to main content</a>
                <a href="#nav" class="soul-skip-link">Skip to navigation</a>
                <a href="#search" class="soul-skip-link">Skip to search</a>
            `;
            
            const style = document.createElement("style");
            style.textContent = `
                .soul-skip-link {
                    position: absolute;
                    top: -40px;
                    left: 0;
                    background: #000;
                    color: #fff;
                    padding: 8px;
                    z-index: 100000;
                    transition: top 0.3s;
                }
                .soul-skip-link:focus {
                    top: 0;
                }
            `;
            
            document.head.appendChild(style);
            document.body.insertBefore(skipNav, document.body.firstChild);
        }""")
