"""Soul Browser Ad Blocker Implementation."""

from __future__ import annotations
import re
import logging
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass, field
from enum import Enum, auto

logger = logging.getLogger("soulbrowser.adblock")

# Common ad domains
AD_DOMAINS: Set[str] = {
    "doubleclick.net", "googlesyndication.com", "googleadservices.com",
    "googleads.g.doubleclick.net", "pagead2.googlesyndication.com",
    "adservice.google.com", "adsrvr.org", "adnxs.com", "rubiconproject.com",
    "pubmatic.com", "openx.net", "criteo.com", "outbrain.com", "taboola.com",
    "amazon-adsystem.com", "adsymptotic.com", "advertising.com", "contextweb.com",
    "zedo.com", "adbrite.com", "bidswitch.net", "casalemedia.com",
    "emxdgt.com", "indexww.com", "lijit.com", "media.net", "mediamath.com",
    "mgid.com", "mopub.com", "nativo.net", "popads.net", "propellerads.com",
    "revcontent.com", "richaudience.com", "sharethrough.com", "smartadserver.com",
    "sovrn.com", "spotxchange.com", "teads.tv", "undertone.com", "yieldmo.com",
}

# Ad-related URL patterns
AD_PATTERNS: List[str] = [
    r"/ads?/", r"/advert", r"/banner", r"\.gif\?ad", r"ad\.php",
    r"ads\.js", r"adserv", r"adtrack", r"adview", r"affiliate",
    r"pagead", r"popunder", r"popup", r"sponsor", r"tracking",
]


class FilterType(Enum):
    """Type of ad blocking filter."""
    NETWORK = auto()
    COSMETIC = auto()
    SCRIPT = auto()
    EXCEPTION = auto()


@dataclass
class FilterRule:
    """A single ad blocking filter rule."""
    pattern: str
    filter_type: FilterType
    domains: List[str] = field(default_factory=list)
    exception_domains: List[str] = field(default_factory=list)
    is_regex: bool = False
    _compiled: Optional[re.Pattern] = None
    
    def matches(self, url: str, domain: str = "") -> bool:
        """Check if this rule matches a URL."""
        if self.domains and domain not in self.domains:
            return False
        if self.exception_domains and domain in self.exception_domains:
            return False
        
        if self.is_regex:
            if not self._compiled:
                self._compiled = re.compile(self.pattern, re.IGNORECASE)
            return bool(self._compiled.search(url))
        
        return self.pattern.lower() in url.lower()


@dataclass
class FilterList:
    """A collection of filter rules."""
    name: str
    url: Optional[str] = None
    rules: List[FilterRule] = field(default_factory=list)
    enabled: bool = True
    
    @classmethod
    def from_text(cls, name: str, text: str) -> "FilterList":
        """Parse a filter list from text (EasyList format)."""
        rules = []
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("!") or line.startswith("["):
                continue
            
            rule = cls._parse_rule(line)
            if rule:
                rules.append(rule)
        
        return cls(name=name, rules=rules)
    
    @staticmethod
    def _parse_rule(line: str) -> Optional[FilterRule]:
        """Parse a single filter rule."""
        if line.startswith("##"):  # Cosmetic filter
            return FilterRule(
                pattern=line[2:],
                filter_type=FilterType.COSMETIC
            )
        elif line.startswith("@@"):  # Exception
            return FilterRule(
                pattern=line[2:],
                filter_type=FilterType.EXCEPTION
            )
        elif "##" in line:  # Domain-specific cosmetic
            parts = line.split("##", 1)
            domains = parts[0].split(",")
            return FilterRule(
                pattern=parts[1],
                filter_type=FilterType.COSMETIC,
                domains=domains
            )
        else:  # Network filter
            return FilterRule(
                pattern=line,
                filter_type=FilterType.NETWORK
            )


class AdBlocker:
    """Advanced ad blocker for Soul Browser.
    
    Supports multiple filter lists, cosmetic filtering, and scriptlet injection.
    Compatible with uBlock Origin and EasyList filter formats.
    """
    
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self._filter_lists: List[FilterList] = []
        self._blocked_domains = AD_DOMAINS.copy()
        self._patterns = [re.compile(p, re.IGNORECASE) for p in AD_PATTERNS]
        self._stats = {
            "ads_blocked": 0,
            "trackers_blocked": 0,
            "scripts_blocked": 0,
        }
        
        # Initialize with built-in rules
        self._init_builtin_rules()
    
    def _init_builtin_rules(self) -> None:
        """Initialize built-in blocking rules."""
        builtin = FilterList(
            name="Soul Browser Built-in",
            rules=[
                FilterRule(domain, FilterType.NETWORK)
                for domain in self._blocked_domains
            ]
        )
        self._filter_lists.append(builtin)
    
    def add_filter_list(self, filter_list: FilterList) -> None:
        """Add a filter list."""
        self._filter_lists.append(filter_list)
    
    def add_custom_rule(self, pattern: str, filter_type: FilterType = FilterType.NETWORK) -> None:
        """Add a custom blocking rule."""
        rule = FilterRule(pattern=pattern, filter_type=filter_type)
        if not self._filter_lists:
            self._filter_lists.append(FilterList(name="Custom"))
        self._filter_lists[0].rules.append(rule)
    
    def should_block(self, url: str, domain: str = "") -> bool:
        """Check if a URL should be blocked."""
        if not self.enabled:
            return False
        
        url_lower = url.lower()
        
        # Check domain blocklist
        for blocked in self._blocked_domains:
            if blocked in url_lower:
                self._stats["ads_blocked"] += 1
                return True
        
        # Check patterns
        for pattern in self._patterns:
            if pattern.search(url):
                self._stats["ads_blocked"] += 1
                return True
        
        # Check filter lists
        for fl in self._filter_lists:
            if not fl.enabled:
                continue
            for rule in fl.rules:
                if rule.filter_type == FilterType.EXCEPTION:
                    if rule.matches(url, domain):
                        return False
                elif rule.filter_type == FilterType.NETWORK:
                    if rule.matches(url, domain):
                        self._stats["ads_blocked"] += 1
                        return True
        
        return False
    
    def get_cosmetic_rules(self, domain: str = "") -> List[str]:
        """Get cosmetic (element hiding) rules for a domain."""
        rules = []
        for fl in self._filter_lists:
            if not fl.enabled:
                continue
            for rule in fl.rules:
                if rule.filter_type == FilterType.COSMETIC:
                    if not rule.domains or domain in rule.domains:
                        if domain not in rule.exception_domains:
                            rules.append(rule.pattern)
        return rules
    
    def get_blocking_script(self) -> str:
        """Get JavaScript for ad blocking."""
        domains = list(self._blocked_domains)
        patterns = AD_PATTERNS
        
        return f'''
(function() {{
    const blockedDomains = {domains};
    const blockedPatterns = {patterns};
    
    function isBlocked(url) {{
        const u = url.toLowerCase();
        for (const d of blockedDomains) {{
            if (u.includes(d)) return true;
        }}
        for (const p of blockedPatterns) {{
            if (new RegExp(p, "i").test(u)) return true;
        }}
        return false;
    }}
    
    // Block fetch requests
    const origFetch = window.fetch;
    window.fetch = function(url) {{
        const urlStr = typeof url === "string" ? url : (url.url || "");
        if (isBlocked(urlStr)) {{
            return Promise.resolve(new Response("", {{ status: 204 }}));
        }}
        return origFetch.apply(this, arguments);
    }};
    
    // Block XHR
    const origOpen = XMLHttpRequest.prototype.open;
    XMLHttpRequest.prototype.open = function(method, url) {{
        if (isBlocked(url)) {{
            this._blocked = true;
            return;
        }}
        return origOpen.apply(this, arguments);
    }};
    
    const origSend = XMLHttpRequest.prototype.send;
    XMLHttpRequest.prototype.send = function() {{
        if (this._blocked) return;
        return origSend.apply(this, arguments);
    }};
    
    // Block ad iframes
    const origCreateElement = document.createElement;
    document.createElement = function(tag) {{
        const el = origCreateElement.apply(this, arguments);
        if (tag.toLowerCase() === "iframe") {{
            const origSrc = Object.getOwnPropertyDescriptor(HTMLIFrameElement.prototype, "src");
            Object.defineProperty(el, "src", {{
                set: function(url) {{
                    if (!isBlocked(url)) origSrc.set.call(this, url);
                }},
                get: function() {{ return origSrc.get.call(this); }}
            }});
        }}
        return el;
    }};
    
    // Block ad images
    const origImage = window.Image;
    window.Image = function() {{
        const img = new origImage();
        const desc = Object.getOwnPropertyDescriptor(HTMLImageElement.prototype, "src");
        Object.defineProperty(img, "src", {{
            set: function(url) {{
                if (!isBlocked(url)) desc.set.call(this, url);
            }},
            get: function() {{ return desc.get.call(this); }}
        }});
        return img;
    }};
}})();
'''
    
    def get_cosmetic_script(self, domain: str = "") -> str:
        """Get JavaScript for cosmetic filtering (element hiding)."""
        rules = self.get_cosmetic_rules(domain)
        if not rules:
            return ""
        
        # Standard ad element selectors
        standard_selectors = [
            '[class*="ad-"]', '[class*="-ad"]', '[class*="_ad"]',
            '[class*="ads-"]', '[class*="-ads"]', '[class*="_ads"]',
            '[id*="ad-"]', '[id*="-ad"]', '[id*="_ad"]',
            '[id*="ads-"]', '[id*="-ads"]', '[id*="_ads"]',
            '[class*="banner"]', '[id*="banner"]',
            '[class*="sponsor"]', '[id*="sponsor"]',
            'iframe[src*="ads"]', 'iframe[src*="doubleclick"]',
            'div[data-ad]', 'div[data-ads]', 'div[data-adunit]',
        ]
        
        all_selectors = list(set(rules + standard_selectors))
        selectors_str = ", ".join(all_selectors[:100])  # Limit to prevent performance issues
        
        return f'''
(function() {{
    const selectors = `{selectors_str}`;
    
    function hideAds() {{
        try {{
            document.querySelectorAll(selectors).forEach(function(el) {{
                el.style.display = "none";
                el.style.visibility = "hidden";
                el.style.height = "0";
                el.style.overflow = "hidden";
            }});
        }} catch(e) {{}}
    }}
    
    // Run immediately
    if (document.readyState !== "loading") {{
        hideAds();
    }} else {{
        document.addEventListener("DOMContentLoaded", hideAds);
    }}
    
    // Run on mutations
    const observer = new MutationObserver(hideAds);
    observer.observe(document.documentElement, {{
        childList: true,
        subtree: true
    }});
    
    // Run periodically
    setInterval(hideAds, 2000);
}})();
'''
    
    def apply_to_page(self, page: Any, domain: str = "") -> None:
        """Apply ad blocking to a page."""
        if not self.enabled:
            return
        
        try:
            page.add_init_script(self.get_blocking_script())
            cosmetic = self.get_cosmetic_script(domain)
            if cosmetic:
                page.add_init_script(cosmetic)
        except Exception as e:
            logger.warning(f"Failed to apply ad blocking: {e}")
    
    async def apply_to_page_async(self, page: Any, domain: str = "") -> None:
        """Apply ad blocking to a page (async)."""
        if not self.enabled:
            return
        
        try:
            await page.add_init_script(self.get_blocking_script())
            cosmetic = self.get_cosmetic_script(domain)
            if cosmetic:
                await page.add_init_script(cosmetic)
        except Exception as e:
            logger.warning(f"Failed to apply ad blocking: {e}")
    
    def get_stats(self) -> Dict[str, int]:
        return self._stats.copy()
    
    def reset_stats(self) -> None:
        self._stats = {"ads_blocked": 0, "trackers_blocked": 0, "scripts_blocked": 0}
