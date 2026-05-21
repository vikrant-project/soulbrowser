"""
Soul Browser Network Module

Advanced networking features including HTTP/3, QUIC, proxy management.
"""

from .http_client import HTTPClient
from .proxy_manager import ProxyManager
from .dns_resolver import DNSResolver
from .request_interceptor import RequestInterceptor

__all__ = ["HTTPClient", "ProxyManager", "DNSResolver", "RequestInterceptor"]
