"""Soul Browser - Core browser launch functions.

Enhanced browser with advanced privacy, security, and performance features.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Literal, Optional, TypedDict
from urllib.parse import quote, unquote, urlparse, urlunparse

from .config import (
    DEFAULT_VIEWPORT,
    IGNORE_DEFAULT_ARGS,
    PrivacyLevel,
    get_default_stealth_args,
    get_privacy_config,
    get_advanced_stealth_args,
)
from .download import ensure_binary

logger = logging.getLogger("soulbrowser")

_VIEWPORT_UNSET = object()


def _resolve_timezone(timezone: str | None, kwargs: Dict[str, Any]) -> str | None:
    if "timezone_id" in kwargs:
        if timezone is None:
            timezone = kwargs.pop("timezone_id")
        else:
            kwargs.pop("timezone_id")
    return timezone


class _ProxySettingsRequired(TypedDict):
    server: str


class ProxySettings(_ProxySettingsRequired, total=False):
    bypass: str
    username: str
    password: str


def launch(
    headless: bool = True,
    proxy: str | ProxySettings | None = None,
    args: List[str] | None = None,
    stealth_args: bool = True,
    timezone: str | None = None,
    locale: str | None = None,
    geoip: bool = False,
    backend: str | None = None,
    humanize: bool = False,
    human_preset: str = "default",
    human_config: Dict[str, Any] | None = None,
    extension_paths: List[str] | None = None,
    privacy_level: PrivacyLevel = PrivacyLevel.STANDARD,
    ad_blocking: bool = True,
    tracking_protection: bool = True,
    performance_mode: bool = True,
    **kwargs: Any,
) -> Any:
    """Launch Soul Browser with enhanced privacy and security.

    Args:
        headless: Run in headless mode (default True).
        proxy: Proxy URL or settings dict.
        args: Additional Chromium CLI arguments.
        stealth_args: Include stealth fingerprint args (default True).
        timezone: IANA timezone (e.g. 'America/New_York').
        locale: BCP 47 locale (e.g. 'en-US').
        geoip: Auto-detect timezone/locale from proxy IP.
        backend: 'playwright' (default) or 'patchright'.
        humanize: Enable human-like behavior.
        human_preset: Humanize preset.
        human_config: Custom humanize config.
        extension_paths: Chrome extension paths.
        privacy_level: Privacy protection level.
        ad_blocking: Enable ad blocking (default True).
        tracking_protection: Enable tracking protection (default True).
        performance_mode: Enable performance optimizations (default True).
        **kwargs: Passed to playwright.chromium.launch().

    Returns:
        Playwright Browser object.
    """
    sync_playwright = _import_sync_playwright(_resolve_backend(backend))

    binary_path = ensure_binary()
    timezone, locale, exit_ip = maybe_resolve_geoip(geoip, proxy, timezone, locale)
    proxy_kwargs, proxy_extra_args = _resolve_proxy_config(proxy)
    args = _resolve_webrtc_args(args, proxy)
    
    if exit_ip and not (args and any(a.startswith("--fingerprint-webrtc-ip") for a in args)):
        args = list(args or [])
        args.append(f"--fingerprint-webrtc-ip={exit_ip}")

    chrome_args = build_args(
        stealth_args,
        (args or []) + proxy_extra_args,
        timezone=timezone,
        locale=locale,
        headless=headless,
        extension_paths=extension_paths,
        privacy_level=privacy_level,
        performance_mode=performance_mode,
    )

    logger.debug("Launching Soul Browser (headless=%s, privacy=%s)", headless, privacy_level.name)

    pw = sync_playwright().start()
    browser = pw.chromium.launch(
        executable_path=binary_path,
        headless=headless,
        args=chrome_args,
        ignore_default_args=IGNORE_DEFAULT_ARGS,
        **proxy_kwargs,
        **kwargs,
    )

    _original_close = browser.close

    def _close_with_cleanup() -> None:
        try:
            _original_close()
        finally:
            pw.stop()

    browser.close = _close_with_cleanup

    # Apply privacy and ad blocking
    browser._soul_config = {
        "privacy_level": privacy_level,
        "ad_blocking": ad_blocking,
        "tracking_protection": tracking_protection,
        "performance_mode": performance_mode,
    }

    if humanize:
        from .human import patch_browser
        from .human.config import resolve_config
        cfg = resolve_config(human_preset, human_config)
        patch_browser(browser, cfg)

    return browser


async def launch_async(
    headless: bool = True,
    proxy: str | ProxySettings | None = None,
    args: List[str] | None = None,
    stealth_args: bool = True,
    timezone: str | None = None,
    locale: str | None = None,
    geoip: bool = False,
    backend: str | None = None,
    humanize: bool = False,
    human_preset: str = "default",
    human_config: Dict[str, Any] | None = None,
    extension_paths: List[str] | None = None,
    privacy_level: PrivacyLevel = PrivacyLevel.STANDARD,
    ad_blocking: bool = True,
    tracking_protection: bool = True,
    performance_mode: bool = True,
    **kwargs: Any,
) -> Any:
    """Async version of launch()."""
    async_playwright = _import_async_playwright(_resolve_backend(backend))

    binary_path = ensure_binary()
    timezone, locale, exit_ip = maybe_resolve_geoip(geoip, proxy, timezone, locale)
    proxy_kwargs, proxy_extra_args = _resolve_proxy_config(proxy)
    args = _resolve_webrtc_args(args, proxy)
    
    if exit_ip and not (args and any(a.startswith("--fingerprint-webrtc-ip") for a in args)):
        args = list(args or [])
        args.append(f"--fingerprint-webrtc-ip={exit_ip}")

    chrome_args = build_args(
        stealth_args,
        (args or []) + proxy_extra_args,
        timezone=timezone,
        locale=locale,
        headless=headless,
        extension_paths=extension_paths,
        privacy_level=privacy_level,
        performance_mode=performance_mode,
    )

    logger.debug("Launching Soul Browser async (headless=%s)", headless)

    pw = await async_playwright().start()
    browser = await pw.chromium.launch(
        executable_path=binary_path,
        headless=headless,
        args=chrome_args,
        ignore_default_args=IGNORE_DEFAULT_ARGS,
        **proxy_kwargs,
        **kwargs,
    )

    _original_close = browser.close

    async def _close_with_cleanup() -> None:
        try:
            await _original_close()
        finally:
            await pw.stop()

    browser.close = _close_with_cleanup

    browser._soul_config = {
        "privacy_level": privacy_level,
        "ad_blocking": ad_blocking,
        "tracking_protection": tracking_protection,
        "performance_mode": performance_mode,
    }

    if humanize:
        from .human import patch_browser_async
        from .human.config import resolve_config
        cfg = resolve_config(human_preset, human_config)
        patch_browser_async(browser, cfg)

    return browser


def launch_persistent_context(
    user_data_dir: str | os.PathLike,
    headless: bool = True,
    proxy: str | ProxySettings | None = None,
    args: List[str] | None = None,
    stealth_args: bool = True,
    user_agent: str | None = None,
    viewport: Dict | None = _VIEWPORT_UNSET,
    locale: str | None = None,
    timezone: str | None = None,
    color_scheme: Literal["light", "dark", "no-preference"] | None = None,
    geoip: bool = False,
    backend: str | None = None,
    humanize: bool = False,
    human_preset: str = "default",
    human_config: Dict[str, Any] | None = None,
    extension_paths: List[str] | None = None,
    privacy_level: PrivacyLevel = PrivacyLevel.STANDARD,
    **kwargs: Any,
) -> Any:
    """Launch Soul Browser with persistent profile."""
    sync_playwright = _import_sync_playwright(_resolve_backend(backend))
    timezone = _resolve_timezone(timezone, kwargs)

    binary_path = ensure_binary()
    timezone, locale, exit_ip = maybe_resolve_geoip(geoip, proxy, timezone, locale)
    proxy_kwargs, proxy_extra_args = _resolve_proxy_config(proxy)
    args = _resolve_webrtc_args(args, proxy)
    
    if exit_ip and not (args and any(a.startswith("--fingerprint-webrtc-ip") for a in args)):
        args = list(args or [])
        args.append(f"--fingerprint-webrtc-ip={exit_ip}")

    chrome_args = build_args(
        stealth_args,
        (args or []) + proxy_extra_args,
        timezone=timezone,
        locale=locale,
        headless=headless,
        extension_paths=extension_paths,
        privacy_level=privacy_level,
    )

    context_kwargs: Dict[str, Any] = {}
    if user_agent:
        context_kwargs["user_agent"] = user_agent
    if viewport is _VIEWPORT_UNSET:
        context_kwargs["viewport"] = DEFAULT_VIEWPORT
    elif viewport is None:
        context_kwargs["no_viewport"] = True
    else:
        context_kwargs["viewport"] = viewport
    if color_scheme:
        context_kwargs["color_scheme"] = color_scheme
    context_kwargs.update(kwargs)

    pw = sync_playwright().start()
    context = pw.chromium.launch_persistent_context(
        user_data_dir=os.fspath(user_data_dir),
        executable_path=binary_path,
        headless=headless,
        args=chrome_args,
        ignore_default_args=IGNORE_DEFAULT_ARGS,
        **proxy_kwargs,
        **context_kwargs,
    )

    _original_close = context.close

    def _close_with_cleanup() -> None:
        try:
            _original_close()
        finally:
            pw.stop()

    context.close = _close_with_cleanup

    if humanize:
        from .human import patch_context
        from .human.config import resolve_config
        cfg = resolve_config(human_preset, human_config)
        patch_context(context, cfg)

    return context


async def launch_persistent_context_async(
    user_data_dir: str | os.PathLike,
    headless: bool = True,
    proxy: str | ProxySettings | None = None,
    args: List[str] | None = None,
    stealth_args: bool = True,
    user_agent: str | None = None,
    viewport: Dict | None = _VIEWPORT_UNSET,
    locale: str | None = None,
    timezone: str | None = None,
    color_scheme: Literal["light", "dark", "no-preference"] | None = None,
    geoip: bool = False,
    backend: str | None = None,
    humanize: bool = False,
    human_preset: str = "default",
    human_config: Dict[str, Any] | None = None,
    extension_paths: List[str] | None = None,
    privacy_level: PrivacyLevel = PrivacyLevel.STANDARD,
    **kwargs: Any,
) -> Any:
    """Async version of launch_persistent_context()."""
    async_playwright = _import_async_playwright(_resolve_backend(backend))
    timezone = _resolve_timezone(timezone, kwargs)

    binary_path = ensure_binary()
    timezone, locale, exit_ip = maybe_resolve_geoip(geoip, proxy, timezone, locale)
    proxy_kwargs, proxy_extra_args = _resolve_proxy_config(proxy)
    args = _resolve_webrtc_args(args, proxy)
    
    if exit_ip and not (args and any(a.startswith("--fingerprint-webrtc-ip") for a in args)):
        args = list(args or [])
        args.append(f"--fingerprint-webrtc-ip={exit_ip}")

    chrome_args = build_args(
        stealth_args,
        (args or []) + proxy_extra_args,
        timezone=timezone,
        locale=locale,
        headless=headless,
        extension_paths=extension_paths,
        privacy_level=privacy_level,
    )

    context_kwargs: Dict[str, Any] = {}
    if user_agent:
        context_kwargs["user_agent"] = user_agent
    if viewport is _VIEWPORT_UNSET:
        context_kwargs["viewport"] = DEFAULT_VIEWPORT
    elif viewport is None:
        context_kwargs["no_viewport"] = True
    else:
        context_kwargs["viewport"] = viewport
    if color_scheme:
        context_kwargs["color_scheme"] = color_scheme
    context_kwargs.update(kwargs)

    pw = await async_playwright().start()
    context = await pw.chromium.launch_persistent_context(
        user_data_dir=os.fspath(user_data_dir),
        executable_path=binary_path,
        headless=headless,
        args=chrome_args,
        ignore_default_args=IGNORE_DEFAULT_ARGS,
        **proxy_kwargs,
        **context_kwargs,
    )

    _original_close = context.close

    async def _close_with_cleanup() -> None:
        try:
            await _original_close()
        finally:
            await pw.stop()

    context.close = _close_with_cleanup

    if humanize:
        from .human import patch_context_async
        from .human.config import resolve_config
        cfg = resolve_config(human_preset, human_config)
        patch_context_async(context, cfg)

    return context


def launch_context(
    headless: bool = True,
    proxy: str | ProxySettings | None = None,
    args: List[str] | None = None,
    stealth_args: bool = True,
    user_agent: str | None = None,
    viewport: Dict | None = _VIEWPORT_UNSET,
    locale: str | None = None,
    timezone: str | None = None,
    color_scheme: Literal["light", "dark", "no-preference"] | None = None,
    geoip: bool = False,
    backend: str | None = None,
    humanize: bool = False,
    human_preset: str = "default",
    human_config: Dict[str, Any] | None = None,
    extension_paths: List[str] | None = None,
    privacy_level: PrivacyLevel = PrivacyLevel.STANDARD,
    **kwargs: Any,
) -> Any:
    """Launch Soul Browser and return a BrowserContext."""
    timezone = _resolve_timezone(timezone, kwargs)
    timezone, locale, exit_ip = maybe_resolve_geoip(geoip, proxy, timezone, locale)
    
    if exit_ip and not (args and any(a.startswith("--fingerprint-webrtc-ip") for a in args)):
        args = list(args or [])
        args.append(f"--fingerprint-webrtc-ip={exit_ip}")

    browser = launch(
        headless=headless,
        proxy=proxy,
        args=args,
        stealth_args=stealth_args,
        timezone=timezone,
        locale=locale,
        backend=backend,
        extension_paths=extension_paths,
        privacy_level=privacy_level,
    )

    context_kwargs: Dict[str, Any] = {}
    if user_agent:
        context_kwargs["user_agent"] = user_agent
    if viewport is _VIEWPORT_UNSET:
        context_kwargs["viewport"] = DEFAULT_VIEWPORT
    elif viewport is None:
        context_kwargs["no_viewport"] = True
    else:
        context_kwargs["viewport"] = viewport
    if color_scheme:
        context_kwargs["color_scheme"] = color_scheme
    context_kwargs.update(kwargs)

    try:
        context = browser.new_context(**context_kwargs)
    except Exception:
        browser.close()
        raise

    _original_ctx_close = context.close

    def _close_context_with_cleanup() -> None:
        try:
            _original_ctx_close()
        finally:
            browser.close()

    context.close = _close_context_with_cleanup

    if humanize:
        from .human import patch_context
        from .human.config import resolve_config
        cfg = resolve_config(human_preset, human_config)
        patch_context(context, cfg)

    return context


async def launch_context_async(
    headless: bool = True,
    proxy: str | ProxySettings | None = None,
    args: List[str] | None = None,
    stealth_args: bool = True,
    user_agent: str | None = None,
    viewport: Dict | None = _VIEWPORT_UNSET,
    locale: str | None = None,
    timezone: str | None = None,
    color_scheme: Literal["light", "dark", "no-preference"] | None = None,
    geoip: bool = False,
    backend: str | None = None,
    humanize: bool = False,
    human_preset: str = "default",
    human_config: Dict[str, Any] | None = None,
    extension_paths: List[str] | None = None,
    privacy_level: PrivacyLevel = PrivacyLevel.STANDARD,
    **kwargs: Any,
) -> Any:
    """Async version of launch_context()."""
    timezone = _resolve_timezone(timezone, kwargs)
    timezone, locale, exit_ip = maybe_resolve_geoip(geoip, proxy, timezone, locale)
    
    if exit_ip and not (args and any(a.startswith("--fingerprint-webrtc-ip") for a in args)):
        args = list(args or [])
        args.append(f"--fingerprint-webrtc-ip={exit_ip}")

    browser = await launch_async(
        headless=headless,
        proxy=proxy,
        args=args,
        stealth_args=stealth_args,
        timezone=timezone,
        locale=locale,
        backend=backend,
        extension_paths=extension_paths,
        privacy_level=privacy_level,
    )

    context_kwargs: Dict[str, Any] = {}
    if user_agent:
        context_kwargs["user_agent"] = user_agent
    if viewport is _VIEWPORT_UNSET:
        context_kwargs["viewport"] = DEFAULT_VIEWPORT
    elif viewport is None:
        context_kwargs["no_viewport"] = True
    else:
        context_kwargs["viewport"] = viewport
    if color_scheme:
        context_kwargs["color_scheme"] = color_scheme
    context_kwargs.update(kwargs)

    try:
        context = await browser.new_context(**context_kwargs)
    except BaseException:
        try:
            await browser.close()
        except BaseException:
            pass
        raise

    _original_ctx_close = context.close

    async def _close_context_with_cleanup() -> None:
        try:
            await _original_ctx_close()
        finally:
            await browser.close()

    context.close = _close_context_with_cleanup

    if humanize:
        from .human import patch_context_async
        from .human.config import resolve_config
        cfg = resolve_config(human_preset, human_config)
        patch_context_async(context, cfg)

    return context


# Backend resolution
def _resolve_backend(backend: str | None) -> str:
    b = backend or os.environ.get("SOULBROWSER_BACKEND", os.environ.get("CLOAKBROWSER_BACKEND", "playwright"))
    if b not in ("playwright", "patchright"):
        raise ValueError(f"Unknown backend '{b}'. Use 'playwright' or 'patchright'.")
    return b


def _import_sync_playwright(backend: str):
    if backend == "patchright":
        try:
            from patchright.sync_api import sync_playwright
        except ModuleNotFoundError:
            raise ModuleNotFoundError("patchright not installed. Use: pip install soulbrowser[patchright]") from None
        return sync_playwright
    from playwright.sync_api import sync_playwright
    return sync_playwright


def _import_async_playwright(backend: str):
    if backend == "patchright":
        try:
            from patchright.async_api import async_playwright
        except ModuleNotFoundError:
            raise ModuleNotFoundError("patchright not installed. Use: pip install soulbrowser[patchright]") from None
        return async_playwright
    from playwright.async_api import async_playwright
    return async_playwright


# Proxy helpers
def _ensure_proxy_scheme(proxy_url: str) -> str:
    return proxy_url if "://" in proxy_url else f"http://{proxy_url}"


def _is_socks_proxy(proxy: ProxySettings | str) -> bool:
    if isinstance(proxy, dict):
        server = proxy.get("server", "")
        return server.startswith("socks")
    return proxy.startswith("socks")


def _resolve_proxy_config(proxy: str | ProxySettings | None):
    if proxy is None:
        return {}, []
    
    if isinstance(proxy, str):
        proxy = _ensure_proxy_scheme(proxy)
        parsed = urlparse(proxy)
        
        if parsed.username:
            return {
                "proxy": {
                    "server": f"{parsed.scheme}://{parsed.hostname}:{parsed.port}",
                    "username": unquote(parsed.username),
                    "password": unquote(parsed.password or ""),
                }
            }, []
        return {"proxy": {"server": proxy}}, []
    
    return {"proxy": proxy}, []


def _resolve_webrtc_args(args: List[str] | None, proxy: str | ProxySettings | None) -> List[str] | None:
    if not proxy:
        return args
    args = list(args or [])
    if not any("--webrtc-ip-handling-policy" in a for a in args):
        args.append("--webrtc-ip-handling-policy=disable_non_proxied_udp")
    return args


def maybe_resolve_geoip(
    geoip: bool,
    proxy: str | ProxySettings | None,
    timezone: str | None,
    locale: str | None,
) -> tuple:
    if not geoip or not proxy:
        return timezone, locale, None
    
    try:
        from .geoip import resolve_proxy_geo_with_ip
        proxy_url = proxy if isinstance(proxy, str) else proxy.get("server", "")
        if proxy_url:
            proxy_url = _ensure_proxy_scheme(proxy_url)
            geo_tz, geo_locale, exit_ip = resolve_proxy_geo_with_ip(proxy_url)
            return timezone or geo_tz, locale or geo_locale, exit_ip
    except Exception:
        pass
    
    return timezone, locale, None


def build_args(
    stealth_args: bool,
    extra_args: List[str],
    timezone: str | None = None,
    locale: str | None = None,
    headless: bool = True,
    extension_paths: List[str] | None = None,
    privacy_level: PrivacyLevel = PrivacyLevel.STANDARD,
    performance_mode: bool = True,
) -> List[str]:
    """Build Chrome command-line arguments."""
    args = []
    
    if stealth_args:
        args.extend(get_default_stealth_args(privacy_level))
    
    if privacy_level in (PrivacyLevel.STRICT, PrivacyLevel.PARANOID):
        args.extend(get_advanced_stealth_args())
    
    if performance_mode:
        from .performance.optimizer import PerformanceOptimizer
        optimizer = PerformanceOptimizer()
        args.extend(optimizer.get_optimization_args())
    
    if timezone:
        args.append(f"--fingerprint-timezone={timezone}")
    
    if locale:
        args.append(f"--lang={locale}")
    
    if extension_paths:
        paths = ",".join(extension_paths)
        args.append(f"--load-extension={paths}")
        args.append(f"--disable-extensions-except={paths}")
    
    args.extend(extra_args)
    
    return args
