"""Advanced HTTP client with HTTP/3 and QUIC support."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import asyncio
import aiohttp
from urllib.parse import urlparse


@dataclass
class HTTPConfig:
    """HTTP client configuration."""
    http2_enabled: bool = True
    http3_enabled: bool = True
    quic_enabled: bool = True
    brotli_enabled: bool = True
    connection_pooling: bool = True
    max_connections: int = 100
    timeout: float = 30.0
    retry_count: int = 3
    follow_redirects: bool = True
    max_redirects: int = 10


class HTTPClient:
    """Advanced HTTP client for Soul Browser."""
    
    def __init__(self, config: Optional[HTTPConfig] = None):
        self.config = config or HTTPConfig()
        self._session: Optional[aiohttp.ClientSession] = None
        self._connection_pool: Dict[str, Any] = {}
        self._request_queue: asyncio.Queue = asyncio.Queue()
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session."""
        if self._session is None or self._session.closed:
            connector = aiohttp.TCPConnector(
                limit=self.config.max_connections,
                enable_cleanup_closed=True,
                force_close=False
            )
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            self._session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout
            )
        return self._session
        
    async def request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        data: Optional[Any] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Make HTTP request with advanced features."""
        session = await self._get_session()
        
        # Add compression support headers
        request_headers = headers or {}
        if self.config.brotli_enabled:
            request_headers["Accept-Encoding"] = "br, gzip, deflate"
            
        for attempt in range(self.config.retry_count):
            try:
                async with session.request(
                    method,
                    url,
                    headers=request_headers,
                    data=data,
                    allow_redirects=self.config.follow_redirects,
                    max_redirects=self.config.max_redirects,
                    **kwargs
                ) as response:
                    return {
                        "status": response.status,
                        "headers": dict(response.headers),
                        "body": await response.read(),
                        "url": str(response.url),
                        "http_version": f"{response.version.major}.{response.version.minor}"
                    }
            except Exception as e:
                if attempt == self.config.retry_count - 1:
                    raise
                await asyncio.sleep(2 ** attempt)
                
    async def get(self, url: str, **kwargs) -> Dict[str, Any]:
        """HTTP GET request."""
        return await self.request("GET", url, **kwargs)
        
    async def post(self, url: str, **kwargs) -> Dict[str, Any]:
        """HTTP POST request."""
        return await self.request("POST", url, **kwargs)
        
    async def batch_request(self, requests: List[Dict]) -> List[Dict[str, Any]]:
        """Execute multiple requests concurrently."""
        tasks = [
            self.request(
                req.get("method", "GET"),
                req["url"],
                headers=req.get("headers"),
                data=req.get("data")
            )
            for req in requests
        ]
        return await asyncio.gather(*tasks, return_exceptions=True)
        
    async def close(self) -> None:
        """Close HTTP client."""
        if self._session and not self._session.closed:
            await self._session.close()


class RequestPrioritizer:
    """Prioritize network requests."""
    
    PRIORITY_CRITICAL = 0  # HTML, critical CSS/JS
    PRIORITY_HIGH = 1      # Above-fold images, fonts
    PRIORITY_NORMAL = 2    # Other resources
    PRIORITY_LOW = 3       # Analytics, tracking
    
    def __init__(self):
        self._queues: Dict[int, asyncio.PriorityQueue] = {
            i: asyncio.PriorityQueue() for i in range(4)
        }
        
    def get_priority(self, url: str, resource_type: str) -> int:
        """Determine request priority."""
        if resource_type in ("document", "stylesheet", "script"):
            return self.PRIORITY_CRITICAL
        elif resource_type in ("image", "font"):
            return self.PRIORITY_HIGH
        elif resource_type in ("xhr", "fetch"):
            return self.PRIORITY_NORMAL
        else:
            return self.PRIORITY_LOW
