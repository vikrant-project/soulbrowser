"""Soul Browser Privacy Protection Modules.

Advanced privacy protection including fingerprint defense, tracking prevention,
and comprehensive isolation mechanisms.
"""

from .manager import PrivacyManager
from .fingerprint import FingerprintProtection
from .tracking import TrackingProtection
from .cookies import CookieIsolation
from .webrtc import WebRTCProtection
from .dns import DNSProtection

__all__ = [
    "PrivacyManager",
    "FingerprintProtection",
    "TrackingProtection",
    "CookieIsolation",
    "WebRTCProtection",
    "DNSProtection",
]
