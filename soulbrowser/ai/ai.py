"""Soul Browser AI Module."""

from __future__ import annotations
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger("soulbrowser.ai")


class ContentSummarizer:
    """AI-powered content summarization."""
    
    def __init__(self):
        self._summaries: Dict[str, str] = {}
    
    def get_extraction_script(self) -> str:
        """Get script for content extraction."""
        return '''
(function() {
    window.soulBrowserAI = {
        extractContent: function() {
            // Get main content
            const article = document.querySelector("article") || document.body;
            const text = article.innerText;
            
            // Get headings
            const headings = Array.from(document.querySelectorAll("h1, h2, h3"))
                .map(h => h.innerText);
            
            return {
                text: text.substring(0, 10000),
                headings: headings,
                title: document.title,
                url: location.href
            };
        },
        
        highlightText: function(keywords) {
            keywords.forEach(keyword => {
                const regex = new RegExp("(" + keyword + ")", "gi");
                document.body.innerHTML = document.body.innerHTML.replace(
                    regex, "<mark>$1</mark>"
                );
            });
        }
    };
})();
'''
    
    def apply_to_page(self, page: Any) -> None:
        try:
            page.add_init_script(self.get_extraction_script())
        except Exception as e:
            logger.warning(f"Failed to inject AI scripts: {e}")


class SmartSearch:
    """AI-enhanced search functionality."""
    
    def __init__(self):
        self._history: List[str] = []
    
    def add_to_history(self, query: str) -> None:
        self._history.append(query)
        if len(self._history) > 100:
            self._history = self._history[-100:]
    
    def get_suggestions(self, prefix: str) -> List[str]:
        """Get search suggestions based on history."""
        prefix_lower = prefix.lower()
        return [q for q in self._history if q.lower().startswith(prefix_lower)][:5]


class PredictiveLoader:
    """Predictive page preloading based on user behavior."""
    
    def __init__(self):
        self._link_clicks: Dict[str, int] = {}
    
    def record_click(self, url: str) -> None:
        self._link_clicks[url] = self._link_clicks.get(url, 0) + 1
    
    def get_preload_candidates(self) -> List[str]:
        """Get URLs likely to be visited next."""
        sorted_links = sorted(self._link_clicks.items(), key=lambda x: x[1], reverse=True)
        return [url for url, _ in sorted_links[:5]]
    
    def get_preload_script(self) -> str:
        """Get script for predictive preloading."""
        return '''
(function() {
    // Track link hovers for preloading
    document.addEventListener("mouseover", function(e) {
        const link = e.target.closest("a");
        if (link && link.href && link.href.startsWith("http")) {
            // Prefetch on hover
            const prefetch = document.createElement("link");
            prefetch.rel = "prefetch";
            prefetch.href = link.href;
            document.head.appendChild(prefetch);
        }
    }, { passive: true });
})();
'''
