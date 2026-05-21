"""Soul Browser DNS Protection Module."""

from __future__ import annotations
import logging
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger("soulbrowser.dns")

# Popular DoH providers
DOH_PROVIDERS: Dict[str, str] = {
    "cloudflare": "https://cloudflare-dns.com/dns-query",
    "google": "https://dns.google/dns-query",
    "quad9": "https://dns.quad9.net/dns-query",
    "adguard": "https://dns.adguard.com/dns-query",
    "cleanbrowsing": "https://doh.cleanbrowsing.org/doh/security-filter/",
    "nextdns": "https://dns.nextdns.io/",
}


@dataclass
class DNSConfig:
    """DNS configuration."""
    doh_enabled: bool = True
    doh_provider: str = "cloudflare"
    doh_url: Optional[str] = None
    fallback_enabled: bool = True
    cache_enabled: bool = True
    cache_ttl: int = 3600


class DNSProtection:
    """DNS encryption and protection for Soul Browser.
    
    Provides DNS-over-HTTPS (DoH) support and DNS leak prevention.
    """
    
    def __init__(self, config: Optional[DNSConfig] = None):
        self.config = config or DNSConfig()
        self._queries_encrypted = 0
    
    def get_doh_url(self) -> str:
        """Get the DoH endpoint URL."""
        if self.config.doh_url:
            return self.config.doh_url
        return DOH_PROVIDERS.get(self.config.doh_provider, DOH_PROVIDERS["cloudflare"])
    
    def get_chrome_args(self) -> List[str]:
        """Get Chrome command-line arguments for DNS protection."""
        args = []
        
        if self.config.doh_enabled:
            args.extend([
                "--enable-features=DnsOverHttps",
                f"--dns-over-https-mode=secure",
                f"--dns-over-https-templates={self.get_doh_url()}",
            ])
        
        return args
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            "queries_encrypted": self._queries_encrypted,
            "doh_provider": self.config.doh_provider,
            "doh_enabled": self.config.doh_enabled,
        }
