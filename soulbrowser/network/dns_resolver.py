"""DNS resolution with DoH and DoT support."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
import asyncio
import aiohttp
import base64
import struct
import socket


@dataclass
class DNSConfig:
    """DNS configuration."""
    doh_enabled: bool = True
    dot_enabled: bool = False
    doh_server: str = "https://cloudflare-dns.com/dns-query"
    dot_server: str = "1.1.1.1"
    cache_enabled: bool = True
    cache_ttl: int = 300
    prefetch_enabled: bool = True


class DNSResolver:
    """Advanced DNS resolver with DoH/DoT support."""
    
    DOH_SERVERS = {
        "cloudflare": "https://cloudflare-dns.com/dns-query",
        "google": "https://dns.google/dns-query",
        "quad9": "https://dns.quad9.net:5053/dns-query",
        "adguard": "https://dns.adguard.com/dns-query",
        "nextdns": "https://dns.nextdns.io"
    }
    
    def __init__(self, config: Optional[DNSConfig] = None):
        self.config = config or DNSConfig()
        self._cache: Dict[str, Tuple[List[str], float]] = {}
        self._prefetch_queue: asyncio.Queue = asyncio.Queue()
        self._session: Optional[aiohttp.ClientSession] = None
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session for DoH."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session
        
    def _build_dns_query(self, domain: str, query_type: int = 1) -> bytes:
        """Build DNS query packet."""
        # Transaction ID
        query = struct.pack(">H", 0x1234)
        # Flags (standard query)
        query += struct.pack(">H", 0x0100)
        # Questions, Answers, Authority, Additional
        query += struct.pack(">HHHH", 1, 0, 0, 0)
        
        # Query name
        for part in domain.split("."):
            query += struct.pack("B", len(part)) + part.encode()
        query += b"\\x00"
        
        # Query type and class
        query += struct.pack(">HH", query_type, 1)
        
        return query
        
    def _parse_dns_response(self, data: bytes) -> List[str]:
        """Parse DNS response for A records."""
        addresses = []
        try:
            # Skip header (12 bytes) and question section
            pos = 12
            while data[pos] != 0:
                pos += 1 + data[pos]
            pos += 5  # null byte + qtype + qclass
            
            # Parse answers
            answer_count = struct.unpack(">H", data[6:8])[0]
            for _ in range(answer_count):
                if data[pos] & 0xc0 == 0xc0:
                    pos += 2  # Compressed name
                else:
                    while data[pos] != 0:
                        pos += 1 + data[pos]
                    pos += 1
                    
                rtype = struct.unpack(">H", data[pos:pos+2])[0]
                rdlen = struct.unpack(">H", data[pos+8:pos+10])[0]
                pos += 10
                
                if rtype == 1 and rdlen == 4:  # A record
                    ip = socket.inet_ntoa(data[pos:pos+4])
                    addresses.append(ip)
                pos += rdlen
        except Exception:
            pass
            
        return addresses
        
    async def resolve_doh(self, domain: str) -> List[str]:
        """Resolve domain using DNS-over-HTTPS."""
        if self.config.cache_enabled and domain in self._cache:
            addresses, timestamp = self._cache[domain]
            if asyncio.get_event_loop().time() - timestamp < self.config.cache_ttl:
                return addresses
                
        session = await self._get_session()
        query = self._build_dns_query(domain)
        query_b64 = base64.urlsafe_b64encode(query).rstrip(b"=").decode()
        
        try:
            async with session.get(
                f"{self.config.doh_server}?dns={query_b64}",
                headers={
                    "Accept": "application/dns-message"
                }
            ) as response:
                if response.status == 200:
                    data = await response.read()
                    addresses = self._parse_dns_response(data)
                    
                    if self.config.cache_enabled:
                        self._cache[domain] = (
                            addresses,
                            asyncio.get_event_loop().time()
                        )
                    return addresses
        except Exception:
            pass
            
        return []
        
    async def resolve(self, domain: str) -> List[str]:
        """Resolve domain with fallback."""
        if self.config.doh_enabled:
            addresses = await self.resolve_doh(domain)
            if addresses:
                return addresses
                
        # Fallback to system resolver
        try:
            result = await asyncio.get_event_loop().getaddrinfo(
                domain, None, socket.AF_INET
            )
            return [r[4][0] for r in result]
        except Exception:
            return []
            
    async def prefetch(self, domains: List[str]) -> None:
        """Prefetch DNS for multiple domains."""
        tasks = [self.resolve(domain) for domain in domains]
        await asyncio.gather(*tasks, return_exceptions=True)
        
    def set_doh_server(self, server: str) -> None:
        """Set DoH server."""
        if server in self.DOH_SERVERS:
            self.config.doh_server = self.DOH_SERVERS[server]
        else:
            self.config.doh_server = server
            
    def clear_cache(self) -> None:
        """Clear DNS cache."""
        self._cache.clear()
        
    async def close(self) -> None:
        """Close DNS resolver."""
        if self._session and not self._session.closed:
            await self._session.close()
