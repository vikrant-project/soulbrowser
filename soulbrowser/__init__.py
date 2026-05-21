"""Soul Browser — The Ultimate Privacy-First Stealth Browser.

100x more powerful than standard browsers with enterprise-grade features.
Advanced fingerprint protection, ML-based tracking detection, and extensive privacy controls.

Usage:
    from soulbrowser import launch

    browser = launch()
    page = browser.new_page()
    page.goto("https://protected-site.com")
    browser.close()
"""

from .browser import (
    launch, 
    launch_async, 
    launch_context, 
    launch_context_async, 
    launch_persistent_context, 
    launch_persistent_context_async, 
    ProxySettings, 
    build_args, 
    maybe_resolve_geoip
)
from .config import (
    CHROMIUM_VERSION, 
    SOUL_BROWSER_VERSION,
    get_default_stealth_args,
    get_privacy_level,
    set_privacy_level,
    PrivacyLevel,
    PrivacyConfig,
    get_privacy_config,
)
from .download import (
    binary_info, 
    check_for_update, 
    clear_cache, 
    ensure_binary
)
from ._version import __version__

# Human-like behavioral layer (optional)
def __getattr__(name):
    if name == "HumanConfig":
        from .human.config import HumanConfig
        globals()["HumanConfig"] = HumanConfig
        return HumanConfig
    if name == "resolve_human_config":
        from .human.config import resolve_config
        globals()["resolve_human_config"] = resolve_config
        return resolve_config
    # Privacy modules
    if name == "PrivacyManager":
        from .privacy.manager import PrivacyManager
        globals()["PrivacyManager"] = PrivacyManager
        return PrivacyManager
    if name == "FingerprintProtection":
        from .privacy.fingerprint import FingerprintProtection
        globals()["FingerprintProtection"] = FingerprintProtection
        return FingerprintProtection
    if name == "TrackingProtection":
        from .privacy.tracking import TrackingProtection
        globals()["TrackingProtection"] = TrackingProtection
        return TrackingProtection
    if name == "AdBlocker":
        from .adblock.blocker import AdBlocker
        globals()["AdBlocker"] = AdBlocker
        return AdBlocker
    if name == "PerformanceOptimizer":
        from .performance.optimizer import PerformanceOptimizer
        globals()["PerformanceOptimizer"] = PerformanceOptimizer
        return PerformanceOptimizer
    if name == "SecurityManager":
        from .security.manager import SecurityManager
        globals()["SecurityManager"] = SecurityManager
        return SecurityManager
    raise AttributeError(f"module 'soulbrowser' has no attribute {name}")

__all__ = [
    # Core browser functions
    "launch",
    "launch_async",
    "launch_context",
    "launch_context_async",
    "launch_persistent_context",
    "launch_persistent_context_async",
    "ensure_binary",
    "clear_cache",
    "binary_info",
    "check_for_update",
    "CHROMIUM_VERSION",
    "SOUL_BROWSER_VERSION",
    "get_default_stealth_args",
    "build_args",
    "maybe_resolve_geoip",
    "ProxySettings",
    "HumanConfig",
    "resolve_human_config",
    "__version__",
    # Privacy
    "PrivacyLevel",
    "PrivacyConfig",
    "get_privacy_level",
    "set_privacy_level",
    "get_privacy_config",
    "PrivacyManager",
    "FingerprintProtection",
    "TrackingProtection",
    # Ad blocking
    "AdBlocker",
    # Performance
    "PerformanceOptimizer",
    # Security
    "SecurityManager",
]
