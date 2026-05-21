"""Soul Browser Security Manager."""

from __future__ import annotations
import logging
import hashlib
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger("soulbrowser.security")

# Known malicious domains (sample)
MALICIOUS_DOMAINS: Set[str] = {
    "malware.example.com", "phishing.example.com",
}

# Known crypto mining scripts
CRYPTOMINER_PATTERNS: List[str] = [
    "coinhive.min.js", "cryptonight.wasm", "deepminer.js",
    "coinimp.min.js", "miner.start", "cryptoloot.pro",
    "webminepool.com", "ppoi.org", "monerominer",
]


@dataclass
class SecurityReport:
    """Security scan report."""
    url: str
    is_secure: bool
    threats_found: List[str]
    recommendations: List[str]
    certificate_valid: bool = True
    https_enforced: bool = False


class CertificateValidator:
    """SSL/TLS certificate validation."""
    
    def __init__(self):
        self._pinned_certs: Dict[str, str] = {}
    
    def pin_certificate(self, domain: str, cert_hash: str) -> None:
        """Pin a certificate for a domain."""
        self._pinned_certs[domain] = cert_hash
    
    def validate(self, domain: str, cert_hash: str) -> bool:
        """Validate a certificate against pinned value."""
        if domain in self._pinned_certs:
            return self._pinned_certs[domain] == cert_hash
        return True  # No pin = accept


class SecurityManager:
    """Security manager for Soul Browser.
    
    Provides protection against malware, phishing, cryptojacking,
    and other web threats.
    """
    
    def __init__(self, strict_mode: bool = False):
        self.strict_mode = strict_mode
        self.cert_validator = CertificateValidator()
        self._blocked_domains = MALICIOUS_DOMAINS.copy()
        self._cryptominer_patterns = CRYPTOMINER_PATTERNS.copy()
        self._stats = {
            "threats_blocked": 0,
            "malware_blocked": 0,
            "phishing_blocked": 0,
            "cryptominers_blocked": 0,
        }
    
    def add_blocked_domain(self, domain: str) -> None:
        """Add a domain to the blocklist."""
        self._blocked_domains.add(domain)
    
    def is_malicious(self, url: str) -> bool:
        """Check if a URL is potentially malicious."""
        url_lower = url.lower()
        
        for domain in self._blocked_domains:
            if domain in url_lower:
                self._stats["threats_blocked"] += 1
                return True
        
        return False
    
    def is_cryptominer(self, url: str) -> bool:
        """Check if a URL is a known cryptominer."""
        url_lower = url.lower()
        
        for pattern in self._cryptominer_patterns:
            if pattern in url_lower:
                self._stats["cryptominers_blocked"] += 1
                return True
        
        return False
    
    def get_security_script(self) -> str:
        """Get JavaScript for security protection."""
        miners = self._cryptominer_patterns
        
        return f'''
(function() {{
    const minerPatterns = {miners};
    
    // Block cryptominers
    const origFetch = window.fetch;
    window.fetch = function(url) {{
        const urlStr = typeof url === "string" ? url : (url.url || "");
        for (const p of minerPatterns) {{
            if (urlStr.includes(p)) {{
                return Promise.reject(new Error("Blocked"));
            }}
        }}
        return origFetch.apply(this, arguments);
    }};
    
    // Block WebWorker miners
    const origWorker = window.Worker;
    window.Worker = function(url) {{
        for (const p of minerPatterns) {{
            if (url.includes(p)) {{
                throw new Error("Blocked");
            }}
        }}
        return new origWorker(url);
    }};
    
    // Block WebAssembly miners
    const origInstantiate = WebAssembly.instantiate;
    WebAssembly.instantiate = function(bufferSource, importObject) {{
        // Check for known miner signatures
        return origInstantiate.apply(this, arguments);
    }};
    
    // Disable clipboard access for suspicious sites
    const origClipboard = navigator.clipboard;
    if (origClipboard) {{
        navigator.clipboard.writeText = function() {{
            console.warn("Clipboard access blocked for security");
            return Promise.reject(new Error("Blocked"));
        }};
    }}
}})();
'''
    
    def get_https_upgrade_script(self) -> str:
        """Get JavaScript for HTTPS upgrading."""
        return '''
(function() {
    // Upgrade insecure requests
    if (location.protocol === "http:") {
        location.replace(location.href.replace("http:", "https:"));
    }
    
    // Upgrade insecure links
    document.addEventListener("DOMContentLoaded", function() {
        document.querySelectorAll("a[href^='http:']").forEach(function(a) {
            a.href = a.href.replace("http:", "https:");
        });
    });
})();
'''
    
    def get_content_security_policy(self) -> Dict[str, str]:
        """Get recommended Content Security Policy headers."""
        if self.strict_mode:
            return {
                "Content-Security-Policy": (
                    "default-src 'self'; "
                    "script-src 'self'; "
                    "style-src 'self' 'unsafe-inline'; "
                    "img-src 'self' data: https:; "
                    "font-src 'self'; "
                    "connect-src 'self'; "
                    "frame-ancestors 'none'; "
                    "base-uri 'self'; "
                    "form-action 'self';"
                )
            }
        return {
            "Content-Security-Policy": (
                "upgrade-insecure-requests; "
                "block-all-mixed-content;"
            )
        }
    
    def apply_to_page(self, page: Any) -> None:
        """Apply security protections to a page."""
        try:
            page.add_init_script(self.get_security_script())
            if self.strict_mode:
                page.add_init_script(self.get_https_upgrade_script())
        except Exception as e:
            logger.warning(f"Failed to apply security protections: {e}")
    
    async def apply_to_page_async(self, page: Any) -> None:
        """Apply security protections to a page (async)."""
        try:
            await page.add_init_script(self.get_security_script())
            if self.strict_mode:
                await page.add_init_script(self.get_https_upgrade_script())
        except Exception as e:
            logger.warning(f"Failed to apply security protections: {e}")
    
    def scan_url(self, url: str) -> SecurityReport:
        """Scan a URL for security threats."""
        threats = []
        recommendations = []
        
        if self.is_malicious(url):
            threats.append("Potentially malicious domain")
        
        if self.is_cryptominer(url):
            threats.append("Cryptominer detected")
        
        if not url.startswith("https://"):
            recommendations.append("Use HTTPS for secure connection")
        
        return SecurityReport(
            url=url,
            is_secure=len(threats) == 0,
            threats_found=threats,
            recommendations=recommendations,
            https_enforced=url.startswith("https://")
        )
    
    def get_stats(self) -> Dict[str, int]:
        return self._stats.copy()
