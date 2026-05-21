"""Proxy management with per-tab and per-domain support."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import asyncio


class ProxyType(Enum):
    HTTP = "http"
    HTTPS = "https"
    SOCKS4 = "socks4"
    SOCKS5 = "socks5"
    TOR = "tor"
    I2P = "i2p"


@dataclass
class ProxyConfig:
    """Proxy configuration."""
    type: ProxyType = ProxyType.HTTP
    host: str = ""
    port: int = 0
    username: Optional[str] = None
    password: Optional[str] = None
    bypass_list: List[str] = field(default_factory=list)
    

class ProxyManager:
    """Advanced proxy management for Soul Browser."""
    
    def __init__(self):
        self._global_proxy: Optional[ProxyConfig] = None
        self._tab_proxies: Dict[str, ProxyConfig] = {}
        self._domain_proxies: Dict[str, ProxyConfig] = {}
        self._proxy_chains: List[ProxyConfig] = []
        
    def set_global_proxy(self, config: ProxyConfig) -> None:
        """Set global proxy for all connections."""
        self._global_proxy = config
        
    def set_tab_proxy(self, tab_id: str, config: ProxyConfig) -> None:
        """Set proxy for specific tab."""
        self._tab_proxies[tab_id] = config
        
    def set_domain_proxy(self, domain: str, config: ProxyConfig) -> None:
        """Set proxy for specific domain."""
        self._domain_proxies[domain] = config
        
    def set_proxy_chain(self, proxies: List[ProxyConfig]) -> None:
        """Set proxy chain for multi-hop routing."""
        self._proxy_chains = proxies
        
    def get_proxy_for_request(
        self,
        url: str,
        tab_id: Optional[str] = None
    ) -> Optional[ProxyConfig]:
        """Get appropriate proxy for request."""
        from urllib.parse import urlparse
        domain = urlparse(url).netloc
        
        # Check tab-specific proxy first
        if tab_id and tab_id in self._tab_proxies:
            return self._tab_proxies[tab_id]
            
        # Check domain-specific proxy
        for pattern, proxy in self._domain_proxies.items():
            if domain.endswith(pattern) or domain == pattern:
                return proxy
                
        # Fall back to global proxy
        return self._global_proxy
        
    def get_proxy_url(self, config: ProxyConfig) -> str:
        """Get proxy URL string."""
        auth = ""
        if config.username and config.password:
            auth = f"{config.username}:{config.password}@"
        return f"{config.type.value}://{auth}{config.host}:{config.port}"
        
    def remove_tab_proxy(self, tab_id: str) -> None:
        """Remove proxy for specific tab."""
        self._tab_proxies.pop(tab_id, None)
        
    def clear_all_proxies(self) -> None:
        """Clear all proxy configurations."""
        self._global_proxy = None
        self._tab_proxies.clear()
        self._domain_proxies.clear()
        self._proxy_chains.clear()


class TorManager:
    """Tor network integration."""
    
    def __init__(self, control_port: int = 9051, socks_port: int = 9050):
        self.control_port = control_port
        self.socks_port = socks_port
        self._connected = False
        
    async def connect(self) -> bool:
        """Connect to Tor network."""
        try:
            # Attempt connection to Tor control port
            reader, writer = await asyncio.open_connection(
                "127.0.0.1", self.control_port
            )
            writer.write(b"AUTHENTICATE\r\n")
            await writer.drain()
            response = await reader.read(100)
            self._connected = b"250 OK" in response
            writer.close()
            await writer.wait_closed()
            return self._connected
        except Exception:
            return False
            
    async def new_identity(self) -> bool:
        """Request new Tor identity (new circuit)."""
        if not self._connected:
            return False
        try:
            reader, writer = await asyncio.open_connection(
                "127.0.0.1", self.control_port
            )
            writer.write(b"AUTHENTICATE\r\nSIGNAL NEWNYM\r\n")
            await writer.drain()
            response = await reader.read(100)
            writer.close()
            await writer.wait_closed()
            return b"250 OK" in response
        except Exception:
            return False
            
    def get_proxy_config(self) -> ProxyConfig:
        """Get Tor proxy configuration."""
        return ProxyConfig(
            type=ProxyType.SOCKS5,
            host="127.0.0.1",
            port=self.socks_port
        )
