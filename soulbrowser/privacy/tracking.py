"""Soul Browser Tracking Protection Module."""

from __future__ import annotations
import re
import logging
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass, field

logger = logging.getLogger("soulbrowser.tracking")

# Known tracking domains
TRACKING_DOMAINS: Set[str] = {
    "doubleclick.net", "googlesyndication.com", "google-analytics.com",
    "googletagmanager.com", "googleadservices.com", "facebook.net",
    "facebook.com/tr", "connect.facebook.net", "fbcdn.net",
    "twitter.com/i/adsct", "ads.twitter.com", "analytics.twitter.com",
    "pixel.facebook.com", "an.facebook.com", "adsserver.zynga.com",
    "scorecardresearch.com", "quantserve.com", "adsrvr.org",
    "adnxs.com", "rubiconproject.com", "pubmatic.com", "openx.net",
    "criteo.com", "outbrain.com", "taboola.com", "amazon-adsystem.com",
    "bing.com/action", "bat.bing.com", "hotjar.com", "mouseflow.com",
    "fullstory.com", "clarity.ms", "crazyegg.com", "luckyorange.com",
    "mixpanel.com", "amplitude.com", "segment.io", "segment.com",
    "rudderstack.com", "heap.io", "keen.io", "plausible.io",
    "matomo.cloud", "piwik.pro", "chartbeat.com", "parsely.com",
    "newrelic.com", "nr-data.net", "appsflyer.com", "adjust.com",
    "branch.io", "kochava.com", "singular.net", "airship.com",
}

# Tracking URL patterns
TRACKING_PATTERNS: List[str] = [
    r"utm_source=", r"utm_medium=", r"utm_campaign=", r"utm_content=",
    r"fbclid=", r"gclid=", r"msclkid=", r"dclid=", r"twclid=",
    r"\_ga=", r"\_gid=", r"\_fbp=", r"\_fbc=", r"mc_eid=",
    r"ref=", r"referrer=", r"source=", r"affiliate=",
]


@dataclass
class TrackingStats:
    """Statistics for tracking protection."""
    requests_blocked: int = 0
    trackers_identified: int = 0
    cookies_blocked: int = 0
    scripts_blocked: int = 0
    pixels_blocked: int = 0


class TrackingProtection:
    """ML-enhanced tracking protection for Soul Browser."""
    
    def __init__(self, strict_mode: bool = False):
        self.strict_mode = strict_mode
        self.stats = TrackingStats()
        self._blocked_domains: Set[str] = TRACKING_DOMAINS.copy()
        self._patterns = [re.compile(p) for p in TRACKING_PATTERNS]
        self._custom_rules: List[str] = []
    
    def add_custom_rule(self, domain_or_pattern: str) -> None:
        """Add a custom blocking rule."""
        if domain_or_pattern.startswith("r:"):
            self._patterns.append(re.compile(domain_or_pattern[2:]))
        else:
            self._blocked_domains.add(domain_or_pattern)
        self._custom_rules.append(domain_or_pattern)
    
    def is_tracker(self, url: str) -> bool:
        """Check if a URL is a known tracker."""
        url_lower = url.lower()
        
        # Check domain blocklist
        for domain in self._blocked_domains:
            if domain in url_lower:
                return True
        
        # Check URL patterns
        for pattern in self._patterns:
            if pattern.search(url):
                return True
        
        return False
    
    def clean_url(self, url: str) -> str:
        """Remove tracking parameters from a URL."""
        if "?" not in url:
            return url
        
        base, query = url.split("?", 1)
        params = query.split("&")
        clean_params = []
        
        for param in params:
            is_tracking = False
            for pattern in self._patterns:
                if pattern.match(param):
                    is_tracking = True
                    break
            if not is_tracking:
                clean_params.append(param)
        
        if clean_params:
            return f"{base}?{'&'.join(clean_params)}"
        return base
    
    def get_blocking_script(self) -> str:
        """Get JavaScript for blocking tracking."""
        domains_json = str(list(self._blocked_domains))
        return f'''
(function() {{
    const blocked = {domains_json};
    
    // Block tracking requests
    const origFetch = window.fetch;
    window.fetch = function(url) {{
        const urlStr = typeof url === "string" ? url : url.url || "";
        for (const d of blocked) {{
            if (urlStr.includes(d)) {{
                return Promise.resolve(new Response("", {{ status: 204 }}));
            }}
        }}
        return origFetch.apply(this, arguments);
    }};
    
    // Block XHR
    const origOpen = XMLHttpRequest.prototype.open;
    XMLHttpRequest.prototype.open = function(method, url) {{
        for (const d of blocked) {{
            if (url.includes(d)) {{
                this._blocked = true;
                return;
            }}
        }}
        return origOpen.apply(this, arguments);
    }};
    
    const origSend = XMLHttpRequest.prototype.send;
    XMLHttpRequest.prototype.send = function() {{
        if (this._blocked) return;
        return origSend.apply(this, arguments);
    }};
    
    // Block sendBeacon
    const origBeacon = navigator.sendBeacon;
    navigator.sendBeacon = function(url) {{
        for (const d of blocked) {{
            if (url.includes(d)) return true;
        }}
        return origBeacon.apply(this, arguments);
    }};
    
    // Block tracking pixels
    const origImage = window.Image;
    window.Image = function() {{
        const img = new origImage();
        const desc = Object.getOwnPropertyDescriptor(HTMLImageElement.prototype, "src");
        Object.defineProperty(img, "src", {{
            set: function(url) {{
                for (const d of blocked) {{
                    if (url.includes(d)) return;
                }}
                desc.set.call(this, url);
            }},
            get: function() {{ return desc.get.call(this); }}
        }});
        return img;
    }};
}})();
'''
    
    def get_cookie_protection_script(self) -> str:
        """Get script for cookie protection."""
        return '''
(function() {
    const origCookie = Object.getOwnPropertyDescriptor(Document.prototype, "cookie");
    const trackingCookies = ["_ga", "_gid", "_fbp", "_fbc", "fr", "sb", "wd"];
    
    Object.defineProperty(document, "cookie", {
        get: function() { return origCookie.get.call(this); },
        set: function(val) {
            const name = val.split("=")[0].trim();
            if (!trackingCookies.includes(name)) {
                origCookie.set.call(this, val);
            }
        }
    });
})();
'''
    
    def apply_to_page(self, page: Any) -> None:
        try:
            page.add_init_script(self.get_blocking_script())
            page.add_init_script(self.get_cookie_protection_script())
        except Exception as e:
            logger.warning(f"Failed to apply tracking protection: {e}")
    
    async def apply_to_page_async(self, page: Any) -> None:
        try:
            await page.add_init_script(self.get_blocking_script())
            await page.add_init_script(self.get_cookie_protection_script())
        except Exception as e:
            logger.warning(f"Failed to apply tracking protection: {e}")
    
    def get_stats(self) -> TrackingStats:
        return self.stats
