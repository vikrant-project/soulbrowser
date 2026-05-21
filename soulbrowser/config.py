"""Soul Browser - Stealth configuration and platform detection.

Enhanced configuration with advanced privacy controls and performance optimization.
"""

from __future__ import annotations

import os
import platform
import random
import json
from pathlib import Path
from enum import Enum, auto
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

from ._version import __version__, SOUL_BROWSER_VERSION

# ---------------------------------------------------------------------------
# Soul Browser Version Information
# ---------------------------------------------------------------------------
SOUL_BROWSER_VERSION = "1.0.0"
SOUL_BROWSER_CODENAME = "Phoenix"

# Chromium version shipped with this release
CHROMIUM_VERSION = "146.0.7680.177.5"

PLATFORM_CHROMIUM_VERSIONS: Dict[str, str] = {
    "linux-x64": "146.0.7680.177.5",
    "linux-arm64": "146.0.7680.177.3",
    "darwin-arm64": "145.0.7632.109.2",
    "darwin-x64": "145.0.7632.109.2",
    "windows-x64": "146.0.7680.177.5",
}

# ---------------------------------------------------------------------------
# Privacy Levels
# ---------------------------------------------------------------------------
class PrivacyLevel(Enum):
    """Privacy protection levels for Soul Browser."""
    MINIMAL = auto()      # Basic protection, maximum compatibility
    STANDARD = auto()     # Balanced protection (default)
    STRICT = auto()       # Enhanced protection
    PARANOID = auto()     # Maximum protection, may break some sites

_current_privacy_level = PrivacyLevel.STANDARD

def get_privacy_level() -> PrivacyLevel:
    """Get the current privacy level."""
    return _current_privacy_level

def set_privacy_level(level: PrivacyLevel) -> None:
    """Set the privacy level."""
    global _current_privacy_level
    _current_privacy_level = level

# ---------------------------------------------------------------------------
# Privacy Configuration Presets
# ---------------------------------------------------------------------------
@dataclass
class PrivacyConfig:
    """Privacy configuration settings."""
    # Fingerprint protection
    canvas_protection: bool = True
    webgl_protection: bool = True
    audio_protection: bool = True
    font_protection: bool = True
    gpu_protection: bool = True
    screen_protection: bool = True
    battery_api_blocked: bool = True
    sensor_api_blocked: bool = True
    
    # Network protection
    webrtc_protection: bool = True
    dns_over_https: bool = True
    https_only: bool = True
    mixed_content_blocked: bool = True
    referrer_policy: str = "strict-origin-when-cross-origin"
    
    # Tracking protection
    tracking_protection: bool = True
    ml_tracking_detection: bool = True
    cookie_isolation: bool = True
    first_party_isolation: bool = True
    cross_origin_isolation: bool = True
    
    # Ad blocking
    ad_blocking: bool = True
    cosmetic_filtering: bool = True
    third_party_blocking: bool = True
    social_media_blocking: bool = True
    
    # User agent
    user_agent_randomization: bool = True
    timezone_spoofing: bool = True
    language_masking: bool = True
    hardware_randomization: bool = True

PRIVACY_PRESETS: Dict[PrivacyLevel, PrivacyConfig] = {
    PrivacyLevel.MINIMAL: PrivacyConfig(
        canvas_protection=False,
        webgl_protection=False,
        audio_protection=False,
        font_protection=False,
        battery_api_blocked=False,
        sensor_api_blocked=False,
        ml_tracking_detection=False,
        cookie_isolation=False,
        first_party_isolation=False,
        cross_origin_isolation=False,
        ad_blocking=False,
        cosmetic_filtering=False,
        third_party_blocking=False,
        social_media_blocking=False,
        user_agent_randomization=False,
        timezone_spoofing=False,
        language_masking=False,
        hardware_randomization=False,
    ),
    PrivacyLevel.STANDARD: PrivacyConfig(),
    PrivacyLevel.STRICT: PrivacyConfig(
        referrer_policy="no-referrer",
        ml_tracking_detection=True,
    ),
    PrivacyLevel.PARANOID: PrivacyConfig(
        referrer_policy="no-referrer",
        ml_tracking_detection=True,
        battery_api_blocked=True,
        sensor_api_blocked=True,
    ),
}

def get_privacy_config(level: Optional[PrivacyLevel] = None) -> PrivacyConfig:
    """Get privacy configuration for the specified level."""
    return PRIVACY_PRESETS.get(level or get_privacy_level(), PrivacyConfig())

# ---------------------------------------------------------------------------
# Performance Configuration
# ---------------------------------------------------------------------------
@dataclass
class PerformanceConfig:
    """Performance optimization settings."""
    # Rendering
    gpu_acceleration: bool = True
    hardware_video_decode: bool = True
    smooth_scrolling: bool = True
    
    # Memory
    lazy_loading: bool = True
    memory_optimization: bool = True
    tab_hibernation: bool = True
    
    # Network
    prefetch_enabled: bool = True
    preconnect_enabled: bool = True
    http3_enabled: bool = True
    brotli_compression: bool = True
    
    # Caching
    aggressive_caching: bool = True
    service_worker_caching: bool = True
    
    # Threading
    multi_threaded_rendering: bool = True
    worker_threads: int = 4

# ---------------------------------------------------------------------------
# Playwright default args to suppress
# ---------------------------------------------------------------------------
IGNORE_DEFAULT_ARGS = ["--enable-automation", "--enable-unsafe-swiftshader"]

# ---------------------------------------------------------------------------
# Default stealth arguments
# ---------------------------------------------------------------------------
def get_default_stealth_args(privacy_level: Optional[PrivacyLevel] = None) -> List[str]:
    """Build stealth args with enhanced privacy protection.

    Args:
        privacy_level: Optional privacy level override.

    Returns:
        List of command-line arguments for the browser.
    """
    seed = random.randint(10000, 99999)
    system = platform.system()
    level = privacy_level or get_privacy_level()
    config = get_privacy_config(level)

    base = [
        "--no-sandbox",
        f"--fingerprint={seed}",
        "--disable-blink-features=AutomationControlled",
        "--disable-infobars",
        "--disable-dev-shm-usage",
        "--disable-background-networking",
        "--disable-default-apps",
        "--disable-extensions-except=[]",
        "--disable-sync",
        "--disable-translate",
        "--metrics-recording-only",
        "--mute-audio",
        "--no-first-run",
        "--safebrowsing-disable-auto-update",
    ]

    # Privacy-level specific args
    if level in (PrivacyLevel.STRICT, PrivacyLevel.PARANOID):
        base.extend([
            "--disable-client-side-phishing-detection",
            "--disable-component-update",
            "--disable-domain-reliability",
            "--disable-features=AudioServiceOutOfProcess",
            "--disable-hang-monitor",
            "--disable-ipc-flooding-protection",
            "--disable-renderer-backgrounding",
            "--force-color-profile=srgb",
        ])

    if level == PrivacyLevel.PARANOID:
        base.extend([
            "--disable-reading-from-canvas",
            "--disable-webgl",
            "--disable-3d-apis",
            "--disable-accelerated-2d-canvas",
            "--disable-gpu-compositing",
        ])

    # DNS-over-HTTPS
    if config.dns_over_https:
        base.append("--enable-features=DnsOverHttps")
        base.append("--dns-over-https-mode=secure")

    # HTTPS-only mode
    if config.https_only:
        base.append("--enable-features=HttpsOnlyMode")

    # Platform-specific args
    if system == "Darwin":
        return base + ["--fingerprint-platform=macos"]

    return base + ["--fingerprint-platform=windows"]

# ---------------------------------------------------------------------------
# Advanced stealth arguments
# ---------------------------------------------------------------------------
def get_advanced_stealth_args() -> List[str]:
    """Get additional stealth arguments for maximum protection."""
    return [
        # WebRTC protection
        "--disable-webrtc-hw-decoding",
        "--disable-webrtc-hw-encoding",
        "--disable-webrtc-multiple-routes",
        "--disable-webrtc-hw-vp8-encoding",
        "--enforce-webrtc-ip-permission-check",
        # GPU fingerprint protection
        "--disable-gpu-shader-disk-cache",
        "--disable-gpu-program-cache",
        # Network protection
        "--disable-quic",
        "--host-resolver-rules=MAP * ~NOTFOUND , EXCLUDE localhost",
        # Memory and performance
        "--memory-pressure-off",
        "--renderer-process-limit=4",
        # Additional protection
        "--disable-features=WebRtcHideLocalIpsWithMdns",
        "--disable-features=IsolateOrigins,site-per-process",
    ]

# ---------------------------------------------------------------------------
# Default viewport
# ---------------------------------------------------------------------------
DEFAULT_VIEWPORT = {"width": 1920, "height": 947}

# Common viewport presets
VIEWPORT_PRESETS = {
    "desktop_1080p": {"width": 1920, "height": 1080},
    "desktop_1440p": {"width": 2560, "height": 1440},
    "desktop_4k": {"width": 3840, "height": 2160},
    "laptop_13": {"width": 1280, "height": 800},
    "laptop_15": {"width": 1440, "height": 900},
    "ipad": {"width": 1024, "height": 768},
    "ipad_pro": {"width": 1366, "height": 1024},
    "iphone_12": {"width": 390, "height": 844},
    "iphone_14_pro": {"width": 393, "height": 852},
    "android_phone": {"width": 360, "height": 800},
    "android_tablet": {"width": 800, "height": 1280},
}

# ---------------------------------------------------------------------------
# Platform detection
# ---------------------------------------------------------------------------
SUPPORTED_PLATFORMS: Dict[tuple, str] = {
    ("Linux", "x86_64"): "linux-x64",
    ("Linux", "aarch64"): "linux-arm64",
    ("Darwin", "arm64"): "darwin-arm64",
    ("Darwin", "x86_64"): "darwin-x64",
    ("Windows", "AMD64"): "windows-x64",
    ("Windows", "x86_64"): "windows-x64",
}

AVAILABLE_PLATFORMS: set = set(PLATFORM_CHROMIUM_VERSIONS.keys())


def get_chromium_version() -> str:
    """Return the Chromium version for the current platform."""
    tag = get_platform_tag()
    return PLATFORM_CHROMIUM_VERSIONS.get(tag, CHROMIUM_VERSION)


def get_platform_tag() -> str:
    """Return the platform tag for binary download."""
    system = platform.system()
    machine = platform.machine()
    tag = SUPPORTED_PLATFORMS.get((system, machine))
    if tag is None:
        raise RuntimeError(
            f"Unsupported platform: {system} {machine}. "
            "Supported: " + ", ".join(f"{s}-{m}" for (s, m) in SUPPORTED_PLATFORMS)
        )
    return tag


# ---------------------------------------------------------------------------
# Binary cache paths
# ---------------------------------------------------------------------------
def get_cache_dir() -> Path:
    """Return the cache directory for downloaded binaries."""
    custom = os.environ.get("SOULBROWSER_CACHE_DIR") or os.environ.get("CLOAKBROWSER_CACHE_DIR")
    if custom:
        return Path(custom)
    return Path.home() / ".soulbrowser"


def get_binary_dir(version: Optional[str] = None) -> Path:
    """Return the directory for a Chromium version binary."""
    v = version or get_chromium_version()
    return get_cache_dir() / f"chromium-{v}"


def get_binary_path(version: Optional[str] = None) -> Path:
    """Return the expected path to the chrome executable."""
    binary_dir = get_binary_dir(version)

    if platform.system() == "Darwin":
        return binary_dir / "Chromium.app" / "Contents" / "MacOS" / "Chromium"
    elif platform.system() == "Windows":
        return binary_dir / "chrome.exe"
    else:
        return binary_dir / "chrome"


def check_platform_available() -> None:
    """Raise a clear error if no pre-built binary exists for this platform."""
    if get_local_binary_override():
        return

    tag = get_platform_tag()
    if tag not in AVAILABLE_PLATFORMS:
        available = ", ".join(sorted(AVAILABLE_PLATFORMS))
        import sys
        sys.exit(
            f"\n\033[1mSoul Browser\033[0m — Pre-built binaries are available for: {available}.\n\n"
            f"To use Soul Browser now, set SOULBROWSER_BINARY_PATH to a local Chromium binary."
        )


def get_effective_version() -> str:
    """Return the best available version."""
    base = get_chromium_version()
    cache = get_cache_dir()
    for name in (f"latest_version_{get_platform_tag()}", "latest_version"):
        marker = cache / name
        if marker.exists():
            try:
                version = marker.read_text().strip()
                if version and _version_newer(version, base):
                    binary = get_binary_path(version)
                    if binary.exists():
                        return version
            except (ValueError, OSError):
                pass
    return base


def _version_tuple(v: str) -> tuple:
    """Parse version string into tuple for comparison."""
    return tuple(int(x) for x in v.split("."))


def _version_newer(a: str, b: str) -> bool:
    """Return True if version a is strictly newer than version b."""
    return _version_tuple(a) > _version_tuple(b)


# ---------------------------------------------------------------------------
# Download URL
# ---------------------------------------------------------------------------
DOWNLOAD_BASE_URL = os.environ.get(
    "SOULBROWSER_DOWNLOAD_URL",
    os.environ.get("CLOAKBROWSER_DOWNLOAD_URL", "https://cloakbrowser.dev"),
)

GITHUB_API_URL = "https://api.github.com/repos/CloakHQ/cloakbrowser/releases"

GITHUB_DOWNLOAD_BASE_URL = (
    "https://github.com/CloakHQ/cloakbrowser/releases/download"
)


def get_archive_ext() -> str:
    """Return the archive extension for the current platform."""
    return ".zip" if platform.system() == "Windows" else ".tar.gz"


def get_archive_name(tag: Optional[str] = None) -> str:
    """Return the archive filename for a platform tag."""
    t = tag or get_platform_tag()
    return f"cloakbrowser-{t}{get_archive_ext()}"


def get_download_url(version: Optional[str] = None) -> str:
    """Return the full download URL for the current platform binary archive."""
    v = version or get_chromium_version()
    return f"{DOWNLOAD_BASE_URL}/chromium-v{v}/{get_archive_name()}"


def get_fallback_download_url(version: Optional[str] = None) -> str:
    """Return the GitHub Releases fallback URL for the binary archive."""
    v = version or get_chromium_version()
    return f"{GITHUB_DOWNLOAD_BASE_URL}/chromium-v{v}/{get_archive_name()}"


def get_local_binary_override() -> Optional[str]:
    """Check if user has set a local binary path via env var."""
    return os.environ.get("SOULBROWSER_BINARY_PATH") or os.environ.get("CLOAKBROWSER_BINARY_PATH")


# ---------------------------------------------------------------------------
# User Agent Management
# ---------------------------------------------------------------------------
USER_AGENTS = {
    "chrome_windows": [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    ],
    "chrome_mac": [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    ],
    "chrome_linux": [
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    ],
    "firefox_windows": [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    ],
    "safari_mac": [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    ],
}

def get_random_user_agent(browser_type: Optional[str] = None) -> str:
    """Get a random user agent string."""
    if browser_type and browser_type in USER_AGENTS:
        return random.choice(USER_AGENTS[browser_type])
    
    system = platform.system()
    if system == "Darwin":
        return random.choice(USER_AGENTS["chrome_mac"])
    elif system == "Windows":
        return random.choice(USER_AGENTS["chrome_windows"])
    else:
        return random.choice(USER_AGENTS["chrome_linux"])


# ---------------------------------------------------------------------------
# Extension Configuration
# ---------------------------------------------------------------------------
@dataclass
class ExtensionConfig:
    """Configuration for browser extensions."""
    ad_blocker: bool = True
    tracker_blocker: bool = True
    password_manager: bool = False
    dark_mode: bool = False
    vpn: bool = False
    custom_extensions: List[str] = field(default_factory=list)
