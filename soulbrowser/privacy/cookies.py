"""Soul Browser Cookie Isolation Module."""

from __future__ import annotations
import hashlib
from typing import Dict, Set, Optional, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger("soulbrowser.cookies")


@dataclass
class CookieContainer:
    """Isolated cookie container for a domain."""
    domain: str
    cookies: Dict[str, str]
    first_party_only: bool = True


class CookieIsolation:
    """Cookie isolation manager for Soul Browser.
    
    Provides first-party isolation and domain-level cookie containers.
    """
    
    def __init__(self, first_party_isolation: bool = True):
        self.first_party_isolation = first_party_isolation
        self._containers: Dict[str, CookieContainer] = {}
        self._blocked_cookies: Set[str] = set()
    
    def get_container(self, domain: str) -> CookieContainer:
        """Get or create a cookie container for a domain."""
        if domain not in self._containers:
            self._containers[domain] = CookieContainer(
                domain=domain,
                cookies={},
                first_party_only=self.first_party_isolation
            )
        return self._containers[domain]
    
    def block_cookie(self, name: str) -> None:
        """Block a specific cookie by name."""
        self._blocked_cookies.add(name)
    
    def get_isolation_script(self) -> str:
        """Get JavaScript for cookie isolation."""
        blocked = list(self._blocked_cookies)
        return f'''
(function() {{
    const blocked = {blocked};
    const origCookie = Object.getOwnPropertyDescriptor(Document.prototype, "cookie");
    
    Object.defineProperty(document, "cookie", {{
        get: function() {{
            return origCookie.get.call(this);
        }},
        set: function(val) {{
            const name = val.split("=")[0].trim();
            if (blocked.includes(name)) return;
            origCookie.set.call(this, val);
        }}
    }});
}})();
'''
    
    def apply_to_page(self, page: Any) -> None:
        try:
            page.add_init_script(self.get_isolation_script())
        except Exception as e:
            logger.warning(f"Failed to apply cookie isolation: {e}")
    
    async def apply_to_page_async(self, page: Any) -> None:
        try:
            await page.add_init_script(self.get_isolation_script())
        except Exception as e:
            logger.warning(f"Failed to apply cookie isolation: {e}")
