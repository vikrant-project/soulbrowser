"""Soul Browser - Binary download and cache management.

Downloads the patched Chromium binary on first use, caches it locally.
"""

from __future__ import annotations

import hashlib
import logging
import os
import platform
import stat
import subprocess
import sys
import tarfile
import tempfile
import threading
import time
from pathlib import Path

import httpx

from ._version import __version__ as _wrapper_version
from .config import (
    CHROMIUM_VERSION,
    DOWNLOAD_BASE_URL,
    GITHUB_API_URL,
    GITHUB_DOWNLOAD_BASE_URL,
    _version_newer,
    check_platform_available,
    get_archive_ext,
    get_archive_name,
    get_binary_dir,
    get_binary_path,
    get_cache_dir,
    get_chromium_version,
    get_download_url,
    get_effective_version,
    get_fallback_download_url,
    get_local_binary_override,
    get_platform_tag,
)

logger = logging.getLogger("soulbrowser")

DOWNLOAD_TIMEOUT = httpx.Timeout(connect=10.0, read=60.0, write=10.0, pool=10.0)
UPDATE_CHECK_INTERVAL = 3600


def _show_welcome() -> None:
    """Show welcome message on first launch."""
    marker = get_cache_dir() / ".welcome_shown"
    if marker.exists():
        return
    
    sys.stderr.write("\n")
    sys.stderr.write("  ╔═══════════════════════════════════════════════════════════╗\n")
    sys.stderr.write("  ║                     SOUL BROWSER v1.0                     ║\n")
    sys.stderr.write("  ║          The Ultimate Privacy-First Stealth Browser      ║\n")
    sys.stderr.write("  ╠═══════════════════════════════════════════════════════════╣\n")
    sys.stderr.write("  ║  ✓ Advanced fingerprint protection                        ║\n")
    sys.stderr.write("  ║  ✓ ML-based tracking prevention                           ║\n")
    sys.stderr.write("  ║  ✓ Built-in ad blocker                                    ║\n")
    sys.stderr.write("  ║  ✓ WebRTC leak protection                                 ║\n")
    sys.stderr.write("  ║  ✓ DNS-over-HTTPS encryption                              ║\n")
    sys.stderr.write("  ║  ✓ Performance optimization                               ║\n")
    sys.stderr.write("  ╠═══════════════════════════════════════════════════════════╣\n")
    sys.stderr.write("  ║  GitHub: https://github.com/vikrant-project/soulbrowser   ║\n")
    sys.stderr.write("  ╚═══════════════════════════════════════════════════════════╝\n")
    sys.stderr.write("\n")
    
    try:
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text("")
    except OSError:
        pass


def ensure_binary() -> str:
    """Ensure the stealth Chromium binary is available."""
    local_override = get_local_binary_override()
    if local_override:
        path = Path(local_override)
        if not path.exists():
            raise FileNotFoundError(
                f"SOULBROWSER_BINARY_PATH set to '{local_override}' but file does not exist"
            )
        logger.info("Using local binary override: %s", local_override)
        return str(path)

    check_platform_available()

    effective = get_effective_version()
    binary_path = get_binary_path(effective)

    if binary_path.exists() and _is_executable(binary_path):
        logger.debug("Binary found in cache: %s (version %s)", binary_path, effective)
        _show_welcome()
        _maybe_trigger_update_check()
        return str(binary_path)

    platform_version = get_chromium_version()
    if effective != platform_version:
        fallback_path = get_binary_path()
        if fallback_path.exists() and _is_executable(fallback_path):
            logger.debug("Binary found in cache: %s", fallback_path)
            _maybe_trigger_update_check()
            return str(fallback_path)

    logger.info(
        "Soul Browser Chromium %s not found. Downloading for %s...",
        platform_version,
        get_platform_tag(),
    )
    _download_and_extract()

    binary_path = get_binary_path()
    if not binary_path.exists():
        raise RuntimeError(
            f"Download completed but binary not found at expected path: {binary_path}"
        )

    _maybe_trigger_update_check()
    return str(binary_path)


def _download_and_extract(version: str | None = None) -> None:
    """Download the binary archive and extract to cache directory."""
    primary_url = get_download_url(version)
    fallback_url = get_fallback_download_url(version)
    binary_dir = get_binary_dir(version)
    binary_path = get_binary_path(version)

    binary_dir.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(suffix=get_archive_ext(), delete=False) as tmp:
        tmp_path = Path(tmp.name)

    try:
        try:
            _download_file(primary_url, tmp_path)
        except Exception as primary_err:
            if os.environ.get("SOULBROWSER_DOWNLOAD_URL") or os.environ.get("CLOAKBROWSER_DOWNLOAD_URL"):
                raise
            logger.warning("Primary download failed (%s), trying GitHub Releases...", primary_err)
            _download_file(fallback_url, tmp_path)

        if os.environ.get("SOULBROWSER_SKIP_CHECKSUM", "").lower() != "true":
            _verify_download_checksum(tmp_path, version)

        _extract_archive(tmp_path, binary_dir, binary_path)
        _show_welcome()
    finally:
        tmp_path.unlink(missing_ok=True)


def _verify_download_checksum(file_path: Path, version: str | None = None) -> None:
    """Verify SHA256 checksum."""
    checksums = _fetch_checksums(version)
    tarball_name = get_archive_name()

    if checksums is None:
        logger.warning("SHA256SUMS not available — skipping checksum verification")
        return

    expected = checksums.get(tarball_name)
    if expected is None:
        logger.warning("No checksum entry for %s — skipping verification", tarball_name)
        return

    _verify_checksum(file_path, expected)


def _fetch_checksums(version: str | None = None) -> dict | None:
    """Fetch SHA256SUMS file."""
    v = version or get_chromium_version()
    has_custom_url = os.environ.get("SOULBROWSER_DOWNLOAD_URL") or os.environ.get("CLOAKBROWSER_DOWNLOAD_URL")

    urls = [f"{DOWNLOAD_BASE_URL}/chromium-v{v}/SHA256SUMS"]
    if not has_custom_url:
        urls.append(f"{GITHUB_DOWNLOAD_BASE_URL}/chromium-v{v}/SHA256SUMS")

    for url in urls:
        try:
            resp = httpx.get(url, follow_redirects=True, timeout=10.0)
            resp.raise_for_status()
            return _parse_checksums(resp.text)
        except Exception:
            continue
    return None


def _parse_checksums(text: str) -> dict:
    """Parse SHA256SUMS format."""
    result = {}
    for line in text.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split(None, 1)
        if len(parts) == 2:
            hash_val, filename = parts
            filename = filename.lstrip("*")
            result[filename] = hash_val.lower()
    return result


def _verify_checksum(file_path: Path, expected_hash: str) -> None:
    """Verify SHA-256 of a file."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    actual = sha256.hexdigest().lower()
    if actual != expected_hash:
        raise RuntimeError(f"Checksum verification failed! Expected: {expected_hash}, Got: {actual}")
    logger.info("Checksum verified: SHA-256 OK")


def _download_file(url: str, dest: Path) -> None:
    """Download a file with progress logging."""
    logger.info("Downloading from %s", url)

    with httpx.stream("GET", url, follow_redirects=True, timeout=DOWNLOAD_TIMEOUT) as response:
        response.raise_for_status()

        total = int(response.headers.get("content-length", 0))
        downloaded = 0
        last_logged_pct = -1

        with open(dest, "wb") as f:
            for chunk in response.iter_bytes(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)

                if total > 0:
                    pct = int(downloaded / total * 100)
                    if pct >= last_logged_pct + 10:
                        last_logged_pct = pct
                        logger.info("Download progress: %d%% (%d/%d MB)", pct, downloaded // (1024 * 1024), total // (1024 * 1024))

    logger.info("Download complete: %d MB", dest.stat().st_size // (1024 * 1024))


def _extract_archive(archive_path: Path, dest_dir: Path, binary_path: Path | None = None) -> None:
    """Extract archive to destination directory."""
    logger.info("Extracting to %s", dest_dir)

    if dest_dir.exists():
        import shutil
        shutil.rmtree(dest_dir)

    dest_dir.mkdir(parents=True, exist_ok=True)

    if str(archive_path).endswith(".zip"):
        _extract_zip(archive_path, dest_dir)
    else:
        _extract_tar(archive_path, dest_dir)

    _flatten_single_subdir(dest_dir)

    bp = binary_path or get_binary_path()
    if bp.exists():
        _make_executable(bp)

    if platform.system() == "Darwin":
        _remove_quarantine(dest_dir)

    if bp.exists():
        logger.info("Binary ready: %s", bp)


def _extract_tar(archive_path: Path, dest_dir: Path) -> None:
    """Extract tar.gz archive."""
    with tarfile.open(archive_path, "r:gz") as tar:
        safe_members = []
        for member in tar.getmembers():
            if member.issym() or member.islnk():
                link_target = member.linkname
                if os.path.isabs(link_target) or ".." in link_target.split("/"):
                    logger.warning("Skipping suspicious symlink: %s -> %s", member.name, link_target)
                    continue
            else:
                member_path = (dest_dir / member.name).resolve()
                if not str(member_path).startswith(str(dest_dir.resolve())):
                    raise RuntimeError(f"Archive contains path traversal: {member.name}")
            safe_members.append(member)

        tar.extractall(dest_dir, members=safe_members)


def _extract_zip(archive_path: Path, dest_dir: Path) -> None:
    """Extract zip archive."""
    import zipfile

    with zipfile.ZipFile(archive_path, "r") as zf:
        for info in zf.infolist():
            member_path = (dest_dir / info.filename).resolve()
            if not str(member_path).startswith(str(dest_dir.resolve())):
                raise RuntimeError(f"Archive contains path traversal: {info.filename}")
        zf.extractall(dest_dir)


def _flatten_single_subdir(dest_dir: Path) -> None:
    """Flatten single subdirectory."""
    import shutil

    entries = list(dest_dir.iterdir())
    if len(entries) == 1 and entries[0].is_dir():
        subdir = entries[0]
        if subdir.name.endswith(".app"):
            logger.debug("Keeping .app bundle intact: %s", subdir.name)
            return
        logger.debug("Flattening single subdirectory: %s", subdir.name)
        for item in subdir.iterdir():
            shutil.move(str(item), str(dest_dir / item.name))
        subdir.rmdir()


def _is_executable(path: Path) -> bool:
    return os.access(path, os.X_OK)


def _make_executable(path: Path) -> None:
    if platform.system() == "Windows":
        return
    current = path.stat().st_mode
    path.chmod(current | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def _remove_quarantine(path: Path) -> None:
    try:
        subprocess.run(["xattr", "-cr", str(path)], capture_output=True, timeout=30)
        logger.debug("Removed quarantine attributes from %s", path)
    except Exception:
        logger.debug("Failed to remove quarantine attributes", exc_info=True)


def clear_cache() -> None:
    """Remove all cached binaries."""
    import shutil
    cache_dir = get_cache_dir()
    if cache_dir.exists():
        shutil.rmtree(cache_dir)
        logger.info("Cache cleared: %s", cache_dir)


def binary_info() -> dict:
    """Return info about the current binary installation."""
    effective = get_effective_version()
    binary_path = get_binary_path(effective)
    return {
        "soul_browser_version": "1.0.0",
        "chromium_version": effective,
        "bundled_version": CHROMIUM_VERSION,
        "platform": get_platform_tag(),
        "binary_path": str(binary_path),
        "installed": binary_path.exists(),
        "cache_dir": str(get_binary_dir(effective)),
        "download_url": get_download_url(effective),
    }


def check_for_update() -> str | None:
    """Check for a newer Chromium version."""
    latest = _get_latest_chromium_version()
    if latest is None:
        return None
    if not _version_newer(latest, get_chromium_version()):
        return None

    binary_dir = get_binary_dir(latest)
    if binary_dir.exists():
        _write_version_marker(latest)
        return latest

    logger.info("Downloading Chromium %s...", latest)
    _download_and_extract(version=latest)
    _write_version_marker(latest)
    return latest


def _should_check_for_update() -> bool:
    if os.environ.get("SOULBROWSER_AUTO_UPDATE", os.environ.get("CLOAKBROWSER_AUTO_UPDATE", "")).lower() == "false":
        return False
    if get_local_binary_override():
        return False
    if os.environ.get("SOULBROWSER_DOWNLOAD_URL") or os.environ.get("CLOAKBROWSER_DOWNLOAD_URL"):
        return False

    check_file = get_cache_dir() / ".last_update_check"
    if check_file.exists():
        try:
            last_check = float(check_file.read_text().strip())
            if time.time() - last_check < UPDATE_CHECK_INTERVAL:
                return False
        except (ValueError, OSError):
            pass
    return True


def _get_latest_chromium_version() -> str | None:
    try:
        resp = httpx.get(GITHUB_API_URL, params={"per_page": 10}, timeout=10.0)
        resp.raise_for_status()
        platform_tarball = get_archive_name()
        for release in resp.json():
            tag = release.get("tag_name", "")
            if tag.startswith("chromium-v") and not release.get("draft"):
                asset_names = {a["name"] for a in release.get("assets", [])}
                if platform_tarball in asset_names:
                    return tag.removeprefix("chromium-v")
        return None
    except Exception:
        logger.debug("Auto-update check failed", exc_info=True)
        return None


def _write_version_marker(version: str) -> None:
    cache_dir = get_cache_dir()
    cache_dir.mkdir(parents=True, exist_ok=True)
    marker = cache_dir / f"latest_version_{get_platform_tag()}"
    tmp = marker.with_suffix(".tmp")
    tmp.write_text(version)
    tmp.rename(marker)


_wrapper_update_checked = False


def _check_wrapper_update() -> None:
    global _wrapper_update_checked
    if _wrapper_update_checked:
        return
    _wrapper_update_checked = True
    if os.environ.get("SOULBROWSER_AUTO_UPDATE", os.environ.get("CLOAKBROWSER_AUTO_UPDATE", "")).lower() == "false":
        return
    if os.environ.get("SOULBROWSER_DOWNLOAD_URL") or os.environ.get("CLOAKBROWSER_DOWNLOAD_URL"):
        return
    try:
        resp = httpx.get("https://pypi.org/pypi/soulbrowser/json", timeout=5.0)
        resp.raise_for_status()
        latest = resp.json()["info"]["version"]
        if _version_newer(latest, _wrapper_version):
            logger.warning("Update available: soulbrowser %s → %s. Run: pip install --upgrade soulbrowser", _wrapper_version, latest)
    except Exception:
        logger.debug("Wrapper update check failed", exc_info=True)


def _check_and_download_update() -> None:
    try:
        check_file = get_cache_dir() / ".last_update_check"
        check_file.parent.mkdir(parents=True, exist_ok=True)
        check_file.write_text(str(time.time()))

        platform_version = get_chromium_version()
        latest = _get_latest_chromium_version()
        if latest is None:
            return
        if not _version_newer(latest, platform_version):
            return

        if get_binary_dir(latest).exists():
            _write_version_marker(latest)
            return

        logger.info("Newer Chromium available: %s (current: %s). Downloading in background...", latest, platform_version)
        _download_and_extract(version=latest)
        _write_version_marker(latest)
        logger.info("Background update complete: Chromium %s ready. Will use on next launch.", latest)
    except Exception:
        logger.debug("Background update failed", exc_info=True)


def _maybe_trigger_update_check() -> None:
    if not _wrapper_update_checked:
        t = threading.Thread(target=_check_wrapper_update, daemon=True)
        t.start()

    if not _should_check_for_update():
        return
    t = threading.Thread(target=_check_and_download_update, daemon=True)
    t.start()
