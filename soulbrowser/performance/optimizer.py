"""Soul Browser Performance Optimizer."""

from __future__ import annotations
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger("soulbrowser.performance")


@dataclass
class PerformanceMetrics:
    """Performance metrics."""
    page_load_time: float = 0.0
    dom_content_loaded: float = 0.0
    first_contentful_paint: float = 0.0
    largest_contentful_paint: float = 0.0
    time_to_interactive: float = 0.0
    total_blocking_time: float = 0.0
    cumulative_layout_shift: float = 0.0
    memory_usage: int = 0
    cpu_usage: float = 0.0


class CacheManager:
    """Cache management for Soul Browser."""
    
    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or Path.home() / ".soulbrowser" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._cache: Dict[str, Any] = {}
        self._max_size = 500 * 1024 * 1024  # 500MB
    
    def get(self, key: str) -> Optional[Any]:
        return self._cache.get(key)
    
    def set(self, key: str, value: Any) -> None:
        self._cache[key] = value
    
    def clear(self) -> None:
        self._cache.clear()
        import shutil
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)
            self.cache_dir.mkdir(parents=True, exist_ok=True)


class PerformanceOptimizer:
    """Performance optimization manager for Soul Browser.
    
    Provides GPU acceleration, memory optimization, and caching strategies.
    """
    
    def __init__(self):
        self.cache = CacheManager()
        self._metrics = PerformanceMetrics()
    
    def get_optimization_args(self) -> List[str]:
        """Get Chrome arguments for performance optimization."""
        return [
            # GPU acceleration
            "--enable-gpu-rasterization",
            "--enable-zero-copy",
            "--enable-hardware-overlays=single-fullscreen,single-on-top",
            "--ignore-gpu-blacklist",
            "--enable-native-gpu-memory-buffers",
            
            # Memory optimization
            "--memory-pressure-off",
            "--max-old-space-size=4096",
            "--js-flags=--max-old-space-size=4096",
            
            # Network optimization
            "--enable-quic",
            "--enable-tcp-fastopen",
            "--enable-features=NetworkService,NetworkServiceInProcess",
            
            # Rendering optimization
            "--enable-features=ParallelDownloading",
            "--enable-smooth-scrolling",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
            
            # Process optimization
            "--process-per-site",
            "--renderer-process-limit=8",
        ]
    
    def get_lazy_loading_script(self) -> str:
        """Get JavaScript for lazy loading optimization."""
        return '''
(function() {
    // Native lazy loading for images
    document.querySelectorAll("img:not([loading])").forEach(function(img) {
        img.loading = "lazy";
    });
    
    // Lazy load iframes
    document.querySelectorAll("iframe:not([loading])").forEach(function(iframe) {
        iframe.loading = "lazy";
    });
    
    // IntersectionObserver for custom lazy loading
    if ("IntersectionObserver" in window) {
        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    const el = entry.target;
                    if (el.dataset.src) {
                        el.src = el.dataset.src;
                        delete el.dataset.src;
                    }
                    observer.unobserve(el);
                }
            });
        }, { rootMargin: "100px" });
        
        document.querySelectorAll("[data-src]").forEach(function(el) {
            observer.observe(el);
        });
    }
})();
'''
    
    def get_preload_script(self) -> str:
        """Get JavaScript for resource preloading."""
        return '''
(function() {
    // Preconnect to common CDNs
    const cdns = [
        "https://fonts.googleapis.com",
        "https://fonts.gstatic.com",
        "https://cdn.jsdelivr.net",
        "https://cdnjs.cloudflare.com"
    ];
    
    cdns.forEach(function(cdn) {
        const link = document.createElement("link");
        link.rel = "preconnect";
        link.href = cdn;
        link.crossOrigin = "anonymous";
        document.head.appendChild(link);
    });
    
    // DNS prefetch for external links
    document.querySelectorAll("a[href^='http']").forEach(function(a) {
        try {
            const url = new URL(a.href);
            if (url.hostname !== location.hostname) {
                const link = document.createElement("link");
                link.rel = "dns-prefetch";
                link.href = url.origin;
                document.head.appendChild(link);
            }
        } catch(e) {}
    });
})();
'''
    
    def get_memory_optimization_script(self) -> str:
        """Get JavaScript for memory optimization."""
        return '''
(function() {
    // Clean up detached DOM elements periodically
    setInterval(function() {
        if (window.gc) {
            try { window.gc(); } catch(e) {}
        }
    }, 60000);
    
    // Remove unused event listeners on unload
    window.addEventListener("beforeunload", function() {
        document.querySelectorAll("*").forEach(function(el) {
            const clone = el.cloneNode(true);
            if (el.parentNode) {
                el.parentNode.replaceChild(clone, el);
            }
        });
    });
})();
'''
    
    def apply_to_page(self, page: Any) -> None:
        """Apply performance optimizations to a page."""
        try:
            page.add_init_script(self.get_lazy_loading_script())
            page.add_init_script(self.get_preload_script())
        except Exception as e:
            logger.warning(f"Failed to apply performance optimizations: {e}")
    
    async def apply_to_page_async(self, page: Any) -> None:
        """Apply performance optimizations to a page (async)."""
        try:
            await page.add_init_script(self.get_lazy_loading_script())
            await page.add_init_script(self.get_preload_script())
        except Exception as e:
            logger.warning(f"Failed to apply performance optimizations: {e}")
    
    def get_metrics(self) -> PerformanceMetrics:
        return self._metrics
