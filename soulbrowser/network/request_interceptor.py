"""Network request interception and modification."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Awaitable
from enum import Enum
import re
import asyncio


class InterceptAction(Enum):
    ALLOW = "allow"
    BLOCK = "block"
    MODIFY = "modify"
    REDIRECT = "redirect"


@dataclass
class InterceptRule:
    """Request interception rule."""
    pattern: str
    action: InterceptAction
    resource_types: List[str] = field(default_factory=list)
    modify_headers: Optional[Dict[str, str]] = None
    redirect_url: Optional[str] = None
    priority: int = 0


class RequestInterceptor:
    """Network request interceptor for Soul Browser."""
    
    def __init__(self):
        self._rules: List[InterceptRule] = []
        self._handlers: List[Callable[[Dict], Awaitable[Dict]]] = []
        self._blocked_count: int = 0
        self._modified_count: int = 0
        
    def add_rule(self, rule: InterceptRule) -> None:
        """Add interception rule."""
        self._rules.append(rule)
        self._rules.sort(key=lambda r: -r.priority)
        
    def remove_rule(self, pattern: str) -> bool:
        """Remove rule by pattern."""
        original_len = len(self._rules)
        self._rules = [r for r in self._rules if r.pattern != pattern]
        return len(self._rules) < original_len
        
    def add_handler(
        self,
        handler: Callable[[Dict], Awaitable[Dict]]
    ) -> None:
        """Add custom request handler."""
        self._handlers.append(handler)
        
    def match_rule(
        self,
        url: str,
        resource_type: str
    ) -> Optional[InterceptRule]:
        """Find matching rule for request."""
        for rule in self._rules:
            if rule.resource_types and resource_type not in rule.resource_types:
                continue
            try:
                if re.search(rule.pattern, url):
                    return rule
            except re.error:
                if rule.pattern in url:
                    return rule
        return None
        
    async def intercept(self, request: Dict) -> Dict:
        """Process request through interception rules."""
        url = request.get("url", "")
        resource_type = request.get("resourceType", "other")
        
        rule = self.match_rule(url, resource_type)
        
        if rule:
            if rule.action == InterceptAction.BLOCK:
                self._blocked_count += 1
                return {"action": "block"}
                
            elif rule.action == InterceptAction.REDIRECT and rule.redirect_url:
                self._modified_count += 1
                return {"action": "redirect", "url": rule.redirect_url}
                
            elif rule.action == InterceptAction.MODIFY:
                self._modified_count += 1
                result = dict(request)
                if rule.modify_headers:
                    result.setdefault("headers", {}).update(rule.modify_headers)
                return {"action": "continue", "request": result}
                
        # Run custom handlers
        for handler in self._handlers:
            try:
                result = await handler(request)
                if result.get("action") != "continue":
                    return result
            except Exception:
                pass
                
        return {"action": "continue"}
        
    def get_stats(self) -> Dict[str, int]:
        """Get interception statistics."""
        return {
            "blocked": self._blocked_count,
            "modified": self._modified_count,
            "rules_count": len(self._rules)
        }
        
    def clear_rules(self) -> None:
        """Clear all interception rules."""
        self._rules.clear()
        
    def clear_stats(self) -> None:
        """Reset statistics."""
        self._blocked_count = 0
        self._modified_count = 0


# Pre-built blocking rules
TRACKING_RULES = [
    InterceptRule(
        pattern=r"google-analytics\\.com",
        action=InterceptAction.BLOCK,
        priority=100
    ),
    InterceptRule(
        pattern=r"googletagmanager\\.com",
        action=InterceptAction.BLOCK,
        priority=100
    ),
    InterceptRule(
        pattern=r"facebook\\.com/(tr|pixel)",
        action=InterceptAction.BLOCK,
        priority=100
    ),
    InterceptRule(
        pattern=r"doubleclick\\.net",
        action=InterceptAction.BLOCK,
        priority=100
    ),
    InterceptRule(
        pattern=r"analytics\\.",
        action=InterceptAction.BLOCK,
        priority=50
    ),
]

AD_RULES = [
    InterceptRule(
        pattern=r"googlesyndication\\.com",
        action=InterceptAction.BLOCK,
        resource_types=["script", "image", "iframe"],
        priority=100
    ),
    InterceptRule(
        pattern=r"ads\\.",
        action=InterceptAction.BLOCK,
        priority=50
    ),
    InterceptRule(
        pattern=r"/ads/",
        action=InterceptAction.BLOCK,
        priority=50
    ),
]
